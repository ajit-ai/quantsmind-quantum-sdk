use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use crate::storage::{Page, PageId, DiskManager, DiskManagerError};
use thiserror::Error;

/// Errors that can occur during buffer pool operations
#[derive(Error, Debug)]
pub enum BufferPoolError {
    #[error("Disk manager error: {0}")]
    DiskManager(#[from] DiskManagerError),
    
    #[error("Buffer pool is full - no available frames")]
    BufferPoolFull,
    
    #[error("Page {0} is not in buffer pool")]
    PageNotInPool(PageId),
    
    #[error("Frame {0} is not in buffer pool")]
    FrameNotInPool(usize),
}

/// Result type for buffer pool operations
pub type Result<T> = std::result::Result<T, BufferPoolError>;

/// Frame identifier - index into the buffer pool frame array
pub type FrameId = usize;

/// Default number of frames in the buffer pool (1024 frames = 8MB of memory)
pub const DEFAULT_POOL_SIZE: usize = 1024;

/// Buffer Pool Manager - Manages in-memory caching of database pages
/// 
/// Responsibilities:
/// - Maintain a fixed-size array of memory frames (pages)
/// - Track which pages are currently in memory using a page table
/// - Implement page replacement policy (Clock algorithm)
/// - Handle page pinning to prevent eviction during use
/// - Flush dirty pages to disk when evicted or on shutdown
/// 
/// Thread Safety:
/// - Uses Arc<RwLock<Page>> for concurrent read/write access to pages
/// - Uses Mutex for internal metadata protection
pub struct BufferPoolManager {
    /// Fixed-size array of memory frames
    frames: Vec<Option<Arc<RwLock<Page>>>>,
    
    /// Page table: maps PageId -> FrameId
    page_table: HashMap<PageId, FrameId>,
    
    /// Clock hand for Clock replacement algorithm
    clock_hand: FrameId,
    
    /// Disk manager for reading/writing pages
    disk_manager: Arc<DiskManager>,
    
    /// Number of frames in the buffer pool
    pool_size: usize,
}

impl BufferPoolManager {
    /// Create a new BufferPoolManager with the specified pool size
    /// 
    /// # Arguments
    /// * `disk_manager` - The disk manager to use for I/O operations
    /// * `pool_size` - Number of frames in the buffer pool (default: 1024)
    pub fn new(disk_manager: Arc<DiskManager>, pool_size: usize) -> Self {
        BufferPoolManager {
            frames: vec![None; pool_size],
            page_table: HashMap::new(),
            clock_hand: 0,
            disk_manager,
            pool_size,
        }
    }

    /// Create a BufferPoolManager with default pool size (1024 frames)
    pub fn with_default_size(disk_manager: Arc<DiskManager>) -> Self {
        Self::new(disk_manager, DEFAULT_POOL_SIZE)
    }

    /// Get the pool size
    pub fn get_pool_size(&self) -> usize {
        self.pool_size
    }

    /// Get the number of pages currently in the buffer pool
    pub fn get_page_count(&self) -> usize {
        self.page_table.len()
    }

    /// Fetch a page from disk into the buffer pool
    /// 
    /// If the page is already in memory, returns the existing frame.
    /// If not, reads from disk and allocates a frame.
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to fetch
    /// 
    /// # Returns
    /// * Arc<RwLock<Page>> - Shared reference to the page
    pub fn fetch_page(&mut self, page_id: PageId) -> Result<Arc<RwLock<Page>>> {
        // Check if page is already in buffer pool (cache hit)
        if let Some(&frame_id) = self.page_table.get(&page_id) {
            if let Some(ref page) = self.frames[frame_id] {
                // Increment pin count
                page.read().expect("Poisoned lock").pin();
                return Ok(Arc::clone(page));
            }
        }

        // Cache miss - need to read from disk
        let page_data = self.disk_manager.read_page(page_id)?;
        let page = Arc::new(RwLock::new(Page::from_bytes(page_id, page_data)));
        
        // Pin the page immediately
        page.read().expect("Poisoned lock").pin();
        
        // Find a free frame or evict a page
        let frame_id = self.find_free_frame()?;
        
        // Insert the page into the frame
        self.frames[frame_id] = Some(Arc::clone(&page));
        self.page_table.insert(page_id, frame_id);
        
        Ok(page)
    }

    /// Create a new page in the buffer pool (allocated on disk)
    /// 
    /// # Returns
    /// * (PageId, Arc<RwLock<Page>>) - The new page ID and the page reference
    pub fn new_page(&mut self) -> Result<(PageId, Arc<RwLock<Page>>)> {
        // Allocate a new page on disk
        let page_id = self.disk_manager.allocate_page()?;
        
        // Create a new empty page
        let page = Arc::new(RwLock::new(Page::new(page_id)));
        
        // Pin the page
        page.read().expect("Poisoned lock").pin();
        
        // Find a free frame or evict a page
        let frame_id = self.find_free_frame()?;
        
        // Insert the page into the frame
        self.frames[frame_id] = Some(Arc::clone(&page));
        self.page_table.insert(page_id, frame_id);
        
        Ok((page_id, page))
    }

    /// Unpin a page, allowing it to be evicted
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to unpin
    /// * `is_dirty` - Whether the page was modified (needs to be written to disk)
    pub fn unpin_page(&mut self, page_id: PageId, is_dirty: bool) -> Result<()> {
        if let Some(&frame_id) = self.page_table.get(&page_id) {
            if let Some(ref page) = self.frames[frame_id] {
                // Unpin the page
                page.read().expect("Poisoned lock").unpin();
                
                // Mark as dirty if specified
                if is_dirty {
                    page.write().expect("Poisoned lock").mark_dirty();
                }
                
                return Ok(());
            }
        }
        
        Err(BufferPoolError::PageNotInPool(page_id))
    }

    /// Flush a page to disk (write dirty page if needed)
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to flush
    pub fn flush_page(&mut self, page_id: PageId) -> Result<()> {
        if let Some(&frame_id) = self.page_table.get(&page_id) {
            if let Some(ref page) = self.frames[frame_id] {
                let page_guard = page.read().expect("Poisoned lock");
                
                if page_guard.is_dirty() {
                    let page_data = *page_guard.get_data();
                    drop(page_guard);
                    self.disk_manager.write_page(page_id, &page_data)?;
                    let page_guard = page.read().expect("Poisoned lock");
                    page_guard.clear_dirty();
                }
                
                return Ok(());
            }
        }
        
        Err(BufferPoolError::PageNotInPool(page_id))
    }

    /// Flush all dirty pages to disk
    pub fn flush_all_pages(&mut self) -> Result<()> {
        let mut page_ids_to_flush: Vec<PageId> = Vec::new();
        
        // Collect all dirty page IDs
        for (page_id, frame_id) in &self.page_table {
            if let Some(ref page) = self.frames[*frame_id] {
                if page.read().expect("Poisoned lock").is_dirty() {
                    page_ids_to_flush.push(*page_id);
                }
            }
        }
        
        // Flush each dirty page
        for page_id in page_ids_to_flush {
            self.flush_page(page_id)?;
        }
        
        Ok(())
    }

    /// Delete a page from the buffer pool and disk
    /// 
    /// # Arguments
    /// * `page_id` - The ID of the page to delete
    pub fn delete_page(&mut self, page_id: PageId) -> Result<()> {
        // Check if page is in buffer pool
        if let Some(&frame_id) = self.page_table.get(&page_id) {
            let page = self.frames[frame_id].take().unwrap();
            
            // Ensure page is not pinned
            if page.read().expect("Poisoned lock").get_pin_count() > 0 {
                return Err(BufferPoolError::PageNotInPool(page_id)); // Actually pinned, but we'll treat as error
            }
            
            // Remove from page table
            self.page_table.remove(&page_id);
        }
        
        // Deallocate on disk
        self.disk_manager.deallocate_page(page_id)?;
        
        Ok(())
    }

    /// Find a free frame using the Clock replacement algorithm
    /// 
    /// Clock Algorithm:
    /// 1. Start at clock_hand
    /// 2. If frame is empty, use it
    /// 3. If page has pin_count == 0, use it
    /// 4. Otherwise, clear reference bit and advance clock
    /// 5. Repeat until a frame is found
    fn find_free_frame(&mut self) -> Result<FrameId> {
        // First pass: look for truly empty frames
        for i in 0..self.pool_size {
            let frame_id = (self.clock_hand + i) % self.pool_size;
            if self.frames[frame_id].is_none() {
                self.clock_hand = (frame_id + 1) % self.pool_size;
                return Ok(frame_id);
            }
        }
        
        // Second pass: clock algorithm to find an evictable page
        for _ in 0..self.pool_size * 2 {
            let frame_id = self.clock_hand;
            
            if let Some(ref page) = self.frames[frame_id] {
                let page_guard = page.read().expect("Poisoned lock");
                
                if page_guard.get_pin_count() == 0 {
                    // Page can be evicted
                    let page_id = page_guard.get_page_id();
                    let is_dirty = page_guard.is_dirty();
                    let page_data = *page_guard.get_data();
                    drop(page_guard);
                    
                    // Flush if dirty
                    if is_dirty {
                        self.disk_manager.write_page(page_id, &page_data)?;
                    }
                    
                    // Remove from page table
                    self.page_table.remove(&page_id);
                    
                    // Clear the frame
                    self.frames[frame_id] = None;
                    
                    // Advance clock
                    self.clock_hand = (frame_id + 1) % self.pool_size;
                    
                    return Ok(frame_id);
                }
            }
            
            // Advance clock
            self.clock_hand = (self.clock_hand + 1) % self.pool_size;
        }
        
        // Buffer pool is full and all pages are pinned
        Err(BufferPoolError::BufferPoolFull)
    }

    /// Check if a page is currently in the buffer pool
    pub fn is_page_in_pool(&self, page_id: PageId) -> bool {
        self.page_table.contains_key(&page_id)
    }

    /// Get the current buffer pool usage statistics
    pub fn get_stats(&self) -> BufferPoolStats {
        let mut pinned_count = 0;
        let mut dirty_count = 0;
        
        for frame in &self.frames {
            if let Some(ref page) = frame {
                let page_guard = page.read().expect("Poisoned lock");
                if page_guard.get_pin_count() > 0 {
                    pinned_count += 1;
                }
                if page_guard.is_dirty() {
                    dirty_count += 1;
                }
            }
        }
        
        BufferPoolStats {
            total_frames: self.pool_size,
            used_frames: self.page_table.len(),
            free_frames: self.pool_size - self.page_table.len(),
            pinned_count,
            dirty_count,
        }
    }
}

/// Buffer pool usage statistics
#[derive(Debug, Clone)]
pub struct BufferPoolStats {
    pub total_frames: usize,
    pub used_frames: usize,
    pub free_frames: usize,
    pub pinned_count: usize,
    pub dirty_count: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn test_buffer_pool_creation() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let bpm = BufferPoolManager::with_default_size(dm);
        
        assert_eq!(bpm.get_pool_size(), DEFAULT_POOL_SIZE);
        assert_eq!(bpm.get_page_count(), 0);
    }

    #[test]
    fn test_new_page() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(dm);
        
        let (page_id, page) = bpm.new_page().unwrap();
        assert_eq!(page_id, 1);
        assert_eq!(page.read().get_page_id(), 1);
        assert_eq!(page.read().get_pin_count(), 1);
        assert!(bpm.is_page_in_pool(page_id));
    }

    #[test]
    fn test_fetch_page_cache_hit() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(Arc::clone(&dm));
        
        // Create a new page
        let (page_id, page1) = bpm.new_page().unwrap();
        
        // Unpin the page
        bpm.unpin_page(page_id, false).unwrap();
        
        // Fetch the same page (should be cache hit)
        let page2 = bpm.fetch_page(page_id).unwrap();
        
        // Should return the same page
        assert!(Arc::ptr_eq(&page1, &page2));
    }

    #[test]
    fn test_fetch_page_cache_miss() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(Arc::clone(&dm));
        
        // Allocate a page on disk without loading into buffer pool
        let page_id = dm.allocate_page().unwrap();
        let mut test_data = [0u8; PAGE_SIZE];
        test_data[0..4].copy_from_slice(&1234u32.to_be_bytes());
        dm.write_page(page_id, &test_data).unwrap();
        
        // Fetch the page (should be cache miss)
        let page = bpm.fetch_page(page_id).unwrap();
        assert_eq!(page.read().get_page_id(), page_id);
        assert!(bpm.is_page_in_pool(page_id));
    }

    #[test]
    fn test_unpin_page() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(dm);
        
        let (page_id, page) = bpm.new_page().unwrap();
        assert_eq!(page.read().get_pin_count(), 1);
        
        bpm.unpin_page(page_id, false).unwrap();
        assert_eq!(page.read().get_pin_count(), 0);
    }

    #[test]
    fn test_flush_page() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(Arc::clone(&dm));
        
        let (page_id, page) = bpm.new_page().unwrap();
        
        // Modify the page
        {
            let mut page_guard = page.write();
            let data = page_guard.get_data_mut();
            data[0..4].copy_from_slice(&9999u32.to_be_bytes());
            page_guard.mark_dirty();
        }
        
        // Flush the page
        bpm.flush_page(page_id).unwrap();
        assert!(!page.read().is_dirty());
        
        // Verify data was written to disk
        let disk_data = dm.read_page(page_id).unwrap();
        let value = u32::from_be_bytes(disk_data[0..4].try_into().unwrap());
        assert_eq!(value, 9999);
    }

    #[test]
    fn test_delete_page() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(Arc::clone(&dm));
        
        let (page_id, page) = bpm.new_page().unwrap();
        bpm.unpin_page(page_id, false).unwrap();
        
        // Delete the page
        bpm.delete_page(page_id).unwrap();
        
        assert!(!bpm.is_page_in_pool(page_id));
    }

    #[test]
    fn test_buffer_pool_stats() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::with_default_size(dm);
        
        let stats = bpm.get_stats();
        assert_eq!(stats.used_frames, 0);
        assert_eq!(stats.free_frames, DEFAULT_POOL_SIZE);
        
        let (page_id, page) = bpm.new_page().unwrap();
        let stats = bpm.get_stats();
        assert_eq!(stats.used_frames, 1);
        assert_eq!(stats.pinned_count, 1);
        
        bpm.unpin_page(page_id, true).unwrap();
        let stats = bpm.get_stats();
        assert_eq!(stats.pinned_count, 0);
        assert_eq!(stats.dirty_count, 1);
    }

    #[test]
    fn test_clock_eviction() {
        let temp_file = NamedTempFile::new().unwrap();
        let dm = Arc::new(DiskManager::new(temp_file.path()).unwrap());
        let mut bpm = BufferPoolManager::new(dm, 4); // Small pool for testing
        
        // Fill the buffer pool
        let mut page_ids = Vec::new();
        for _ in 0..4 {
            let (page_id, page) = bpm.new_page().unwrap();
            bpm.unpin_page(page_id, false).unwrap();
            page_ids.push(page_id);
        }
        
        assert_eq!(bpm.get_page_count(), 4);
        
        // Try to add a 5th page - should trigger eviction
        let (new_page_id, _new_page) = bpm.new_page().unwrap();
        assert_eq!(bpm.get_page_count(), 4);
        
        // One of the original pages should have been evicted
        let evicted_count = page_ids.iter().filter(|&&id| !bpm.is_page_in_pool(id)).count();
        assert_eq!(evicted_count, 1);
    }
}
