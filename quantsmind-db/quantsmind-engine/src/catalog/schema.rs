use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use serde::{Serialize, Deserialize};
use crate::execution::types::{Schema, DataType};

/// Column metadata stored in the catalog
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColumnMetadata {
    /// Column name
    pub name: String,
    /// Data type
    pub data_type: DataType,
    /// Whether the column is nullable
    pub nullable: bool,
    /// Default value (as string)
    pub default_value: Option<String>,
    /// Whether the column is part of the primary key
    pub is_primary_key: bool,
    /// Column position in the table
    pub position: usize,
}

impl ColumnMetadata {
    pub fn new(name: String, data_type: DataType, nullable: bool, position: usize) -> Self {
        ColumnMetadata {
            name,
            data_type,
            nullable,
            default_value: None,
            is_primary_key: false,
            position,
        }
    }
}

/// Index metadata stored in the catalog
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IndexMetadata {
    /// Index name
    pub name: String,
    /// Table the index is on
    pub table_name: String,
    /// Columns the index is on
    pub column_names: Vec<String>,
    /// Whether the index is unique
    pub is_unique: bool,
    /// Whether the index is the primary key index
    pub is_primary: bool,
}

impl IndexMetadata {
    #[allow(dead_code)]
    pub fn new(name: String, table_name: String, column_names: Vec<String>, is_unique: bool, is_primary: bool) -> Self {
        IndexMetadata {
            name,
            table_name,
            column_names,
            is_unique,
            is_primary,
        }
    }
}

/// Table metadata stored in the catalog
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TableMetadata {
    /// Table name
    pub name: String,
    /// Column metadata
    pub columns: Vec<ColumnMetadata>,
    /// Primary key columns
    pub primary_key: Vec<String>,
    /// Foreign keys (table, columns, ref_table, ref_columns)
    pub foreign_keys: Vec<(String, Vec<String>, String, Vec<String>)>,
    /// Indexes on this table
    pub indexes: Vec<IndexMetadata>,
    /// Page ID of the first data page
    pub first_page_id: Option<u32>,
}

impl TableMetadata {
    pub fn new(name: String) -> Self {
        TableMetadata {
            name,
            columns: Vec::new(),
            primary_key: Vec::new(),
            foreign_keys: Vec::new(),
            indexes: Vec::new(),
            first_page_id: None,
        }
    }
    
    /// Add a column to the table metadata
    pub fn add_column(&mut self, column: ColumnMetadata) {
        self.columns.push(column);
    }
    
    /// Get a column by name
    #[allow(dead_code)]
    pub fn get_column(&self, name: &str) -> Option<&ColumnMetadata> {
        self.columns.iter().find(|c| c.name == name)
    }
    
    /// Get the schema for this table
    pub fn to_schema(&self) -> Schema {
        let mut schema = Schema::new();
        
        // Sort columns by position
        let mut sorted_columns = self.columns.clone();
        sorted_columns.sort_by_key(|c| c.position);
        
        for column in sorted_columns {
            schema.add_column(column.name.clone(), column.data_type.clone(), column.nullable);
        }
        
        schema
    }
}

/// System Catalog - manages database metadata
/// 
/// The catalog stores information about:
/// - Tables (names, columns, constraints)
/// - Indexes (which columns, uniqueness)
/// - Views
/// - Users and permissions
pub struct Catalog {
    /// Map of table name to table metadata
    tables: Arc<RwLock<HashMap<String, TableMetadata>>>,
    
    /// Map of index name to index metadata
    #[allow(dead_code)]
    indexes: Arc<RwLock<HashMap<String, IndexMetadata>>>,
}

impl Catalog {
    /// Create a new empty catalog
    pub fn new() -> Self {
        Catalog {
            tables: Arc::new(RwLock::new(HashMap::new())),
            indexes: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Add a table to the catalog
    pub fn create_table(&self, metadata: TableMetadata) -> Result<(), String> {
        let mut tables = self.tables.write().unwrap();
        
        if tables.contains_key(&metadata.name) {
            return Err(format!("Table {} already exists", metadata.name));
        }
        
        tables.insert(metadata.name.clone(), metadata);
        Ok(())
    }
    
    /// Get table metadata by name
    pub fn get_table(&self, name: &str) -> Option<TableMetadata> {
        self.tables.read().unwrap().get(name).cloned()
    }
    
    /// Drop a table from the catalog
    #[allow(dead_code)]
    pub fn drop_table(&self, name: &str) -> Result<(), String> {
        let mut tables = self.tables.write().unwrap();
        
        if !tables.contains_key(name) {
            return Err(format!("Table {} does not exist", name));
        }
        
        // Remove associated indexes
        let _table = tables.get(name).unwrap();
        let mut indexes = self.indexes.write().unwrap();
        indexes.retain(|_, idx| idx.table_name != name);
        
        tables.remove(name);
        Ok(())
    }
    
    /// List all tables
    pub fn list_tables(&self) -> Vec<String> {
        self.tables.read().unwrap().keys().cloned().collect()
    }
    
    /// Check if a table exists
    #[allow(dead_code)]
    pub fn table_exists(&self, name: &str) -> bool {
        self.tables.read().unwrap().contains_key(name)
    }
    
    /// Add an index to the catalog
    #[allow(dead_code)]
    pub fn create_index(&self, metadata: IndexMetadata) -> Result<(), String> {
        let mut indexes = self.indexes.write().unwrap();
        
        if indexes.contains_key(&metadata.name) {
            return Err(format!("Index {} already exists", metadata.name));
        }
        
        // Verify the table exists
        if !self.table_exists(&metadata.table_name) {
            return Err(format!("Table {} does not exist", metadata.table_name));
        }
        
        indexes.insert(metadata.name.clone(), metadata.clone());
        
        // Add index to table metadata
        let mut tables = self.tables.write().unwrap();
        if let Some(table) = tables.get_mut(&metadata.table_name) {
            table.indexes.push(metadata);
        }
        
        Ok(())
    }
    
    /// Get index metadata by name
    #[allow(dead_code)]
    pub fn get_index(&self, name: &str) -> Option<IndexMetadata> {
        self.indexes.read().unwrap().get(name).cloned()
    }
    
    /// Drop an index from the catalog
    #[allow(dead_code)]
    pub fn drop_index(&self, name: &str) -> Result<(), String> {
        let mut indexes = self.indexes.write().unwrap();
        
        if !indexes.contains_key(name) {
            return Err(format!("Index {} does not exist", name));
        }
        
        let index = indexes.get(name).unwrap();
        let table_name = index.table_name.clone();
        
        indexes.remove(name);
        
        // Remove index from table metadata
        let mut tables = self.tables.write().unwrap();
        if let Some(table) = tables.get_mut(&table_name) {
            table.indexes.retain(|idx| idx.name != name);
        }
        
        Ok(())
    }
    
    /// List all indexes
    #[allow(dead_code)]
    pub fn list_indexes(&self) -> Vec<String> {
        self.indexes.read().unwrap().keys().cloned().collect()
    }
    
    /// Get indexes for a specific table
    #[allow(dead_code)]
    pub fn get_table_indexes(&self, table_name: &str) -> Vec<IndexMetadata> {
        self.indexes.read().unwrap()
            .values()
            .filter(|idx| idx.table_name == table_name)
            .cloned()
            .collect()
    }
    
    /// Add a foreign key to a table
    pub fn add_foreign_key(
        &self,
        table_name: &str,
        columns: Vec<String>,
        ref_table: &str,
        ref_columns: Vec<String>,
    ) -> Result<(), String> {
        // Verify referenced table exists first
        {
            let tables = self.tables.read().unwrap();
            if !tables.contains_key(ref_table) {
                return Err(format!("Referenced table {} does not exist", ref_table));
            }
        }
        
        let mut tables = self.tables.write().unwrap();
        
        if let Some(table) = tables.get_mut(table_name) {
            table.foreign_keys.push((table_name.to_string(), columns, ref_table.to_string(), ref_columns));
            Ok(())
        } else {
            Err(format!("Table {} does not exist", table_name))
        }
    }
    
    /// Get the schema for a table
    pub fn get_table_schema(&self, table_name: &str) -> Option<Schema> {
        self.get_table(table_name).map(|t| t.to_schema())
    }
    
    /// Initialize the catalog with default QuantsMind schema
    pub fn initialize_default_schema(&self) -> Result<(), String> {
        // Users table
        let mut users_table = TableMetadata::new("users".to_string());
        users_table.add_column(ColumnMetadata::new("user_id".to_string(), DataType::UUID, false, 0));
        users_table.add_column(ColumnMetadata::new("email".to_string(), DataType::Varchar(255), false, 1));
        users_table.add_column(ColumnMetadata::new("organization".to_string(), DataType::Varchar(100), false, 2));
        users_table.add_column(ColumnMetadata::new("created_at".to_string(), DataType::Timestamp, false, 3));
        users_table.primary_key = vec!["user_id".to_string()];
        self.create_table(users_table)?;
        
        // API Keys table
        let mut api_keys_table = TableMetadata::new("api_keys".to_string());
        api_keys_table.add_column(ColumnMetadata::new("key_id".to_string(), DataType::UUID, false, 0));
        api_keys_table.add_column(ColumnMetadata::new("user_id".to_string(), DataType::UUID, false, 1));
        api_keys_table.add_column(ColumnMetadata::new("key_hash".to_string(), DataType::Varchar(64), false, 2));
        api_keys_table.add_column(ColumnMetadata::new("rate_limit_rpm".to_string(), DataType::Int, false, 3));
        api_keys_table.primary_key = vec!["key_id".to_string()];
        self.create_table(api_keys_table)?;
        self.add_foreign_key("api_keys", vec!["user_id".to_string()], "users", vec!["user_id".to_string()])?;
        
        // Compute Jobs table
        let mut compute_jobs_table = TableMetadata::new("compute_jobs".to_string());
        compute_jobs_table.add_column(ColumnMetadata::new("job_id".to_string(), DataType::UUID, false, 0));
        compute_jobs_table.add_column(ColumnMetadata::new("user_id".to_string(), DataType::UUID, false, 1));
        compute_jobs_table.add_column(ColumnMetadata::new("target_backend".to_string(), DataType::Varchar(50), false, 2));
        compute_jobs_table.add_column(ColumnMetadata::new("status".to_string(), DataType::Varchar(20), false, 3));
        compute_jobs_table.add_column(ColumnMetadata::new("execution_time_ms".to_string(), DataType::Int, true, 4));
        compute_jobs_table.add_column(ColumnMetadata::new("created_at".to_string(), DataType::Timestamp, false, 5));
        compute_jobs_table.primary_key = vec!["job_id".to_string()];
        self.create_table(compute_jobs_table)?;
        self.add_foreign_key("compute_jobs", vec!["user_id".to_string()], "users", vec!["user_id".to_string()])?;
        
        // Risk Evaluations table
        let mut risk_evaluations_table = TableMetadata::new("risk_evaluations".to_string());
        risk_evaluations_table.add_column(ColumnMetadata::new("eval_id".to_string(), DataType::UUID, false, 0));
        risk_evaluations_table.add_column(ColumnMetadata::new("job_id".to_string(), DataType::UUID, false, 1));
        risk_evaluations_table.add_column(ColumnMetadata::new("portfolio_id".to_string(), DataType::UUID, false, 2));
        risk_evaluations_table.add_column(ColumnMetadata::new("var_99".to_string(), DataType::Numeric(20, 6), false, 3));
        risk_evaluations_table.add_column(ColumnMetadata::new("sharpe_ratio".to_string(), DataType::Numeric(10, 4), false, 4));
        risk_evaluations_table.add_column(ColumnMetadata::new("max_drawdown".to_string(), DataType::Numeric(20, 6), false, 5));
        risk_evaluations_table.add_column(ColumnMetadata::new("evaluated_at".to_string(), DataType::Timestamp, false, 6));
        risk_evaluations_table.primary_key = vec!["eval_id".to_string()];
        self.create_table(risk_evaluations_table)?;
        self.add_foreign_key("risk_evaluations", vec!["job_id".to_string()], "compute_jobs", vec!["job_id".to_string()])?;
        
        Ok(())
    }
}

impl Default for Catalog {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_catalog_creation() {
        let catalog = Catalog::new();
        assert_eq!(catalog.list_tables().len(), 0);
    }

    #[test]
    fn test_create_table() {
        let catalog = Catalog::new();
        
        let mut table = TableMetadata::new("test".to_string());
        table.add_column(ColumnMetadata::new("id".to_string(), DataType::Int, false, 0));
        
        assert!(catalog.create_table(table).is_ok());
        assert!(catalog.table_exists("test"));
    }

    #[test]
    fn test_duplicate_table() {
        let catalog = Catalog::new();
        
        let table = TableMetadata::new("test".to_string());
        catalog.create_table(table.clone()).unwrap();
        
        assert!(catalog.create_table(table).is_err());
    }

    #[test]
    fn test_drop_table() {
        let catalog = Catalog::new();
        
        let table = TableMetadata::new("test".to_string());
        catalog.create_table(table).unwrap();
        
        assert!(catalog.drop_table("test").is_ok());
        assert!(!catalog.table_exists("test"));
    }

    #[test]
    fn test_get_table_schema() {
        let catalog = Catalog::new();
        
        let mut table = TableMetadata::new("test".to_string());
        table.add_column(ColumnMetadata::new("id".to_string(), DataType::Int, false, 0));
        table.add_column(ColumnMetadata::new("name".to_string(), DataType::Varchar(255), true, 1));
        
        catalog.create_table(table).unwrap();
        
        let schema = catalog.get_table_schema("test");
        assert!(schema.is_some());
        
        let schema = schema.unwrap();
        assert_eq!(schema.len(), 2);
        assert_eq!(schema.get_column_name(0), Some("id"));
    }

    #[test]
    fn test_create_index() {
        let catalog = Catalog::new();
        
        let mut table = TableMetadata::new("test".to_string());
        table.add_column(ColumnMetadata::new("id".to_string(), DataType::Int, false, 0));
        catalog.create_table(table).unwrap();
        
        let index = IndexMetadata::new(
            "test_idx".to_string(),
            "test".to_string(),
            vec!["id".to_string()],
            true,
            false,
        );
        
        assert!(catalog.create_index(index).is_ok());
        assert!(catalog.get_index("test_idx").is_some());
    }

    #[test]
    fn test_foreign_key() {
        let catalog = Catalog::new();
        
        let mut users = TableMetadata::new("users".to_string());
        users.add_column(ColumnMetadata::new("id".to_string(), DataType::Int, false, 0));
        catalog.create_table(users).unwrap();
        
        let mut posts = TableMetadata::new("posts".to_string());
        posts.add_column(ColumnMetadata::new("id".to_string(), DataType::Int, false, 0));
        posts.add_column(ColumnMetadata::new("user_id".to_string(), DataType::Int, false, 1));
        catalog.create_table(posts).unwrap();
        
        assert!(catalog.add_foreign_key("posts", vec!["user_id".to_string()], "users", vec!["id".to_string()]).is_ok());
    }

    #[test]
    fn test_initialize_default_schema() {
        let catalog = Catalog::new();
        
        assert!(catalog.initialize_default_schema().is_ok());
        
        assert!(catalog.table_exists("users"));
        assert!(catalog.table_exists("api_keys"));
        assert!(catalog.table_exists("compute_jobs"));
        assert!(catalog.table_exists("risk_evaluations"));
    }
}
