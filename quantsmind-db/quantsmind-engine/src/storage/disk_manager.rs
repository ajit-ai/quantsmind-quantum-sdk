use std::fs::{File, OpenOptions};
use std::io::{Read, Write, Seek, SeekFrom};
use std::path::Path;
use std::sync::{Arc, Mutex};
use crate::storage::{PageId, PAGE_SIZE};
use thiserror::Error;

/// Errors that can occur during disk operations
#[derive(Error, Debug)]
pub enum DiskManagerError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Invalid page ID: {0}")]
    InvalidPageId(PageId),
    
    #[error("Page overflow: page {0} exceeds file size")]
    PageOverflow(PageId),
    
    #[error("File not found: {0}")]
    FileNotFound(String),
}

/// Result type for disk operations
pub type Result<T> = std::result::Result<T, DiskManagerError>;

/// Disk Manager - Handles low-level file I/O operations for database pages
/// 
/// Responsibilities:
/// - Read and write 8KB pages to disk
/// - Allocate new pages by extending the file
/// - Maintain a free-list bitmap for recycling deleted pages
/// - Thread-safe operations using Arc<Mutex>
pub struct DiskManager {
    /// The database file handle
    file: Arc<Mutex<File>>,
    /// Path to the database file
    file_path: String,
    /// Number of pages currently allocated in the file
    num_pages: Arc<Mutex<u32>>,
    /// Free-list of deleted page IDs that can be reused
    free_list: Arc<Mutex<Vec<PageId>>>,
}

impl DiskManager {
    /// Create a new DiskManager with the specified database file
    /// 
    /// If the file doesn't exist, it will be created.
    /// If it exists, the existing pages will be counted.
    pub fn new<P: AsRef<Path>>(file_path: P) -> Result<Self> {
        let path = file_path.as_ref().to_string_lossy().to_string();
        
        // Open or create the file
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open(&path)?;
        
        // Calculate number of existing pages
        let metadata = file.metadata()?;
        let file_size = metadata.len();
        let num_pages = (file_size / PAGE_SIZE as u64) as u32;
        
        Ok(DiskManager {
            file: Arc::new(Mutex::new(file)),
            file_path: path,
            num_pages: Arc::new(Mutex::new(num_pages)),
            free_list: Arc::new(Mutex::new(Vec::new())),
        })
    }

    /// Get the file path
    pub fn get_file_path(&self) -> &str {
        &self.file_path
    }

    /// Read a page from disk
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to read
    /// 
    /// # Returns
    /// * The page data as a fixed-size array of PAGE_SIZE bytes
    pub fn read_page(&self, page_id: PageId) -> Result<[u8; PAGE_SIZE]> {
        let mut file = self.file.lock().unwrap();
        let num_pages = *self.num_pages.lock().unwrap();
        
        // Validate page ID
        if page_id == 0 || page_id > num_pages {
            return Err(DiskManagerError::InvalidPageId(page_id));
        }
        
        // Seek to the page position
        let offset = (page_id - 1) as u64 * PAGE_SIZE as u64;
        file.seek(SeekFrom::Start(offset))?;
        
        // Read the page data
        let mut buffer = [0u8; PAGE_SIZE];
        file.read_exact(&mut buffer)?;
        
        Ok(buffer)
    }

    /// Write a page to disk
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to write
    /// * `data` - The page data to write (must be exactly PAGE_SIZE bytes)
    pub fn write_page(&self, page_id: PageId, data: &[u8; PAGE_SIZE]) -> Result<()> {
        let mut file = self.file.lock().unwrap();
        let num_pages = *self.num_pages.lock().unwrap();
        
        // Validate page ID
        if page_id == 0 || page_id > num_pages {
            return Err(DiskManagerError::InvalidPageId(page_id));
        }
        
        // Seek to the page position
        let offset = (page_id - 1) as u64 * PAGE_SIZE as u64;
        file.seek(SeekFrom::Start(offset))?;
        
        // Write the page data
        file.write_all(data)?;
        file.flush()?; // Ensure data is written to disk
        
        Ok(())
    }

    /// Allocate a new page
    /// 
    /// First checks the free-list for reusable pages.
    /// If no free pages, extends the file by one page.
    /// 
    /// # Returns
    /// * The newly allocated page ID
    pub fn allocate_page(&self) -> Result<PageId> {
        // First, try to reuse a page from the free-list
        {
            let mut free_list = self.free_list.lock().unwrap();
            if let Some(page_id) = free_list.pop() {
                return Ok(page_id);
            }
        }
        
        // No free pages, allocate a new one by extending the file
        let mut num_pages = self.num_pages.lock().unwrap();
        let new_page_id = *num_pages + 1;
        
        let mut file = self.file.lock().unwrap();
        
        // Seek to the end of the file + one page size
        let offset = (*num_pages as u64) * PAGE_SIZE as u64;
        file.seek(SeekFrom::Start(offset))?;
        
        // Write a zero-filled page
        let zero_page = [0u8; PAGE_SIZE];
        file.write_all(&zero_page)?;
        file.flush()?;
        
        // Update page count
        *num_pages = new_page_id;
        
        Ok(new_page_id)
    }

    /// Deallocate a page (add to free-list for reuse)
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to deallocate
    pub fn deallocate_page(&self, page_id: PageId) -> Result<()> {
        let num_pages = *self.num_pages.lock().unwrap();
        
        // Validate page ID
        if page_id == 0 || page_id > num_pages {
            return Err(DiskManagerError::InvalidPageId(page_id));
        }
        
        // Add to free-list
        let mut free_list = self.free_list.lock().unwrap();
        free_list.push(page_id);
        
        Ok(())
    }

    /// Get the total number of allocated pages
    pub fn get_num_pages(&self) -> u32 {
        *self.num_pages.lock().unwrap()
    }

    /// Get the number of pages in the free-list
    pub fn get_free_list_count(&self) -> usize {
        self.free_list.lock().unwrap().len()
    }

    /// Flush all buffered writes to disk
    pub fn flush(&self) -> Result<()> {
        let mut file = self.file.lock().unwrap();
        file.flush()?;
        Ok(())
    }

    /// Sync the file to ensure all writes are persisted
    pub fn sync(&self) -> Result<()> {
        let file = self.file.lock().unwrap();
        file.sync_all()?;
        Ok(())
    }

    /// Close the disk manager and release resources
    pub fn close(&self) -> Result<()> {
        self.flush()?;
        self.sync()?;
        Ok(())
    }
}

impl Drop for DiskManager {
    fn drop(&mut self) {
        // Ensure all data is flushed when the manager is dropped
        let _ = self.flush();
        let _ = self.sync();
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use tempfile::NamedTempFile;

    #[test]
    fn test_disk_manager_creation() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        assert_eq!(dm.get_num_pages(), 0);
        assert_eq!(dm.get_free_list_count(), 0);
    }

    #[test]
    fn test_page_allocation() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        let page_id1 = dm.allocate_page().unwrap();
        assert_eq!(page_id1, 1);
        assert_eq!(dm.get_num_pages(), 1);
        
        let page_id2 = dm.allocate_page().unwrap();
        assert_eq!(page_id2, 2);
        assert_eq!(dm.get_num_pages(), 2);
    }

    #[test]
    fn test_page_write_and_read() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        let page_id = dm.allocate_page().unwrap();
        
        // Create test data
        let mut test_data = [0u8; PAGE_SIZE];
        test_data[0..4].copy_from_slice(&1234u32.to_be_bytes());
        test_data[100..104].copy_from_slice(&5678u32.to_be_bytes());
        
        // Write the page
        dm.write_page(page_id, &test_data).unwrap();
        
        // Read the page back
        let read_data = dm.read_page(page_id).unwrap();
        
        assert_eq!(read_data, test_data);
    }

    #[test]
    fn test_page_deallocation_and_reuse() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        // Allocate 3 pages
        let page_id1 = dm.allocate_page().unwrap();
        let page_id2 = dm.allocate_page().unwrap();
        let page_id3 = dm.allocate_page().unwrap();
        
        assert_eq!(dm.get_num_pages(), 3);
        
        // Deallocate page 2
        dm.deallocate_page(page_id2).unwrap();
        assert_eq!(dm.get_free_list_count(), 1);
        
        // Next allocation should reuse page 2
        let reused_page_id = dm.allocate_page().unwrap();
        assert_eq!(reused_page_id, page_id2);
        assert_eq!(dm.get_free_list_count(), 0);
        assert_eq!(dm.get_num_pages(), 3); // Total pages should not increase
    }

    #[test]
    fn test_invalid_page_read() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        // Try to read a page that doesn't exist
        let result = dm.read_page(999);
        assert!(result.is_err());
    }

    #[test]
    fn test_invalid_page_write() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        let test_data = [0u8; PAGE_SIZE];
        
        // Try to write to a page that doesn't exist
        let result = dm.write_page(999, &test_data);
        assert!(result.is_err());
    }

    #[test]
    fn test_multiple_pages() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = DiskManager::new(temp_file.path()).unwrap();
        
        // Allocate and write 10 pages
        for i in 1..=10 {
            let page_id = dm.allocate_page().unwrap();
            assert_eq!(page_id, i);
            
            let mut test_data = [0u8; PAGE_SIZE];
            test_data[0..4].copy_from_slice(&(i as u32).to_be_bytes());
            dm.write_page(page_id, &test_data).unwrap();
        }
        
        // Read back and verify
        for i in 1..=10 {
            let read_data = dm.read_page(i).unwrap();
            let value = u32::from_be_bytes(read_data[0..4].try_into().unwrap());
            assert_eq!(value, i);
        }
    }

    #[test]
    fn test_file_persistence() {
        let temp_file = NamedTempFile::new().unwrap();
        let path = temp_file.path().to_path_buf();
        
        {
            // Create disk manager and write data
            let dm = DiskManager::new(&path).unwrap();
            let page_id = dm.allocate_page().unwrap();
            
            let mut test_data = [0u8; PAGE_SIZE];
            test_data[0..8].copy_from_slice(&0xDEADBEEFCAFEBABEu64.to_be_bytes());
            dm.write_page(page_id, &test_data).unwrap();
        } // dm is dropped here
        
        // Reopen the file and verify data persists
        let dm = DiskManager::new(&path).unwrap();
        assert_eq!(dm.get_num_pages(), 1);
        
        let read_data = dm.read_page(1).unwrap();
        let value = u64::from_be_bytes(read_data[0..8].try_into().unwrap());
        assert_eq!(value, 0xDEADBEEFCAFEBABE);
    }
}
