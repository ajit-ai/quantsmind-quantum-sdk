// QuantsMind Database Engine - Library Interface
//
// This file exposes the database engine as a library for use in Tauri Studio

pub mod storage;
pub mod index;
pub mod concurrency;
pub mod catalog;
pub mod execution;
pub mod server;

// Re-export key types and components for easier access
pub use storage::{DiskManager, BufferPoolManager, Page, PageId, PAGE_SIZE};
pub use catalog::{Catalog, TableMetadata, ColumnMetadata};
pub use execution::{SQLParser, QueryPlanner, ExecutorBuilder};
pub use execution::types::{DataType, Schema, Value, Tuple};
pub use concurrency::{WALManager, WALRecord, WALRecordType, LockManager};

use std::sync::Arc;
use tokio::sync::RwLock;
use thiserror::Error;

/// Error type for engine operations
#[derive(Error, Debug)]
pub enum EngineError {
    #[error("Storage error: {0}")]
    Storage(String),
    
    #[error("Execution error: {0}")]
    Execution(String),
    
    #[error("Transaction error: {0}")]
    Transaction(String),
    
    #[error("Parser error: {0}")]
    Parser(String),
}

/// Result type for engine operations
pub type Result<T> = std::result::Result<T, EngineError>;

/// QuantsMind Database Engine - Main entry point for library usage
pub struct QuantsMindEngine {
    disk_manager: Arc<DiskManager>,
    buffer_pool: Arc<RwLock<BufferPoolManager>>,
    catalog: Arc<Catalog>,
    wal: Arc<WALManager>,
    lock_manager: Arc<LockManager>,
}

impl QuantsMindEngine {
    /// Create a new QuantsMind engine instance
    pub fn new(db_path: &str) -> Result<Self> {
        let disk_manager = Arc::new(DiskManager::new(db_path)
            .map_err(|e| EngineError::Storage(e.to_string()))?);
        
        let buffer_pool = Arc::new(RwLock::new(
            BufferPoolManager::with_default_size(disk_manager.clone())
        ));
        
        let catalog = Arc::new(Catalog::new());
        catalog.initialize_default_schema()
            .map_err(|e| EngineError::Storage(e.to_string()))?;
        
        let wal = Arc::new(WALManager::with_default_size(format!("{}/wal.log", db_path))
            .map_err(|e| EngineError::Storage(e.to_string()))?);
        
        let lock_manager = Arc::new(LockManager::new());
        
        Ok(QuantsMindEngine {
            disk_manager,
            buffer_pool,
            catalog,
            wal,
            lock_manager,
        })
    }
    
    /// Execute a SQL query and return results
    pub fn execute_sql(&self, sql: &str) -> Result<QueryResult> {
        let start = std::time::Instant::now();
        
        // Parse the SQL
        let parse_result = SQLParser::parse(sql)
            .map_err(|e| EngineError::Parser(e.to_string()))?;
        
        // Convert to logical plan
        let logical_plan = QueryPlanner::ast_to_logical(&parse_result.ast)
            .map_err(|e| EngineError::Execution(e.to_string()))?;
        
        // Convert to physical plan
        let physical_plan = QueryPlanner::logical_to_physical(&logical_plan)
            .map_err(|e| EngineError::Execution(e.to_string()))?;
        
        // Build executor
        let mut executor = ExecutorBuilder::build(physical_plan)
            .map_err(|e| EngineError::Execution(e.to_string()))?;
        
        // Execute query
        executor.open()
            .map_err(|e| EngineError::Execution(e.to_string()))?;
        
        let mut rows = Vec::new();
        let mut columns = Vec::new();
        
        // Get column names from schema
        if let Some(tuple) = executor.next().map_err(|e| EngineError::Execution(e.to_string()))? {
            let schema = executor.schema();
            columns = schema.columns().iter().cloned().collect();
            rows.push(tuple.values().iter().map(|v| v.to_string()).collect());
            
            // Get remaining rows
            while let Some(tuple) = executor.next().map_err(|e| EngineError::Execution(e.to_string()))? {
                rows.push(tuple.values().iter().map(|v| v.to_string()).collect());
            }
        }
        
        executor.close()
            .map_err(|e| EngineError::Execution(e.to_string()))?;
        
        let execution_time_ms = start.elapsed().as_millis() as u64;
        
        Ok(QueryResult {
            success: true,
            message: "Query executed successfully".to_string(),
            rows,
            columns,
            execution_time_ms,
        })
    }
    
    /// Get list of tables in the database
    pub fn list_tables(&self) -> Result<Vec<String>> {
        Ok(self.catalog.list_tables())
    }
    
    /// Get schema for a specific table
    pub fn get_table_schema(&self, table_name: &str) -> Result<Vec<ColumnDefinition>> {
        let schema = self.catalog.get_table_schema(table_name)
            .ok_or_else(|| EngineError::Execution(format!("Table '{}' not found", table_name)))?;
        
        let mut columns = Vec::new();
        for (i, col_name) in schema.columns().iter().enumerate() {
            let col_type = schema.get_column_type(i)
                .ok_or_else(|| EngineError::Execution("Invalid schema".to_string()))?;
            let nullable = schema.is_nullable(i)
                .ok_or_else(|| EngineError::Execution("Invalid schema".to_string()))?;
            
            columns.push(ColumnDefinition {
                name: col_name.clone(),
                data_type: col_type.name().to_string(),
                nullable: *nullable,
                primary_key: false, // TODO: Get from catalog
            });
        }
        
        Ok(columns)
    }
    
    /// Shut down the engine and flush data to disk
    pub fn shutdown(&self) -> Result<()> {
        self.disk_manager.flush()
            .map_err(|e| EngineError::Storage(e.to_string()))?;
        self.wal.flush()
            .map_err(|e| EngineError::Storage(e.to_string()))?;
        Ok(())
    }
}

/// Query result structure
#[derive(Debug, Clone)]
pub struct QueryResult {
    pub success: bool,
    pub message: String,
    pub rows: Vec<Vec<String>>,
    pub columns: Vec<String>,
    pub execution_time_ms: u64,
}

/// Column definition for schema queries
#[derive(Debug, Clone)]
pub struct ColumnDefinition {
    pub name: String,
    pub data_type: String,
    pub nullable: bool,
    pub primary_key: bool,
}