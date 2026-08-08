use std::sync::Arc;
use tonic::Status;
use serde::{Serialize, Deserialize};
use crate::storage::{DiskManager, BufferPoolManager};
use crate::catalog::Catalog;
use crate::execution::{SQLParser, QueryPlanner, DataType};
use crate::execution::volcano::ExecutorBuilder;

/// Query request from client
#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct QueryRequest {
    pub sql: String,
}

/// Query response to client
#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct QueryResponse {
    pub success: bool,
    pub message: String,
    pub rows: Vec<Vec<String>>,
    pub columns: Vec<String>,
    pub execution_time_ms: u64,
}

/// Table creation request
#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct CreateTableRequest {
    pub table_name: String,
    pub columns: Vec<ColumnDefinition>,
}

/// Column definition
#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct ColumnDefinition {
    pub name: String,
    pub data_type: String,
    pub nullable: bool,
    pub primary_key: bool,
}

/// Simple response
#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct SimpleResponse {
    pub success: bool,
    pub message: String,
}

/// QuantsMind Database Server
/// 
/// Provides API endpoints for:
/// - SQL query execution
/// - Table management
/// - Schema information
#[allow(dead_code)]
pub struct QuantsMindServer {
    catalog: Arc<Catalog>,
    disk_manager: Arc<DiskManager>,
    buffer_pool: Arc<tokio::sync::RwLock<BufferPoolManager>>,
}

#[allow(dead_code)]
impl QuantsMindServer {
    /// Create a new server instance
    pub fn new(
        catalog: Arc<Catalog>,
        disk_manager: Arc<DiskManager>,
        buffer_pool: Arc<tokio::sync::RwLock<BufferPoolManager>>,
    ) -> Self {
        QuantsMindServer {
            catalog,
            disk_manager,
            buffer_pool,
        }
    }
    
    /// Execute a SQL query
    #[allow(dead_code)]
    pub async fn execute_query(&self, request: QueryRequest) -> Result<QueryResponse, Status> {
        let start = std::time::Instant::now();
        
        // Parse the SQL
        let parse_result = SQLParser::parse(&request.sql)
            .map_err(|e| Status::invalid_argument(format!("Parse error: {}", e)))?;
        
        // Convert to logical plan
        let logical_plan = QueryPlanner::ast_to_logical(&parse_result.ast)
            .map_err(|e| Status::internal(format!("Planning error: {}", e)))?;
        
        // Convert to physical plan
        let physical_plan = QueryPlanner::logical_to_physical(&logical_plan)
            .map_err(|e| Status::internal(format!("Physical planning error: {}", e)))?;
        
        // Build executor
        let mut executor = ExecutorBuilder::build(physical_plan)
            .map_err(|e| Status::internal(format!("Executor build error: {}", e)))?;
        
        // Execute query
        executor.open()
            .map_err(|e| Status::internal(format!("Executor open error: {}", e)))?;
        
        let mut rows = Vec::new();
        let columns = executor.schema().columns().to_vec();
        
        while let Some(tuple) = executor.next()
            .map_err(|e| Status::internal(format!("Executor next error: {}", e)))? 
        {
            let row: Vec<String> = tuple.values().iter().map(|v| v.to_string()).collect();
            rows.push(row);
        }
        
        executor.close()
            .map_err(|e| Status::internal(format!("Executor close error: {}", e)))?;
        
        let execution_time = start.elapsed().as_millis() as u64;
        
        Ok(QueryResponse {
            success: true,
            message: format!("Query executed successfully, {} rows returned", rows.len()),
            rows,
            columns,
            execution_time_ms: execution_time,
        })
    }
    
    /// Create a new table
    #[allow(dead_code)]
    pub async fn create_table(&self, request: CreateTableRequest) -> Result<SimpleResponse, Status> {
        use crate::catalog::{TableMetadata, ColumnMetadata};
        
        let mut table = TableMetadata::new(request.table_name.clone());
        let mut primary_keys = Vec::new();
        
        for (i, col_def) in request.columns.iter().enumerate() {
            let data_type = Self::parse_data_type(&col_def.data_type)
                .map_err(|e| Status::invalid_argument(format!("Invalid data type: {}", e)))?;
            
            let mut col = ColumnMetadata::new(col_def.name.clone(), data_type, col_def.nullable, i);
            col.is_primary_key = col_def.primary_key;
            
            if col_def.primary_key {
                primary_keys.push(col_def.name.clone());
            }
            
            table.add_column(col);
        }
        
        table.primary_key = primary_keys;
        
        self.catalog.create_table(table)
            .map_err(|e| Status::internal(format!("Failed to create table: {}", e)))?;
        
        Ok(SimpleResponse {
            success: true,
            message: format!("Table {} created successfully", request.table_name),
        })
    }
    
    /// Drop a table
    #[allow(dead_code)]
    pub async fn drop_table(&self, table_name: String) -> Result<SimpleResponse, Status> {
        self.catalog.drop_table(&table_name)
            .map_err(|e| Status::internal(format!("Failed to drop table: {}", e)))?;
        
        Ok(SimpleResponse {
            success: true,
            message: format!("Table {} dropped successfully", table_name),
        })
    }
    
    /// List all tables
    #[allow(dead_code)]
    pub async fn list_tables(&self) -> Result<Vec<String>, Status> {
        Ok(self.catalog.list_tables())
    }
    
    /// Get table schema
    #[allow(dead_code)]
    pub async fn get_table_schema(&self, table_name: String) -> Result<Vec<ColumnDefinition>, Status> {
        let table = self.catalog.get_table(&table_name)
            .ok_or_else(|| Status::not_found(format!("Table {} not found", table_name)))?;
        
        let columns = table.columns.into_iter().map(|col| ColumnDefinition {
            name: col.name,
            data_type: col.data_type.name().to_string(),
            nullable: col.nullable,
            primary_key: col.is_primary_key,
        }).collect();
        
        Ok(columns)
    }
    
    /// Parse data type string to DataType enum
    #[allow(dead_code)]
    fn parse_data_type(type_str: &str) -> Result<DataType, String> {
        match type_str.to_uppercase().as_str() {
            "UUID" => Ok(DataType::UUID),
            "VARCHAR" | "TEXT" => Ok(DataType::Varchar(255)),
            "INT" | "INTEGER" => Ok(DataType::Int),
            "FLOAT" | "DOUBLE" => Ok(DataType::Float),
            "BOOLEAN" | "BOOL" => Ok(DataType::Boolean),
            "TIMESTAMP" => Ok(DataType::Timestamp),
            "NUMERIC" | "DECIMAL" => Ok(DataType::Numeric(38, 10)),
            _ => Err(format!("Unknown data type: {}", type_str)),
        }
    }
}

/// Start the QuantsMind server
#[allow(dead_code)]
pub async fn start_server(
    catalog: Arc<Catalog>,
    disk_manager: Arc<DiskManager>,
    buffer_pool: Arc<tokio::sync::RwLock<BufferPoolManager>>,
    address: String,
) -> Result<(), Box<dyn std::error::Error>> {
    let _server = QuantsMindServer::new(catalog, disk_manager, buffer_pool);
    
    // In a real implementation, this would start a gRPC server
    // For this simplified version, we'll just print a message
    println!("QuantsMind Server listening on {}", address);
    println!("Server initialized and ready to accept connections");
    
    // Keep the server running
    // In production, you'd use: Server::builder().add_service(service).serve(addr).await
    let _ = tokio::signal::ctrl_c().await;
    println!("Server shutdown");
    
    Ok(())
}

#[cfg(test)]
#[allow(dead_code)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[tokio::test]
    async fn test_server_creation() {
        let catalog = Arc::new(Catalog::new());
        let temp_file = NamedTempFile::new().unwrap();
        let disk_manager = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let buffer_pool = Arc::new(tokio::sync::RwLock::new(
            BufferPoolManager::with_default_size(disk_manager.clone())
        ));
        
        let server = QuantsMindServer::new(catalog, disk_manager, buffer_pool);
        assert!(server.list_tables().await.is_ok());
    }

    #[tokio::test]
    async fn test_create_table_via_server() {
        let catalog = Arc::new(Catalog::new());
        let temp_file = NamedTempFile::new().unwrap();
        let disk_manager = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let buffer_pool = Arc::new(tokio::sync::RwLock::new(
            BufferPoolManager::with_default_size(disk_manager.clone())
        ));
        
        let server = QuantsMindServer::new(catalog.clone(), disk_manager, buffer_pool);
        
        let request = CreateTableRequest {
            table_name: "test".to_string(),
            columns: vec![
                ColumnDefinition {
                    name: "id".to_string(),
                    data_type: "INT".to_string(),
                    nullable: false,
                    primary_key: true,
                },
            ],
        };
        
        let response = server.create_table(request).await;
        assert!(response.is_ok());
        assert!(catalog.table_exists("test"));
    }
}
