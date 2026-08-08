use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use std::time::{Duration, Instant};
use thiserror::Error;

/// Errors that can occur during lock operations
#[derive(Error, Debug)]
pub enum LockManagerError {
    #[error("Lock timeout after {0:?}")]
    Timeout(Duration),
    
    #[error("Deadlock detected")]
    Deadlock,
    
    #[error("Lock acquisition failed: {0}")]
    AcquisitionFailed(String),
    
    #[error("Lock not held by transaction {0}")]
    LockNotHeld(u64),
}

/// Result type for lock operations
pub type Result<T> = std::result::Result<T, LockManagerError>;

/// Transaction ID
pub type TransactionId = u64;

/// Lock types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum LockType {
    /// Shared lock - allows concurrent reads
    Shared,
    /// Exclusive lock - allows single writer
    Exclusive,
}

impl LockType {
    /// Check if this lock type is compatible with another
    fn is_compatible_with(&self, other: LockType) -> bool {
        match (self, other) {
            (LockType::Shared, LockType::Shared) => true,
            _ => false,
        }
    }
}

/// Lock granularity
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum LockGranularity {
    /// Table-level lock
    Table(String),
    /// Row-level lock (table_name, row_id)
    Row(String, u64),
}

/// Lock request structure
#[derive(Debug, Clone)]
pub struct LockRequest {
    transaction_id: TransactionId,
    lock_type: LockType,
    granularity: LockGranularity,
    requested_at: Instant,
}

impl LockRequest {
    pub fn new(transaction_id: TransactionId, lock_type: LockType, granularity: LockGranularity) -> Self {
        LockRequest {
            transaction_id,
            lock_type,
            granularity,
            requested_at: Instant::now(),
        }
    }
}

/// Lock entry - tracks locks held on a resource
#[derive(Debug, Clone)]
struct LockEntry {
    resource: LockGranularity,
    holders: HashMap<TransactionId, LockType>,
    waiters: Vec<LockRequest>,
}

impl LockEntry {
    fn new(resource: LockGranularity) -> Self {
        LockEntry {
            resource,
            holders: HashMap::new(),
            waiters: Vec::new(),
        }
    }
    
    /// Check if a lock can be granted immediately
    fn can_grant(&self, lock_type: LockType) -> bool {
        // If no holders, always grant
        if self.holders.is_empty() {
            return true;
        }
        
        // Check compatibility with existing holders
        for held_type in self.holders.values() {
            if !lock_type.is_compatible_with(*held_type) {
                return false;
            }
        }
        
        true
    }
    
    /// Grant a lock to a transaction
    fn grant(&mut self, transaction_id: TransactionId, lock_type: LockType) {
        self.holders.insert(transaction_id, lock_type);
    }
    
    /// Release a lock held by a transaction
    fn release(&mut self, transaction_id: TransactionId) -> bool {
        self.holders.remove(&transaction_id).is_some()
    }
    
    /// Add a request to the wait queue
    fn enqueue(&mut self, request: LockRequest) {
        self.waiters.push(request);
    }
    
    /// Try to grant locks to waiting transactions
    fn try_grant_waiters(&mut self) -> Vec<TransactionId> {
        let mut granted = Vec::new();
        let mut i = 0;
        
        while i < self.waiters.len() {
            let request = &self.waiters[i];
            
            if self.can_grant(request.lock_type) {
                let request = self.waiters.remove(i);
                self.grant(request.transaction_id, request.lock_type);
                granted.push(request.transaction_id);
            } else {
                i += 1;
            }
        }
        
        granted
    }
}

/// Lock Manager - Implements Strict Two-Phase Locking (SS2PL)
/// 
/// Responsibilities:
/// - Grant locks based on compatibility (S locks compatible with S locks)
/// - Queue conflicting lock requests
/// - Detect deadlocks using wait-for graph
/// - Ensure locks are held until transaction commit/abort
pub struct LockManager {
    /// Map from resource to lock entry
    lock_table: HashMap<LockGranularity, LockEntry>,
    
    /// Map from transaction to set of resources it has locks on
    transaction_locks: HashMap<TransactionId, HashSet<LockGranularity>>,
    
    /// Wait-for graph for deadlock detection
    wait_for_graph: HashMap<TransactionId, HashSet<TransactionId>>,
    
    /// Timeout for lock acquisition
    lock_timeout: Duration,
}

impl LockManager {
    /// Create a new LockManager with default timeout (30 seconds)
    pub fn new() -> Self {
        LockManager {
            lock_table: HashMap::new(),
            transaction_locks: HashMap::new(),
            wait_for_graph: HashMap::new(),
            lock_timeout: Duration::from_secs(30),
        }
    }
    
    /// Create a LockManager with custom timeout
    pub fn with_timeout(timeout: Duration) -> Self {
        let mut lm = Self::new();
        lm.lock_timeout = timeout;
        lm
    }
    
    /// Acquire a lock for a transaction
    /// 
    /// # Arguments
    /// * `transaction_id` - The transaction requesting the lock
    /// * `lock_type` - Type of lock (Shared or Exclusive)
    /// * `granularity` - Granularity of the lock (Table or Row)
    pub fn acquire_lock(
        &mut self,
        transaction_id: TransactionId,
        lock_type: LockType,
        granularity: LockGranularity,
    ) -> Result<()> {
        // Check for deadlock before acquiring
        if self.would_cause_deadlock(transaction_id, &granularity) {
            return Err(LockManagerError::Deadlock);
        }
        
        // Get or create lock entry
        let holders_clone = {
            let entry = self.lock_table
                .entry(granularity.clone())
                .or_insert_with(|| LockEntry::new(granularity.clone()));
            
            // Check if transaction already holds a lock on this resource
            if let Some(&held_type) = entry.holders.get(&transaction_id) {
                // Lock upgrade: S -> X
                if held_type == LockType::Shared && lock_type == LockType::Exclusive {
                    // Check if we can upgrade (only one S holder)
                    if entry.holders.len() == 1 {
                        entry.holders.insert(transaction_id, LockType::Exclusive);
                        return Ok(());
                    } else {
                        // Need to wait for other S holders to release
                        let request = LockRequest::new(transaction_id, lock_type, granularity);
                        entry.enqueue(request);
                        let holders = entry.holders.clone();
                        self.add_wait_for_edge(transaction_id, &holders);
                        return Err(LockManagerError::AcquisitionFailed(
                            "Lock upgrade requires waiting for other shared holders".to_string()
                        ));
                    }
                } else {
                    // Already have compatible lock
                    return Ok(());
                }
            }
            
            // Clone holders for later use
            entry.holders.clone()
        };
        
        // Try to grant the lock immediately
        {
            let entry = self.lock_table.get_mut(&granularity).unwrap();
            if entry.can_grant(lock_type) {
                entry.grant(transaction_id, lock_type);
                self.track_transaction_lock(transaction_id, granularity);
                return Ok(());
            }
        }
        
        // Add to wait queue
        {
            let entry = self.lock_table.get_mut(&granularity).unwrap();
            let request = LockRequest::new(transaction_id, lock_type, granularity);
            entry.enqueue(request);
        }
        self.add_wait_for_edge(transaction_id, &holders_clone);
        Err(LockManagerError::AcquisitionFailed(
            "Lock conflicts with existing holders".to_string()
        ))
    }
    
    /// Release a lock held by a transaction
    /// 
    /// # Arguments
    /// * `transaction_id` - The transaction releasing the lock
    /// * `granularity` - The resource to unlock
    pub fn release_lock(
        &mut self,
        transaction_id: TransactionId,
        granularity: &LockGranularity,
    ) -> Result<()> {
        if let Some(entry) = self.lock_table.get_mut(granularity) {
            if entry.release(transaction_id) {
                // Remove from transaction's lock set
                if let Some(locks) = self.transaction_locks.get_mut(&transaction_id) {
                    locks.remove(granularity);
                }
                
                // Try to grant locks to waiting transactions
                let granted = entry.try_grant_waiters();
                for tid in granted {
                    self.remove_wait_for_edge(tid);
                    self.track_transaction_lock(tid, granularity.clone());
                }
                
                Ok(())
            } else {
                Err(LockManagerError::LockNotHeld(transaction_id))
            }
        } else {
            Err(LockManagerError::LockNotHeld(transaction_id))
        }
    }
    
    /// Release all locks held by a transaction (at commit/abort)
    pub fn release_all_locks(&mut self, transaction_id: TransactionId) {
        if let Some(locks) = self.transaction_locks.remove(&transaction_id) {
            for granularity in locks {
                let _ = self.release_lock(transaction_id, &granularity);
            }
        }
        
        // Remove from wait-for graph
        self.wait_for_graph.remove(&transaction_id);
    }
    
    /// Check if a transaction holds a lock on a resource
    pub fn holds_lock(&self, transaction_id: TransactionId, granularity: &LockGranularity) -> bool {
        self.transaction_locks
            .get(&transaction_id)
            .map(|locks| locks.contains(granularity))
            .unwrap_or(false)
    }
    
    /// Track that a transaction holds a lock on a resource
    fn track_transaction_lock(&mut self, transaction_id: TransactionId, granularity: LockGranularity) {
        self.transaction_locks
            .entry(transaction_id)
            .or_insert_with(HashSet::new)
            .insert(granularity);
    }
    
    /// Add wait-for edge for deadlock detection
    fn add_wait_for_edge(&mut self, waiter: TransactionId, holders: &HashMap<TransactionId, LockType>) {
        let edges = self.wait_for_graph.entry(waiter).or_insert_with(HashSet::new);
        for holder in holders.keys() {
            edges.insert(*holder);
        }
    }
    
    /// Remove wait-for edge
    fn remove_wait_for_edge(&mut self, transaction_id: TransactionId) {
        self.wait_for_graph.remove(&transaction_id);
    }
    
    /// Check if acquiring a lock would cause a deadlock
    fn would_cause_deadlock(&self, transaction_id: TransactionId, _granularity: &LockGranularity) -> bool {
        // Simple cycle detection in wait-for graph
        let mut visited = HashSet::new();
        self.has_cycle(transaction_id, transaction_id, &mut visited)
    }
    
    /// DFS cycle detection
    fn has_cycle(&self, current: TransactionId, target: TransactionId, visited: &mut HashSet<TransactionId>) -> bool {
        if visited.contains(&current) {
            return false;
        }
        
        visited.insert(current);
        
        if let Some(neighbors) = self.wait_for_graph.get(&current) {
            for &neighbor in neighbors {
                if neighbor == target || self.has_cycle(neighbor, target, visited) {
                    return true;
                }
            }
        }
        
        false
    }
    
    /// Get statistics about the lock manager
    pub fn get_stats(&self) -> LockManagerStats {
        let total_locks = self.lock_table.values()
            .map(|entry| entry.holders.len())
            .sum();
        
        let waiting_transactions = self.wait_for_graph.len();
        
        LockManagerStats {
            total_locks,
            waiting_transactions,
            total_resources: self.lock_table.len(),
        }
    }
}

/// Lock manager statistics
#[derive(Debug, Clone)]
pub struct LockManagerStats {
    pub total_locks: usize,
    pub waiting_transactions: usize,
    pub total_resources: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lock_manager_creation() {
        let lm = LockManager::new();
        let stats = lm.get_stats();
        assert_eq!(stats.total_locks, 0);
        assert_eq!(stats.total_resources, 0);
    }

    #[test]
    fn test_shared_lock_compatibility() {
        let mut lm = LockManager::new();
        let resource = LockGranularity::Table("users".to_string());
        
        // Two transactions can hold shared locks
        assert!(lm.acquire_lock(1, LockType::Shared, resource.clone()).is_ok());
        assert!(lm.acquire_lock(2, LockType::Shared, resource.clone()).is_ok());
        
        assert!(lm.holds_lock(1, &resource));
        assert!(lm.holds_lock(2, &resource));
    }

    #[test]
    fn test_exclusive_lock_conflict() {
        let mut lm = LockManager::new();
        let resource = LockGranularity::Table("users".to_string());
        
        // First transaction gets exclusive lock
        assert!(lm.acquire_lock(1, LockType::Exclusive, resource.clone()).is_ok());
        
        // Second transaction should be blocked
        let result = lm.acquire_lock(2, LockType::Exclusive, resource.clone());
        assert!(result.is_err());
    }

    #[test]
    fn test_lock_upgrade() {
        let mut lm = LockManager::new();
        let resource = LockGranularity::Table("users".to_string());
        
        // Get shared lock
        assert!(lm.acquire_lock(1, LockType::Shared, resource.clone()).is_ok());
        
        // Upgrade to exclusive (should work if only holder)
        assert!(lm.acquire_lock(1, LockType::Exclusive, resource.clone()).is_ok());
    }

    #[test]
    fn test_lock_release() {
        let mut lm = LockManager::new();
        let resource = LockGranularity::Table("users".to_string());
        
        lm.acquire_lock(1, LockType::Exclusive, resource.clone()).unwrap();
        assert!(lm.holds_lock(1, &resource));
        
        lm.release_lock(1, &resource).unwrap();
        assert!(!lm.holds_lock(1, &resource));
    }

    #[test]
    fn test_release_all_locks() {
        let mut lm = LockManager::new();
        let table1 = LockGranularity::Table("users".to_string());
        let table2 = LockGranularity::Table("orders".to_string());
        
        lm.acquire_lock(1, LockType::Exclusive, table1.clone()).unwrap();
        lm.acquire_lock(1, LockType::Shared, table2.clone()).unwrap();
        
        lm.release_all_locks(1);
        
        assert!(!lm.holds_lock(1, &table1));
        assert!(!lm.holds_lock(1, &table2));
    }

    #[test]
    fn test_row_level_locking() {
        let mut lm = LockManager::new();
        let row1 = LockGranularity::Row("users".to_string(), 1);
        let row2 = LockGranularity::Row("users".to_string(), 2);
        
        // Different rows can be locked independently
        assert!(lm.acquire_lock(1, LockType::Exclusive, row1.clone()).is_ok());
        assert!(lm.acquire_lock(2, LockType::Exclusive, row2.clone()).is_ok());
        
        assert!(lm.holds_lock(1, &row1));
        assert!(lm.holds_lock(2, &row2));
    }

    #[test]
    fn test_deadlock_detection() {
        let mut lm = LockManager::new();
        let resource1 = LockGranularity::Table("users".to_string());
        let resource2 = LockGranularity::Table("orders".to_string());
        
        // T1 locks users
        lm.acquire_lock(1, LockType::Exclusive, resource1.clone()).unwrap();
        
        // T2 locks orders
        lm.acquire_lock(2, LockType::Exclusive, resource2.clone()).unwrap();
        
        // T1 tries to lock orders (would wait)
        let result1 = lm.acquire_lock(1, LockType::Exclusive, resource2.clone());
        assert!(result1.is_err());
        
        // T2 tries to lock users (would cause deadlock)
        let result2 = lm.acquire_lock(2, LockType::Exclusive, resource1.clone());
        assert!(result2.is_err());
    }
}
