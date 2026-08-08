use std::fs::{File, OpenOptions};
use std::io::{Read, Write, Seek, SeekFrom};
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::collections::HashSet;
use serde::{Serialize, Deserialize};
use thiserror::Error;

/// Errors that can occur during WAL operations
#[derive(Error, Debug)]
pub enum WALError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Invalid WAL record: {0}")]
    InvalidRecord(String),
    
    #[error("WAL file corrupted")]
    Corrupted,
    
    #[error("Checkpoint failed: {0}")]
    CheckpointFailed(String),
}

/// Result type for WAL operations
pub type Result<T> = std::result::Result<T, WALError>;

/// Log Sequence Number - unique identifier for each WAL record
#[allow(dead_code)]
pub type LSN = u64;

/// WAL record types
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[allow(dead_code)]
pub enum WALRecordType {
    /// Transaction begin
    Begin,
    /// Insert operation
    Insert,
    /// Update operation
    Update,
    /// Delete operation
    Delete,
    /// Transaction commit
    Commit,
    /// Transaction abort
    Abort,
    /// Checkpoint marker
    Checkpoint,
}

/// WAL record structure
#[derive(Debug, Clone, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct WALRecord {
    /// Log Sequence Number
    pub lsn: LSN,
    /// Transaction ID
    pub transaction_id: u64,
    /// Record type
    pub record_type: WALRecordType,
    /// Page ID being modified (for CRUD operations)
    pub page_id: Option<u32>,
    /// Before image (for undo)
    pub before_image: Option<Vec<u8>>,
    /// After image (for redo)
    pub after_image: Option<Vec<u8>>,
    /// Timestamp
    pub timestamp: i64,
}

#[allow(dead_code)]
impl WALRecord {
    /// Create a new WAL record
    pub fn new(
        lsn: LSN,
        transaction_id: u64,
        record_type: WALRecordType,
    ) -> Self {
        WALRecord {
            lsn,
            transaction_id,
            record_type,
            page_id: None,
            before_image: None,
            after_image: None,
            timestamp: chrono::Utc::now().timestamp(),
        }
    }
    
    /// Set page ID for the record
    #[allow(dead_code)]
    pub fn with_page_id(mut self, page_id: u32) -> Self {
        self.page_id = Some(page_id);
        self
    }
    
    /// Set before image
    #[allow(dead_code)]
    pub fn with_before_image(mut self, image: Vec<u8>) -> Self {
        self.before_image = Some(image);
        self
    }
    
    /// Set after image
    #[allow(dead_code)]
    pub fn with_after_image(mut self, image: Vec<u8>) -> Self {
        self.after_image = Some(image);
        self
    }
    
    /// Serialize record to bytes
    #[allow(dead_code)]
    pub fn to_bytes(&self) -> Result<Vec<u8>> {
        bincode::serialize(self)
            .map_err(|e| WALError::InvalidRecord(e.to_string()))
    }
    
    /// Deserialize record from bytes
    #[allow(dead_code)]
    pub fn from_bytes(bytes: &[u8]) -> Result<Self> {
        bincode::deserialize(bytes)
            .map_err(|e| WALError::InvalidRecord(e.to_string()))
    }
}

/// WAL Manager - Write-Ahead Logging for crash recovery
/// 
/// Responsibilities:
/// - Append log records to durable storage
/// - Ensure WAL invariant: log must be flushed before data pages
/// - Support ARIES recovery protocol (Analysis, Redo, Undo)
/// - Periodic checkpointing to reduce recovery time
#[allow(dead_code)]
pub struct WALManager {
    /// WAL file handle
    file: Arc<Mutex<File>>,
    
    /// Path to the WAL file
    file_path: String,
    
    /// Next LSN to assign
    next_lsn: Arc<Mutex<LSN>>,
    
    /// Last flushed LSN
    flushed_lsn: Arc<Mutex<LSN>>,
    
    /// Last checkpoint LSN
    checkpoint_lsn: Arc<Mutex<LSN>>,
    
    /// Buffer for batching log records
    buffer: Arc<Mutex<Vec<WALRecord>>>,
    
    /// Buffer size threshold for flushing
    buffer_size: usize,
}

#[allow(dead_code)]
impl WALManager {
    /// Create a new WALManager
    /// 
    /// # Arguments
    /// * `file_path` - Path to the WAL file
    /// * `buffer_size` - Number of records to buffer before flushing (default: 100)
    pub fn new<P: AsRef<Path>>(file_path: P, buffer_size: usize) -> Result<Self> {
        let path = file_path.as_ref().to_string_lossy().to_string();
        
        // Open or create the WAL file
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .append(true)
            .open(&path)?;
        
        // Read existing records to determine next LSN
        let next_lsn = Self::read_next_lsn(&file)?;
        
        Ok(WALManager {
            file: Arc::new(Mutex::new(file)),
            file_path: path,
            next_lsn: Arc::new(Mutex::new(next_lsn)),
            flushed_lsn: Arc::new(Mutex::new(0)),
            checkpoint_lsn: Arc::new(Mutex::new(0)),
            buffer: Arc::new(Mutex::new(Vec::new())),
            buffer_size,
        })
    }
    
    /// Create a WALManager with default buffer size (100 records)
    #[allow(dead_code)]
    pub fn with_default_size<P: AsRef<Path>>(file_path: P) -> Result<Self> {
        Self::new(file_path, 100)
    }
    
    /// Read the next LSN from existing WAL file
    #[allow(dead_code)]
    fn read_next_lsn(file: &File) -> Result<LSN> {
        let metadata = file.metadata()?;
        if metadata.len() == 0 {
            return Ok(1); // Start with LSN 1
        }
        
        // In a real implementation, we'd scan the file to find the highest LSN
        // For simplicity, we'll just return 1
        Ok(1)
    }
    
    /// Append a log record
    /// 
    /// # Arguments
    /// * `record` - The WAL record to append
    #[allow(dead_code)]
    pub fn append_record(&self, record: WALRecord) -> Result<LSN> {
        let lsn = {
            let mut next_lsn = self.next_lsn.lock().unwrap();
            let lsn = *next_lsn;
            *next_lsn += 1;
            lsn
        };
        
        // Create record with assigned LSN
        let mut record = record;
        record.lsn = lsn;
        
        // Add to buffer
        {
            let mut buffer = self.buffer.lock().unwrap();
            buffer.push(record.clone());
            
            // Flush if buffer is full
            if buffer.len() >= self.buffer_size {
                self.flush_buffer_internal(&mut buffer)?;
            }
        }
        
        Ok(lsn)
    }
    
    /// Flush the buffer to disk
    #[allow(dead_code)]
    fn flush_buffer_internal(&self, buffer: &mut Vec<WALRecord>) -> Result<()> {
        if buffer.is_empty() {
            return Ok(());
        }
        
        let mut file = self.file.lock().unwrap();
        
        for record in buffer.iter() {
            let bytes = record.to_bytes()?;
            
            // Write record length followed by record data
            let length = bytes.len() as u32;
            file.write_all(&length.to_be_bytes())?;
            file.write_all(&bytes)?;
        }
        
        file.flush()?;
        
        // Update flushed LSN
        if let Some(last_record) = buffer.last() {
            let mut flushed_lsn = self.flushed_lsn.lock().unwrap();
            *flushed_lsn = last_record.lsn;
        }
        
        buffer.clear();
        Ok(())
    }
    
    /// Force flush the buffer to disk
    #[allow(dead_code)]
    pub fn flush(&self) -> Result<()> {
        let mut buffer = self.buffer.lock().unwrap();
        self.flush_buffer_internal(&mut buffer)
    }
    
    /// Get the last flushed LSN
    #[allow(dead_code)]
    pub fn get_flushed_lsn(&self) -> LSN {
        *self.flushed_lsn.lock().unwrap()
    }
    
    /// Get the next LSN to be assigned
    #[allow(dead_code)]
    pub fn get_next_lsn(&self) -> LSN {
        *self.next_lsn.lock().unwrap()
    }
    
    /// Create a checkpoint
    /// 
    /// A checkpoint marks a point in the log from which recovery can start
    #[allow(dead_code)]
    pub fn checkpoint(&self) -> Result<LSN> {
        // Flush any buffered records first
        self.flush()?;
        
        let lsn = {
            let mut next_lsn = self.next_lsn.lock().unwrap();
            let lsn = *next_lsn;
            *next_lsn += 1;
            lsn
        };
        
        let checkpoint_record = WALRecord::new(lsn, 0, WALRecordType::Checkpoint);
        
        // Write checkpoint record directly
        let mut file = self.file.lock().unwrap();
        let bytes = checkpoint_record.to_bytes()?;
        let length = bytes.len() as u32;
        
        file.write_all(&length.to_be_bytes())?;
        file.write_all(&bytes)?;
        file.flush()?;
        
        // Update checkpoint LSN
        let mut checkpoint_lsn = self.checkpoint_lsn.lock().unwrap();
        *checkpoint_lsn = lsn;
        
        Ok(lsn)
    }
    
    /// Get the last checkpoint LSN
    #[allow(dead_code)]
    pub fn get_checkpoint_lsn(&self) -> LSN {
        *self.checkpoint_lsn.lock().unwrap()
    }
    
    /// Read all WAL records from the file
    #[allow(dead_code)]
    pub fn read_all_records(&self) -> Result<Vec<WALRecord>> {
        let mut file = self.file.lock().unwrap();
        file.seek(SeekFrom::Start(0))?;
        
        let mut records = Vec::new();
        
        loop {
            // Read record length
            let mut length_bytes = [0u8; 4];
            match file.read_exact(&mut length_bytes) {
                Ok(_) => {},
                Err(ref e) if e.kind() == std::io::ErrorKind::UnexpectedEof => break,
                Err(e) => return Err(WALError::Io(e)),
            }
            
            let length = u32::from_be_bytes(length_bytes) as usize;
            
            // Read record data
            let mut record_bytes = vec![0u8; length];
            file.read_exact(&mut record_bytes)?;
            
            let record = WALRecord::from_bytes(&record_bytes)?;
            records.push(record);
        }
        
        Ok(records)
    }
    
    /// ARIES Analysis Phase
    /// 
    /// Reconstructs the state of transactions and dirty pages at the time of crash
    #[allow(dead_code)]
    pub fn analysis_phase(&self) -> Result<ARIESState> {
        let records = self.read_all_records()?;
        let checkpoint_lsn = self.get_checkpoint_lsn();
        
        let mut committed_transactions: HashSet<u64> = HashSet::new();
        let mut active_transactions: HashSet<u64> = HashSet::new();
        let mut dirty_pages: HashSet<u32> = HashSet::new();
        
        // Start from checkpoint or beginning
        let start_idx = records.iter()
            .position(|r| r.lsn == checkpoint_lsn)
            .unwrap_or(0);
        
        for record in &records[start_idx..] {
            match record.record_type {
                WALRecordType::Begin => {
                    active_transactions.insert(record.transaction_id);
                }
                WALRecordType::Commit => {
                    active_transactions.remove(&record.transaction_id);
                    committed_transactions.insert(record.transaction_id);
                }
                WALRecordType::Abort => {
                    active_transactions.remove(&record.transaction_id);
                }
                WALRecordType::Insert | WALRecordType::Update | WALRecordType::Delete => {
                    if let Some(page_id) = record.page_id {
                        dirty_pages.insert(page_id);
                    }
                }
                _ => {}
            }
        }
        
        Ok(ARIESState {
            committed_transactions,
            active_transactions,
            dirty_pages,
            last_lsn: records.last().map(|r| r.lsn).unwrap_or(0),
        })
    }
    
    /// ARIES Redo Phase
    /// 
    /// Replays log records to restore the database state
    #[allow(dead_code)]
    pub fn redo_phase(&self, state: &ARIESState) -> Result<Vec<WALRecord>> {
        let records = self.read_all_records()?;
        let mut redo_records = Vec::new();
        
        // Find the starting point (after checkpoint)
        let start_idx = records.iter()
            .position(|r| r.lsn == state.last_lsn)
            .unwrap_or(0);
        
        for record in &records[start_idx..] {
            match record.record_type {
                WALRecordType::Insert | WALRecordType::Update | WALRecordType::Delete => {
                    // Only redo if page is in dirty page table
                    if let Some(page_id) = record.page_id {
                        if state.dirty_pages.contains(&page_id) {
                            redo_records.push(record.clone());
                        }
                    }
                }
                _ => {}
            }
        }
        
        Ok(redo_records)
    }
    
    /// ARIES Undo Phase
    /// 
    /// Rolls back transactions that were active at the time of crash
    #[allow(dead_code)]
    pub fn undo_phase(&self, state: &ARIESState) -> Result<Vec<WALRecord>> {
        let records = self.read_all_records()?;
        let mut undo_records = Vec::new();
        
        // Process records in reverse order
        for record in records.iter().rev() {
            // Only undo records from active transactions
            if state.active_transactions.contains(&record.transaction_id) {
                match record.record_type {
                    WALRecordType::Insert | WALRecordType::Update | WALRecordType::Delete => {
                        undo_records.push(record.clone());
                    }
                    _ => {}
                }
            }
        }
        
        Ok(undo_records)
    }
    
    /// Close the WAL manager and ensure all records are flushed
    #[allow(dead_code)]
    pub fn close(&self) -> Result<()> {
        self.flush()?;
        Ok(())
    }
}

#[allow(dead_code)]
impl Drop for WALManager {
    fn drop(&mut self) {
        // Ensure all records are flushed when the manager is dropped
        let _ = self.flush();
    }
}

/// ARIES recovery state
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct ARIESState {
    /// Committed transactions
    pub committed_transactions: HashSet<u64>,
    /// Active (uncommitted) transactions at crash time
    pub active_transactions: HashSet<u64>,
    /// Dirty pages that need to be flushed
    pub dirty_pages: HashSet<u32>,
    /// Last LSN in the log
    pub last_lsn: LSN,
}

#[cfg(test)]
#[allow(dead_code)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;
    use std::collections::HashSet;

    #[test]
    fn test_wal_manager_creation() {
        let temp_file = NamedTempFile::new().unwrap();
        let wm = WALManager::with_default_size(temp_file.path()).unwrap();
        
        assert_eq!(wm.get_next_lsn(), 1);
        assert_eq!(wm.get_flushed_lsn(), 0);
    }

    #[test]
    fn test_append_record() {
        let temp_file = NamedTempFile::new().unwrap();
        let wm = WALManager::with_default_size(temp_file.path()).unwrap();
        
        let record = WALRecord::new(0, 1, WALRecordType::Begin);
        let lsn = wm.append_record(record).unwrap();
        
        assert_eq!(lsn, 1);
        assert_eq!(wm.get_next_lsn(), 2);
    }

    #[test]
    fn test_record_serialization() {
        let record = WALRecord::new(1, 100, WALRecordType::Insert)
            .with_page_id(5)
            .with_after_image(vec![1, 2, 3, 4]);
        
        let bytes = record.to_bytes().unwrap();
        let restored = WALRecord::from_bytes(&bytes).unwrap();
        
        assert_eq!(restored.lsn, 1);
        assert_eq!(restored.transaction_id, 100);
        assert_eq!(restored.record_type, WALRecordType::Insert);
        assert_eq!(restored.page_id, Some(5));
        assert_eq!(restored.after_image, Some(vec![1, 2, 3, 4]));
    }

    #[test]
    fn test_flush() {
        let temp_file = NamedTempFile::new().unwrap();
        let wm = WALManager::with_default_size(temp_file.path()).unwrap();
        
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Begin)).unwrap();
        wm.flush().unwrap();
        
        assert_eq!(wm.get_flushed_lsn(), 1);
    }

    #[test]
    fn test_checkpoint() {
        let temp_file = NamedTempFile::new().unwrap();
        let wm = WALManager::with_default_size(temp_file.path()).unwrap();
        
        let lsn = wm.checkpoint().unwrap();
        assert_eq!(wm.get_checkpoint_lsn(), lsn);
    }

    #[test]
    fn test_analysis_phase() {
        let temp_file = NamedTempFile::new().unwrap();
        let wm = WALManager::with_default_size(temp_file.path()).unwrap();
        
        // Simulate a transaction
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Begin)).unwrap();
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Insert).with_page_id(10)).unwrap();
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Commit)).unwrap();
        wm.flush().unwrap();
        
        let state = wm.analysis_phase().unwrap();
        assert!(state.committed_transactions.contains(&1));
        assert!(!state.active_transactions.contains(&1));
        assert!(state.dirty_pages.contains(&10));
    }

    #[test]
    fn test_buffer_flushing() {
        let temp_file = NamedTempFile::new().unwrap();
        let wm = WALManager::new(temp_file.path(), 3).unwrap(); // Small buffer
        
        // Add records (should flush after 3)
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Begin)).unwrap();
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Insert)).unwrap();
        wm.append_record(WALRecord::new(0, 1, WALRecordType::Commit)).unwrap();
        
        // Should have flushed
        assert_eq!(wm.get_flushed_lsn(), 3);
    }
}
