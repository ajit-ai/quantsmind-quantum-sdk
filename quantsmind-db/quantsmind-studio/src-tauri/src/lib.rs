// Tauri IPC Commands for QuantsMind Studio
// 
// This file provides the interface between the React frontend and the Rust backend.
// Commands are invoked from the frontend using Tauri's invoke() function.

use tauri::State;
use serde::{Deserialize, Serialize};
use std::sync::Mutex;
use quantsmind_engine::{QuantsMindEngine, ColumnDefinition, QueryResult as EngineQueryResult};

/// Database state holding the engine instance
struct DatabaseState {
    engine: Mutex<Option<QuantsMindEngine>>,
    connection_string: Mutex<String>,
}

impl DatabaseState {
    fn new() -> Self {
        DatabaseState {
            engine: Mutex::new(None),
            connection_string: Mutex::new(String::new()),
        }
    }
}

/// Query request from frontend
#[derive(Debug, Serialize, Deserialize)]
pub struct QueryRequest {
    pub sql: String,
}

/// Query response to frontend
#[derive(Debug, Serialize, Deserialize)]
pub struct QueryResponse {
    pub success: bool,
    pub message: String,
    pub rows: Vec<Vec<String>>,
    pub columns: Vec<String>,
    pub execution_time_ms: u64,
}

/// Table schema request
#[derive(Debug, Serialize, Deserialize)]
pub struct TableSchemaRequest {
    pub table_name: String,
}

/// Column definition
#[derive(Debug, Serialize, Deserialize)]
pub struct ColumnDefinition {
    pub name: String,
    pub data_type: String,
    pub nullable: bool,
    pub primary_key: bool,
}

/// Execute a SQL query
#[tauri::command]
async fn execute_query(
    request: QueryRequest,
    state: State<'_, DatabaseState>,
) -> Result<QueryResponse, String> {
    let start = std::time::Instant::now();
    
    // Check if connected
    let engine_guard = state.engine.lock().unwrap();
    let engine = engine_guard.as_ref()
        .ok_or_else(|| "Not connected to database".to_string())?;
    
    // Execute query using the real engine
    let result = engine.execute_sql(&request.sql)
        .map_err(|e| format!("Query execution error: {}", e))?;
    
    Ok(QueryResponse {
        success: result.success,
        message: result.message,
        rows: result.rows,
        columns: result.columns,
        execution_time_ms: result.execution_time_ms,
    })
}

/// Connect to database
#[tauri::command]
async fn connect_database(
    connection_string: String,
    state: State<'_, DatabaseState>,
) -> Result<bool, String> {
    // Store connection string
    *state.connection_string.lock().unwrap() = connection_string.clone();
    
    // Create the real engine instance
    let engine = QuantsMindEngine::new(&connection_string)
        .map_err(|e| format!("Failed to initialize engine: {}", e))?;
    
    // Store the engine in state
    *state.engine.lock().unwrap() = Some(engine);
    
    Ok(true)
}

/// Disconnect from database
#[tauri::command]
async fn disconnect_database(state: State<'_, DatabaseState>) -> Result<bool, String> {
    // Shutdown the engine if it exists
    let mut engine_guard = state.engine.lock().unwrap();
    if let Some(engine) = engine_guard.take() {
        engine.shutdown()
            .map_err(|e| format!("Failed to shutdown engine: {}", e))?;
    }
    
    *state.connection_string.lock().unwrap() = String::new();
    
    Ok(true)
}

/// Get list of tables
#[tauri::command]
async fn list_tables(state: State<'_, DatabaseState>) -> Result<Vec<String>, String> {
    let engine_guard = state.engine.lock().unwrap();
    let engine = engine_guard.as_ref()
        .ok_or_else(|| "Not connected to database".to_string())?;
    
    engine.list_tables()
        .map_err(|e| format!("Failed to list tables: {}", e))
}

/// Get table schema
#[tauri::command]
async fn get_table_schema(
    request: TableSchemaRequest,
    state: State<'_, DatabaseState>,
) -> Result<Vec<ColumnDefinition>, String> {
    let engine_guard = state.engine.lock().unwrap();
    let engine = engine_guard.as_ref()
        .ok_or_else(|| "Not connected to database".to_string())?;
    
    let engine_columns = engine.get_table_schema(&request.table_name)
        .map_err(|e| format!("Failed to get table schema: {}", e))?;
    
    // Convert engine column definitions to Tauri column definitions
    let schema = engine_columns.into_iter().map(|col| ColumnDefinition {
        name: col.name,
        data_type: col.data_type,
        nullable: col.nullable,
        primary_key: col.primary_key,
    }).collect();
    
    Ok(schema)
}

/// Execute DDL statement (CREATE TABLE, etc.)
#[tauri::command]
async fn execute_ddl(
    sql: String,
    state: State<'_, DatabaseState>,
) -> Result<bool, String> {
    let engine_guard = state.engine.lock().unwrap();
    let engine = engine_guard.as_ref()
        .ok_or_else(|| "Not connected to database".to_string())?;
    
    // Execute DDL using the real engine
    engine.execute_sql(&sql)
        .map_err(|e| format!("DDL execution error: {}", e))?;
    
    Ok(true)
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(DatabaseState::new())
        .invoke_handler(tauri::generate_handler![
            execute_query,
            connect_database,
            disconnect_database,
            list_tables,
            get_table_schema,
            execute_ddl,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
