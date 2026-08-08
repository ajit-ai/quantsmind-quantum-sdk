use std::sync::atomic::{AtomicU32, AtomicBool, Ordering};
use serde::{Serialize, Deserialize};

/// Page identifier - 32-bit unsigned integer
pub type PageId = u32;

/// Fixed page size of 8KB (8192 bytes) - standard database page size
pub const PAGE_SIZE: usize = 8192;

/// Page header size in bytes (32 bytes total)
pub const PAGE_HEADER_SIZE: usize = 32;

/// Slot entry size in bytes (offset: u16, length: u16)
pub const SLOT_ENTRY_SIZE: usize = 4;

/// Maximum number of slots per page (conservative estimate)
pub const MAX_SLOTS: usize = (PAGE_SIZE - PAGE_HEADER_SIZE) / SLOT_ENTRY_SIZE;

/// Page header structure - 32 bytes at the start of each page
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct PageHeader {
    /// Unique page identifier
    pub page_id: PageId,
    /// Log Sequence Number for WAL recovery
    pub lsn: u64,
    /// Number of active slots in the page
    pub slot_count: u16,
    /// Pointer to free space from the end of page (grows backward)
    pub free_space_pointer: u16,
    /// Page flags (e.g., is_leaf, is_dirty)
    pub flags: u16,
}

impl PageHeader {
    /// Create a new page header with default values
    pub fn new(page_id: PageId) -> Self {
        PageHeader {
            page_id,
            lsn: 0,
            slot_count: 0,
            free_space_pointer: PAGE_SIZE as u16,
            flags: 0,
        }
    }

    /// Serialize header to bytes
    pub fn to_bytes(&self) -> [u8; PAGE_HEADER_SIZE] {
        let mut bytes = [0u8; PAGE_HEADER_SIZE];
        bytes[0..4].copy_from_slice(&self.page_id.to_be_bytes());
        bytes[4..12].copy_from_slice(&self.lsn.to_be_bytes());
        bytes[12..14].copy_from_slice(&self.slot_count.to_be_bytes());
        bytes[14..16].copy_from_slice(&self.free_space_pointer.to_be_bytes());
        bytes[16..18].copy_from_slice(&self.flags.to_be_bytes());
        bytes
    }

    /// Deserialize header from bytes
    pub fn from_bytes(bytes: &[u8]) -> Self {
        PageHeader {
            page_id: u32::from_be_bytes(bytes[0..4].try_into().unwrap()),
            lsn: u64::from_be_bytes(bytes[4..12].try_into().unwrap()),
            slot_count: u16::from_be_bytes(bytes[12..14].try_into().unwrap()),
            free_space_pointer: u16::from_be_bytes(bytes[14..16].try_into().unwrap()),
            flags: u16::from_be_bytes(bytes[16..18].try_into().unwrap()),
        }
    }
}

/// Slot entry - points to actual tuple data within the page
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct Slot {
    /// Offset from start of page where tuple data begins
    pub offset: u16,
    /// Length of the tuple data in bytes
    pub length: u16,
}

impl Slot {
    pub const fn new(offset: u16, length: u16) -> Self {
        Slot { offset, length }
    }

    /// Serialize slot to bytes
    pub fn to_bytes(&self) -> [u8; SLOT_ENTRY_SIZE] {
        let mut bytes = [0u8; SLOT_ENTRY_SIZE];
        bytes[0..2].copy_from_slice(&self.offset.to_be_bytes());
        bytes[2..4].copy_from_slice(&self.length.to_be_bytes());
        bytes
    }

    /// Deserialize slot from bytes
    pub fn from_bytes(bytes: &[u8]) -> Self {
        Slot {
            offset: u16::from_be_bytes(bytes[0..2].try_into().unwrap()),
            length: u16::from_be_bytes(bytes[2..4].try_into().unwrap()),
        }
    }
}

/// Database Page - 8KB fixed-size storage unit with slotted page architecture
/// 
/// Memory layout:
/// - Page Header (32 bytes): page_id, lsn, slot_count, free_space_pointer, flags
/// - Slot Array (grows forward): Array of (offset, length) pointers to tuples
/// - Free Space (shrinks from both ends)
/// - Tuple Data (grows backward): Actual variable-length tuple data
pub struct Page {
    /// Page identifier
    id: PageId,
    /// Pin count for buffer pool management (prevents eviction)
    pin_count: AtomicU32,
    /// Dirty flag - indicates page has been modified and needs to be written
    is_dirty: AtomicBool,
    /// Fixed-size binary buffer representing the 8KB page
    data: [u8; PAGE_SIZE],
}

impl Page {
    /// Create a new empty page
    pub fn new(page_id: PageId) -> Self {
        let mut page = Page {
            id: page_id,
            pin_count: AtomicU32::new(0),
            is_dirty: AtomicBool::new(false),
            data: [0u8; PAGE_SIZE],
        };
        
        // Initialize page header
        let header = PageHeader::new(page_id);
        let header_bytes = header.to_bytes();
        page.data[0..PAGE_HEADER_SIZE].copy_from_slice(&header_bytes);
        
        page
    }

    /// Create a page from existing binary data (loaded from disk)
    pub fn from_bytes(page_id: PageId, data: [u8; PAGE_SIZE]) -> Self {
        Page {
            id: page_id,
            pin_count: AtomicU32::new(0),
            is_dirty: AtomicBool::new(false),
            data,
        }
    }

    /// Get page ID
    pub fn get_page_id(&self) -> PageId {
        self.id
    }

    /// Get the page header
    pub fn get_header(&self) -> PageHeader {
        PageHeader::from_bytes(&self.data[0..PAGE_HEADER_SIZE])
    }

    /// Update the page header
    pub fn set_header(&mut self, header: &PageHeader) {
        let header_bytes = header.to_bytes();
        self.data[0..PAGE_HEADER_SIZE].copy_from_slice(&header_bytes);
        self.mark_dirty();
    }

    /// Get the raw binary data
    pub fn get_data(&self) -> &[u8; PAGE_SIZE] {
        &self.data
    }

    /// Get mutable reference to binary data
    pub fn get_data_mut(&mut self) -> &mut [u8; PAGE_SIZE] {
        &mut self.data
    }

    /// Increment pin count - prevents page from being evicted
    pub fn pin(&self) {
        self.pin_count.fetch_add(1, Ordering::SeqCst);
    }

    /// Decrement pin count - allows page to be evicted if count reaches 0
    pub fn unpin(&self) {
        self.pin_count.fetch_sub(1, Ordering::SeqCst);
    }

    /// Get current pin count
    pub fn get_pin_count(&self) -> u32 {
        self.pin_count.load(Ordering::SeqCst)
    }

    /// Mark page as dirty (modified)
    pub fn mark_dirty(&self) {
        self.is_dirty.store(true, Ordering::SeqCst);
    }

    /// Clear dirty flag (after writing to disk)
    pub fn clear_dirty(&self) {
        self.is_dirty.store(false, Ordering::SeqCst);
    }

    /// Check if page is dirty
    pub fn is_dirty(&self) -> bool {
        self.is_dirty.load(Ordering::SeqCst)
    }

    /// Insert a tuple into the page using slotted page architecture
    /// Returns Some(slot_id) on success, None if page is full
    pub fn insert_tuple(&mut self, tuple_data: &[u8]) -> Option<u16> {
        let header = self.get_header();
        let tuple_len = tuple_data.len() as u16;

        // Calculate required space
        let slot_array_end = PAGE_HEADER_SIZE + (header.slot_count as usize) * SLOT_ENTRY_SIZE;
        let required_space = SLOT_ENTRY_SIZE + tuple_len as usize;

        // Check if we have enough free space
        let free_space = header.free_space_pointer as usize - slot_array_end;
        if free_space < required_space {
            return None; // Page is full
        }

        // Calculate where to insert the tuple data (grow backward from end)
        let new_tuple_offset = header.free_space_pointer - tuple_len;
        
        // Copy tuple data to the page
        let offset_end = header.free_space_pointer as usize;
        let offset_start = new_tuple_offset as usize;
        self.data[offset_start..offset_end].copy_from_slice(tuple_data);

        // Create slot entry
        let slot = Slot::new(new_tuple_offset, tuple_len);
        let slot_bytes = slot.to_bytes();

        // Insert slot entry (grow forward from header)
        let slot_start = PAGE_HEADER_SIZE + (header.slot_count as usize) * SLOT_ENTRY_SIZE;
        let slot_end = slot_start + SLOT_ENTRY_SIZE;
        self.data[slot_start..slot_end].copy_from_slice(&slot_bytes);

        // Update header
        let mut new_header = header.clone();
        new_header.slot_count += 1;
        new_header.free_space_pointer = new_tuple_offset;
        self.set_header(&new_header);

        Some(header.slot_count) // Return the slot ID
    }

    /// Get tuple data by slot ID
    pub fn get_tuple(&self, slot_id: u16) -> Option<Vec<u8>> {
        let header = self.get_header();
        
        if slot_id >= header.slot_count {
            return None;
        }

        // Read slot entry
        let slot_start = PAGE_HEADER_SIZE + (slot_id as usize) * SLOT_ENTRY_SIZE;
        let slot_end = slot_start + SLOT_ENTRY_SIZE;
        let slot = Slot::from_bytes(&self.data[slot_start..slot_end]);

        // Read tuple data
        let tuple_start = slot.offset as usize;
        let tuple_end = tuple_start + slot.length as usize;
        
        if tuple_end > PAGE_SIZE {
            return None; // Invalid tuple data
        }

        Some(self.data[tuple_start..tuple_end].to_vec())
    }

    /// Delete a tuple by slot ID (mark slot as deleted)
    pub fn delete_tuple(&mut self, slot_id: u16) -> bool {
        let header = self.get_header();
        
        if slot_id >= header.slot_count {
            return false;
        }

        // Mark slot as deleted by setting offset to 0 (tombstone)
        let slot_start = PAGE_HEADER_SIZE + (slot_id as usize) * SLOT_ENTRY_SIZE;
        let slot_end = slot_start + SLOT_ENTRY_SIZE;
        let mut slot = Slot::from_bytes(&self.data[slot_start..slot_end]);
        slot.offset = 0; // Tombstone
        let slot_bytes = slot.to_bytes();
        self.data[slot_start..slot_end].copy_from_slice(&slot_bytes);

        self.mark_dirty();
        true
    }

    /// Get available free space in bytes
    pub fn get_free_space(&self) -> usize {
        let header = self.get_header();
        let slot_array_end = PAGE_HEADER_SIZE + (header.slot_count as usize) * SLOT_ENTRY_SIZE;
        header.free_space_pointer as usize - slot_array_end
    }

    /// Iterator over all valid tuples in the page
    pub fn iter_tuples(&self) -> PageTupleIterator<'_> {
        PageTupleIterator {
            page: self,
            current_slot: 0,
        }
    }
}

/// Iterator for tuples in a page
pub struct PageTupleIterator<'a> {
    page: &'a Page,
    current_slot: u16,
}

impl<'a> Iterator for PageTupleIterator<'a> {
    type Item = (u16, Vec<u8>);

    fn next(&mut self) -> Option<Self::Item> {
        let header = self.page.get_header();
        
        while self.current_slot < header.slot_count {
            let slot_id = self.current_slot;
            self.current_slot += 1;

            if let Some(tuple_data) = self.page.get_tuple(slot_id) {
                // Skip tombstones (offset == 0)
                let slot_start = PAGE_HEADER_SIZE + (slot_id as usize) * SLOT_ENTRY_SIZE;
                let slot_end = slot_start + SLOT_ENTRY_SIZE;
                let slot = Slot::from_bytes(&self.page.data[slot_start..slot_end]);
                
                if slot.offset > 0 {
                    return Some((slot_id, tuple_data));
                }
            }
        }
        
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_page_creation() {
        let page = Page::new(1);
        assert_eq!(page.get_page_id(), 1);
        assert_eq!(page.get_pin_count(), 0);
        assert!(!page.is_dirty());
    }

    #[test]
    fn test_page_header_serialization() {
        let header = PageHeader::new(42);
        let bytes = header.to_bytes();
        let restored = PageHeader::from_bytes(&bytes);
        assert_eq!(header.page_id, restored.page_id);
        assert_eq!(header.lsn, restored.lsn);
        assert_eq!(header.slot_count, restored.slot_count);
    }

    #[test]
    fn test_tuple_insertion() {
        let mut page = Page::new(1);
        let tuple_data = b"Hello, World!";
        
        let slot_id = page.insert_tuple(tuple_data);
        assert!(slot_id.is_some());
        
        let retrieved = page.get_tuple(slot_id.unwrap());
        assert_eq!(retrieved, Some(tuple_data.to_vec()));
    }

    #[test]
    fn test_multiple_tuples() {
        let mut page = Page::new(1);
        
        for i in 0..10 {
            let data = format!("Tuple {}", i);
            page.insert_tuple(data.as_bytes());
        }
        
        let header = page.get_header();
        assert_eq!(header.slot_count, 10);
    }

    #[test]
    fn test_page_full() {
        let mut page = Page::new(1);
        let large_data = vec![0u8; 4000]; // Large tuple
        
        // Insert tuples until page is full
        let mut count = 0;
        loop {
            if page.insert_tuple(&large_data).is_none() {
                break;
            }
            count += 1;
            if count > 10 {
                break; // Safety limit
            }
        }
        
        // Should fit at least 1 tuple
        assert!(count >= 1);
    }

    #[test]
    fn test_tuple_deletion() {
        let mut page = Page::new(1);
        let tuple_data = b"Test tuple";
        
        let slot_id = page.insert_tuple(tuple_data).unwrap();
        assert!(page.delete_tuple(slot_id));
        
        // After deletion, get_tuple should return None or empty
        let retrieved = page.get_tuple(slot_id);
        // Tombstone should make this return None or handle deletion
        assert!(retrieved.is_none() || retrieved.unwrap().is_empty());
    }

    #[test]
    fn test_pin_count() {
        let page = Page::new(1);
        assert_eq!(page.get_pin_count(), 0);
        
        page.pin();
        assert_eq!(page.get_pin_count(), 1);
        
        page.pin();
        assert_eq!(page.get_pin_count(), 2);
        
        page.unpin();
        assert_eq!(page.get_pin_count(), 1);
        
        page.unpin();
        assert_eq!(page.get_pin_count(), 0);
    }

    #[test]
    fn test_dirty_flag() {
        let page = Page::new(1);
        assert!(!page.is_dirty());
        
        page.mark_dirty();
        assert!(page.is_dirty());
        
        page.clear_dirty();
        assert!(!page.is_dirty());
    }
}
