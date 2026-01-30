"""
True Lazy Loading for Streamlit Tabs
Staff+ Mandate: NOTHING heavy runs unless user opens that tab

PROBLEM:
Streamlit evaluates ALL tab content on every rerun, even if tabs aren't visible.

SOLUTION:
Use session state guards to track which tabs have been "activated" by user,
and only render heavy content for activated tabs.
"""

import streamlit as st
from typing import Callable, Optional, Any
from functools import wraps
import time


class LazyTabLoader:
    """
    Enterprise-grade lazy loading for Streamlit tabs.
    
    Usage:
        loader = LazyTabLoader()
        
        with main_tabs[0]:
            if loader.should_load("sender_tab"):
                # Heavy content here - only loads when tab is active
                render_sender_dashboard()
            else:
                st.info("Loading...")
    """
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        """Initialize lazy loading tracking in session state"""
        if "_lazy_tabs" not in st.session_state:
            st.session_state._lazy_tabs = {
                "loaded": set(),           # Tabs that have been loaded
                "active": None,            # Currently active tab
                "load_times": {},          # Performance tracking
                "first_load": True,        # Is this the first page load?
            }
    
    def should_load(self, tab_id: str, force: bool = False) -> bool:
        """
        Determine if a tab's heavy content should be loaded.
        
        Returns True if:
        1. Tab has been explicitly activated, OR
        2. This is the first load and tab is the default, OR
        3. force=True is passed
        
        CRITICAL: First render should only load the FIRST tab.
        Subsequent tabs load on-demand when user clicks.
        """
        if force:
            self._mark_loaded(tab_id)
            return True
        
        # Check if this tab is already loaded
        if tab_id in st.session_state._lazy_tabs["loaded"]:
            return True
        
        # On first page load, only load the first tab (index 0)
        if st.session_state._lazy_tabs["first_load"]:
            if tab_id.endswith("_0") or tab_id in ["sender_tab", "sender_side"]:
                self._mark_loaded(tab_id)
                st.session_state._lazy_tabs["first_load"] = False
                return True
            return False
        
        # Tab hasn't been loaded yet
        return False
    
    def activate_tab(self, tab_id: str):
        """Mark a tab as activated (user has clicked on it)"""
        self._mark_loaded(tab_id)
        st.session_state._lazy_tabs["active"] = tab_id
    
    def _mark_loaded(self, tab_id: str):
        """Internal: mark tab as loaded and track timing"""
        if tab_id not in st.session_state._lazy_tabs["loaded"]:
            start = time.perf_counter()
            st.session_state._lazy_tabs["loaded"].add(tab_id)
            st.session_state._lazy_tabs["load_times"][tab_id] = time.perf_counter() - start
    
    def get_load_time(self, tab_id: str) -> float:
        """Get load time for a tab (for performance monitoring)"""
        return st.session_state._lazy_tabs["load_times"].get(tab_id, 0)
    
    def is_loaded(self, tab_id: str) -> bool:
        """Check if a tab has been loaded"""
        return tab_id in st.session_state._lazy_tabs["loaded"]
    
    def render_loading_placeholder(self, tab_id: str):
        """Render a placeholder for tabs that haven't loaded yet"""
        st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 300px;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 10px;
            margin: 20px 0;
        ">
            <div style="font-size: 48px; margin-bottom: 16px;">📊</div>
            <h3 style="color: #4a5568; margin: 0;">Ready to Load</h3>
            <p style="color: #718096; margin: 8px 0 0 0;">Click to activate this section</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Load Section", key=f"load_{tab_id}", use_container_width=True):
            self.activate_tab(tab_id)
            st.rerun()


def lazy_section(section_id: str, loader: Optional[LazyTabLoader] = None):
    """
    Decorator for lazy loading entire sections.
    
    Usage:
        @lazy_section("coo_dashboard")
        def render_coo_dashboard():
            # Heavy rendering here
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _loader = loader or LazyTabLoader()
            
            if _loader.should_load(section_id):
                return func(*args, **kwargs)
            else:
                _loader.render_loading_placeholder(section_id)
                return None
        
        return wrapper
    return decorator


# Global loader instance for convenience
_global_loader: Optional[LazyTabLoader] = None


def get_lazy_loader() -> LazyTabLoader:
    """Get the global lazy loader instance"""
    global _global_loader
    if _global_loader is None:
        _global_loader = LazyTabLoader()
    return _global_loader
