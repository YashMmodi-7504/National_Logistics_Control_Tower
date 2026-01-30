# Performance optimization utilities
# Staff+ mandate: < 5s load time per section

from .cache_manager import CacheManager, get_cache_key
from .lazy_loader import LazyTabLoader, lazy_section
from .data_loader import DataLoader

__all__ = ['CacheManager', 'get_cache_key', 'LazyTabLoader', 'lazy_section', 'DataLoader']
