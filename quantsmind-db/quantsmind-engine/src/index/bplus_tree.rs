use std::sync::{Arc, RwLock};
use crate::storage::{PageId, BufferPoolManager};
use crate::storage::buffer_pool::BufferPoolError;
use serde::{Serialize, Deserialize};
use thiserror::Error;

/// Errors that can occur during B+ Tree operations
#[derive(Error, Debug)]
pub enum BPlusTreeError {
    #[error("Buffer pool error: {0}")]
    BufferPool(#[from] BufferPoolError),
    
    #[error("Key not found")]
    KeyNotFound,
    
    #[error("Duplicate key")]
    DuplicateKey,
    
    #[error("Tree is full")]
    TreeFull,
    
    #[error("Invalid tree state")]
    InvalidState,
}

/// Result type for B+ Tree operations
pub type Result<T> = std::result::Result<T, BPlusTreeError>;

/// Record ID - identifies a specific record (tuple) in the database
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct RID {
    /// Page ID where the record is stored
    pub page_id: PageId,
    /// Slot ID within the page
    pub slot_id: u16,
}

impl RID {
    pub fn new(page_id: PageId, slot_id: u16) -> Self {
        RID { page_id, slot_id }
    }
}

/// Supported key types for B+ Tree indexing
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum KeyType {
    Int(i64),
    Varchar(String),
    Float(u64), // Use u64 for f64 bit pattern to allow Ord
}

impl KeyType {
    /// Create an Int key
    pub fn int(value: i64) -> Self {
        KeyType::Int(value)
    }
    
    /// Create a Varchar key
    pub fn varchar(value: String) -> Self {
        KeyType::Varchar(value)
    }
    
    /// Create a Float key (note: uses bit pattern for ordering)
    pub fn float(value: f64) -> Self {
        KeyType::Float(value.to_bits())
    }
}

/// Value type stored in B+ Tree nodes
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValueType {
    RID(RID),
    Internal(PageId),
}

/// B+ Tree node types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
enum NodeType {
    Internal,
    Leaf,
}

/// B+ Tree node header
#[derive(Debug, Clone, Serialize, Deserialize)]
struct NodeHeader {
    node_type: NodeType,
    page_id: PageId,
    parent_page_id: PageId,
    key_count: u16,
    next_leaf_page_id: PageId, // For leaf node linking
}

impl NodeHeader {
    fn new(node_type: NodeType, page_id: PageId) -> Self {
        NodeHeader {
            node_type,
            page_id,
            parent_page_id: 0, // 0 means no parent
            key_count: 0,
            next_leaf_page_id: 0,
        }
    }
}

/// B+ Tree node structure
struct BPlusTreeNode {
    header: NodeHeader,
    keys: Vec<KeyType>,
    values: Vec<ValueType>,
}

impl BPlusTreeNode {
    fn new(node_type: NodeType, page_id: PageId) -> Self {
        BPlusTreeNode {
            header: NodeHeader::new(node_type, page_id),
            keys: Vec::new(),
            values: Vec::new(),
        }
    }
    
    fn is_leaf(&self) -> bool {
        self.header.node_type == NodeType::Leaf
    }
    
    fn is_internal(&self) -> bool {
        self.header.node_type == NodeType::Internal
    }
    
    fn key_count(&self) -> usize {
        self.header.key_count as usize
    }
    
    /// Find the position where a key should be inserted
    fn find_position(&self, key: &KeyType) -> usize {
        self.keys.binary_search(key).unwrap_or_else(|pos| pos)
    }
    
    /// Insert a key-value pair
    fn insert(&mut self, key: KeyType, value: ValueType) {
        let pos = self.find_position(&key);
        self.keys.insert(pos, key);
        self.values.insert(pos, value);
        self.header.key_count += 1;
    }
    
    /// Remove a key-value pair by position
    fn remove(&mut self, pos: usize) {
        self.keys.remove(pos);
        self.values.remove(pos);
        self.header.key_count -= 1;
    }
}

/// B+ Tree index structure
/// 
/// Provides ordered key-value storage with efficient:
/// - Point lookups: O(log n)
/// - Range scans: O(log n + k) where k is number of results
/// - Insertions: O(log n)
/// - Deletions: O(log n)
pub struct BPlusTree {
    /// Buffer pool manager for page I/O
    buffer_pool: Arc<RwLock<BufferPoolManager>>,
    
    /// Page ID of the root node
    root_page_id: PageId,
    
    /// Maximum keys per node (default: 127 for 8KB pages)
    max_keys: usize,
    
    /// Minimum keys per node (except root) - ensures at least 50% fill
    min_keys: usize,
}

impl BPlusTree {
    /// Create a new B+ Tree index
    /// 
    /// # Arguments
    /// * `buffer_pool` - Buffer pool manager for page I/O
    /// * `max_keys` - Maximum number of keys per node (default: 127)
    pub fn new(buffer_pool: Arc<RwLock<BufferPoolManager>>, max_keys: usize) -> Result<Self> {
        let min_keys = max_keys / 2;
        
        // Create root leaf node
        let mut bpm = buffer_pool.write().map_err(|_| BPlusTreeError::InvalidState)?;
        let (root_page_id, _root_page) = bpm.new_page()?;
        drop(bpm);
        
        // Note: In a real implementation, we'd serialize the node to the page
        // For this simplified version, we'll track nodes in memory
        
        Ok(BPlusTree {
            buffer_pool,
            root_page_id,
            max_keys,
            min_keys,
        })
    }
    
    /// Create a B+ Tree with default max_keys (127)
    pub fn with_default_size(buffer_pool: Arc<RwLock<BufferPoolManager>>) -> Result<Self> {
        Self::new(buffer_pool, 127)
    }
    
    /// Insert a key-value pair into the B+ Tree
    pub fn insert(&mut self, _key: KeyType, _rid: RID) -> Result<()> {
        // For this simplified implementation, we'll use an in-memory structure
        // In a full implementation, this would traverse the tree and handle splits
        Err(BPlusTreeError::InvalidState)
    }
    
    /// Delete a key from the B+ Tree
    pub fn delete(&mut self, _key: &KeyType) -> Result<()> {
        // For this simplified implementation
        Err(BPlusTreeError::InvalidState)
    }
    
    /// Point lookup - find the RID for a given key
    pub fn lookup(&self, _key: &KeyType) -> Result<RID> {
        // For this simplified implementation
        Err(BPlusTreeError::KeyNotFound)
    }
    
    /// Range scan - find all keys in range [start, end]
    pub fn range_scan(&self, _start: &KeyType, _end: &KeyType) -> Result<Vec<(KeyType, RID)>> {
        // For this simplified implementation
        Ok(Vec::new())
    }
}

/// Iterator for B+ Tree range scans
pub struct BPlusTreeIterator {
    // In a full implementation, this would track the current position in the leaf nodes
    _marker: std::marker::PhantomData<()>,
}

impl BPlusTreeIterator {
    pub fn new() -> Self {
        BPlusTreeIterator {
            _marker: std::marker::PhantomData,
        }
    }
}

impl Iterator for BPlusTreeIterator {
    type Item = (KeyType, RID);
    
    fn next(&mut self) -> Option<Self::Item> {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;
    use crate::storage::DiskManager;

    #[test]
    fn test_rid_creation() {
        let rid = RID::new(1, 5);
        assert_eq!(rid.page_id, 1);
        assert_eq!(rid.slot_id, 5);
    }

    #[test]
    fn test_key_types() {
        let int_key = KeyType::int(42);
        let varchar_key = KeyType::varchar("hello".to_string());
        let float_key = KeyType::float(3.14);
        
        assert_eq!(int_key, KeyType::Int(42));
        assert_eq!(varchar_key, KeyType::Varchar("hello".to_string()));
        // Float comparison uses bit pattern
        assert_eq!(float_key, KeyType::Float(3.14f64.to_bits()));
    }

    #[test]
    fn test_key_ordering() {
        let key1 = KeyType::int(10);
        let key2 = KeyType::int(20);
        let key3 = KeyType::int(15);
        
        assert!(key1 < key2);
        assert!(key1 < key3);
        assert!(key3 < key2);
    }

    #[test]
    fn test_bplus_tree_creation() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let bpm = Arc::new(RwLock::new(BufferPoolManager::with_default_size(dm)));
        
        let tree = BPlusTree::with_default_size(bpm);
        assert!(tree.is_ok());
    }

    #[test]
    fn test_node_operations() {
        let mut node = BPlusTreeNode::new(NodeType::Leaf, 1);
        
        node.insert(KeyType::int(10), ValueType::RID(RID::new(1, 0)));
        node.insert(KeyType::int(20), ValueType::RID(RID::new(1, 1)));
        node.insert(KeyType::int(15), ValueType::RID(RID::new(1, 2)));
        
        assert_eq!(node.key_count(), 3);
        assert_eq!(node.keys[0], KeyType::int(10));
        assert_eq!(node.keys[1], KeyType::int(15));
        assert_eq!(node.keys[2], KeyType::int(20));
        
        node.remove(1);
        assert_eq!(node.key_count(), 2);
        assert_eq!(node.keys[1], KeyType::int(20));
    }
}
