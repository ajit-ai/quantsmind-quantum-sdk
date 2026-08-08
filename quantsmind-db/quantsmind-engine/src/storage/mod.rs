// Storage module - Page architecture, disk management, and buffer pool
pub mod page;
pub mod disk_manager;
pub mod buffer_pool;

pub use page::{Page, PageId, PAGE_SIZE};
pub use disk_manager::{DiskManager, DiskManagerError};
pub use buffer_pool::{BufferPoolManager, FrameId, BufferPoolError};
