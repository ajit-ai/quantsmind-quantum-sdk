use serde::{Serialize, Deserialize};
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// Supported data types in QuantsMind DB
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum DataType {
    /// 128-bit UUID
    UUID,
    /// Variable-length string
    Varchar(usize), // max length
    /// 64-bit signed integer
    Int,
    /// 64-bit floating point
    Float,
    /// Boolean
    Boolean,
    /// Timestamp (UTC)
    Timestamp,
    /// Numeric with precision and scale
    Numeric(u8, u8), // precision, scale
}

impl DataType {
    /// Get the name of the data type
    pub fn name(&self) -> &str {
        match self {
            DataType::UUID => "UUID",
            DataType::Varchar(_) => "VARCHAR",
            DataType::Int => "INT",
            DataType::Float => "FLOAT",
            DataType::Boolean => "BOOLEAN",
            DataType::Timestamp => "TIMESTAMP",
            DataType::Numeric(_, _) => "NUMERIC",
        }
    }
}

/// Value type representing data stored in tuples
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Value {
    /// UUID value
    UUID(Uuid),
    /// String value
    Varchar(String),
    /// Integer value
    Int(i64),
    /// Float value
    Float(f64),
    /// Boolean value
    Boolean(bool),
    /// Timestamp value
    Timestamp(DateTime<Utc>),
    /// Numeric value (stored as string for precision)
    Numeric(String),
    /// Null value
    Null,
}

impl Value {
    /// Get the data type of this value
    #[allow(dead_code)]
    pub fn get_type(&self) -> DataType {
        match self {
            Value::UUID(_) => DataType::UUID,
            Value::Varchar(s) => DataType::Varchar(s.len()),
            Value::Int(_) => DataType::Int,
            Value::Float(_) => DataType::Float,
            Value::Boolean(_) => DataType::Boolean,
            Value::Timestamp(_) => DataType::Timestamp,
            Value::Numeric(_) => DataType::Numeric(38, 10), // Default precision
            Value::Null => DataType::Varchar(0), // Null has no specific type
        }
    }
    
    /// Check if the value is null
    #[allow(dead_code)]
    pub fn is_null(&self) -> bool {
        matches!(self, Value::Null)
    }
    
    /// Convert value to string representation
    pub fn to_string(&self) -> String {
        match self {
            Value::UUID(u) => u.to_string(),
            Value::Varchar(s) => s.clone(),
            Value::Int(i) => i.to_string(),
            Value::Float(f) => f.to_string(),
            Value::Boolean(b) => b.to_string(),
            Value::Timestamp(dt) => dt.to_rfc3339(),
            Value::Numeric(n) => n.clone(),
            Value::Null => "NULL".to_string(),
        }
    }
    
    /// Create a null value
    #[allow(dead_code)]
    pub fn null() -> Self {
        Value::Null
    }
}

impl PartialEq for Value {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Value::UUID(a), Value::UUID(b)) => a == b,
            (Value::Varchar(a), Value::Varchar(b)) => a == b,
            (Value::Int(a), Value::Int(b)) => a == b,
            (Value::Float(a), Value::Float(b)) => a.to_bits() == b.to_bits(),
            (Value::Boolean(a), Value::Boolean(b)) => a == b,
            (Value::Timestamp(a), Value::Timestamp(b)) => a == b,
            (Value::Numeric(a), Value::Numeric(b)) => a == b,
            (Value::Null, Value::Null) => true,
            _ => false,
        }
    }
}

/// Tuple - represents a row in a table
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Tuple {
    /// The values in the tuple
    values: Vec<Value>,
}

impl Tuple {
    /// Create a new tuple from values
    pub fn new(values: Vec<Value>) -> Self {
        Tuple { values }
    }
    
    /// Get the number of values in the tuple
    #[allow(dead_code)]
    pub fn len(&self) -> usize {
        self.values.len()
    }
    
    /// Check if the tuple is empty
    #[allow(dead_code)]
    pub fn is_empty(&self) -> bool {
        self.values.is_empty()
    }
    
    /// Get a value by index
    pub fn get(&self, index: usize) -> Option<&Value> {
        self.values.get(index)
    }
    
    /// Get a mutable reference to a value by index
    #[allow(dead_code)]
    pub fn get_mut(&mut self, index: usize) -> Option<&mut Value> {
        self.values.get_mut(index)
    }
    
    /// Get all values
    pub fn values(&self) -> &[Value] {
        &self.values
    }
    
    /// Convert tuple to a vector of values
    #[allow(dead_code)]
    pub fn into_values(self) -> Vec<Value> {
        self.values
    }
}

impl IntoIterator for Tuple {
    type Item = Value;
    type IntoIter = std::vec::IntoIter<Value>;
    
    fn into_iter(self) -> Self::IntoIter {
        self.values.into_iter()
    }
}

/// Schema - defines the structure of a table
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Schema {
    /// Column names
    columns: Vec<String>,
    /// Column types
    types: Vec<DataType>,
    /// Whether each column is nullable
    nullable: Vec<bool>,
}

impl Schema {
    /// Create a new schema
    pub fn new() -> Self {
        Schema {
            columns: Vec::new(),
            types: Vec::new(),
            nullable: Vec::new(),
        }
    }
    
    /// Add a column to the schema
    pub fn add_column(&mut self, name: String, data_type: DataType, nullable: bool) {
        self.columns.push(name);
        self.types.push(data_type);
        self.nullable.push(nullable);
    }
    
    /// Get the number of columns
    #[allow(dead_code)]
    pub fn len(&self) -> usize {
        self.columns.len()
    }
    
    /// Check if the schema is empty
    #[allow(dead_code)]
    pub fn is_empty(&self) -> bool {
        self.columns.is_empty()
    }
    
    /// Get column name by index
    pub fn get_column_name(&self, index: usize) -> Option<&str> {
        self.columns.get(index).map(|s| s.as_str())
    }
    
    /// Get column type by index
    pub fn get_column_type(&self, index: usize) -> Option<&DataType> {
        self.types.get(index)
    }
    
    /// Check if column is nullable by index
    pub fn is_nullable(&self, index: usize) -> Option<bool> {
        self.nullable.get(index).copied()
    }
    
    /// Get all column names
    pub fn columns(&self) -> &[String] {
        &self.columns
    }
    
    /// Get all column types
    #[allow(dead_code)]
    pub fn types(&self) -> &[DataType] {
        &self.types
    }
    
    /// Find the index of a column by name
    pub fn find_column(&self, name: &str) -> Option<usize> {
        self.columns.iter().position(|c| c == name)
    }
    
    /// Validate a tuple against this schema
    #[allow(dead_code)]
    pub fn validate_tuple(&self, tuple: &Tuple) -> bool {
        if tuple.len() != self.len() {
            return false;
        }
        
        for (i, value) in tuple.values().iter().enumerate() {
            if let Some(data_type) = self.get_column_type(i) {
                // Check type compatibility
                match (data_type, value) {
                    (DataType::UUID, Value::UUID(_)) => {},
                    (DataType::Varchar(_), Value::Varchar(_)) => {},
                    (DataType::Int, Value::Int(_)) => {},
                    (DataType::Float, Value::Float(_)) => {},
                    (DataType::Boolean, Value::Boolean(_)) => {},
                    (DataType::Timestamp, Value::Timestamp(_)) => {},
                    (DataType::Numeric(_, _), Value::Numeric(_)) => {},
                    (_, Value::Null) => {
                        // Null is allowed only if column is nullable
                        if !self.is_nullable(i).unwrap_or(true) {
                            return false;
                        }
                    }
                    _ => return false,
                }
            }
        }
        
        true
    }
}

impl Default for Schema {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_value_creation() {
        let uuid_val = Value::UUID(Uuid::new_v4());
        let int_val = Value::Int(42);
        let float_val = Value::Float(3.14);
        let bool_val = Value::Boolean(true);
        let null_val = Value::Null;
        
        assert!(!uuid_val.is_null());
        assert!(!int_val.is_null());
        assert!(!float_val.is_null());
        assert!(!bool_val.is_null());
        assert!(null_val.is_null());
    }

    #[test]
    fn test_value_equality() {
        let val1 = Value::Int(42);
        let val2 = Value::Int(42);
        let val3 = Value::Int(43);
        
        assert_eq!(val1, val2);
        assert_ne!(val1, val3);
    }

    #[test]
    fn test_tuple_creation() {
        let tuple = Tuple::new(vec![
            Value::Int(1),
            Value::Varchar("hello".to_string()),
            Value::Float(3.14),
        ]);
        
        assert_eq!(tuple.len(), 3);
        assert_eq!(tuple.get(0), Some(&Value::Int(1)));
        assert_eq!(tuple.get(1), Some(&Value::Varchar("hello".to_string())));
    }

    #[test]
    fn test_schema_creation() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), DataType::Int, false);
        schema.add_column("name".to_string(), DataType::Varchar(255), true);
        
        assert_eq!(schema.len(), 2);
        assert_eq!(schema.get_column_name(0), Some("id"));
        assert_eq!(schema.get_column_type(0), Some(&DataType::Int));
        assert_eq!(schema.is_nullable(0), Some(false));
        assert_eq!(schema.is_nullable(1), Some(true));
    }

    #[test]
    fn test_schema_find_column() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), DataType::Int, false);
        schema.add_column("name".to_string(), DataType::Varchar(255), true);
        
        assert_eq!(schema.find_column("id"), Some(0));
        assert_eq!(schema.find_column("name"), Some(1));
        assert_eq!(schema.find_column("unknown"), None);
    }

    #[test]
    fn test_schema_validation() {
        let mut schema = Schema::new();
        schema.add_column("id".to_string(), DataType::Int, false);
        schema.add_column("name".to_string(), DataType::Varchar(255), true);
        
        let valid_tuple = Tuple::new(vec![
            Value::Int(1),
            Value::Varchar("test".to_string()),
        ]);
        
        let invalid_tuple = Tuple::new(vec![
            Value::Varchar("not an int".to_string()),
            Value::Varchar("test".to_string()),
        ]);
        
        assert!(schema.validate_tuple(&valid_tuple));
        assert!(!schema.validate_tuple(&invalid_tuple));
    }

    #[test]
    fn test_tuple_iteration() {
        let tuple = Tuple::new(vec![
            Value::Int(1),
            Value::Int(2),
            Value::Int(3),
        ]);
        
        let sum: i64 = tuple.into_iter().map(|v| {
            if let Value::Int(i) = v {
                i
            } else {
                0
            }
        }).sum();
        
        assert_eq!(sum, 6);
    }
}
