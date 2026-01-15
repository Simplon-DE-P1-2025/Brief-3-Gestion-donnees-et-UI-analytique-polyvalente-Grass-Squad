import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
import sys
import os
import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.app.utils.formatters import format_datetime, format_coordinates, format_text, format_metric

# We need to mock streamlit for session_state tests BEFORE importing the module
# because it imports streamlit at top level.
sys.modules['streamlit'] = MagicMock()
import streamlit as st
from src.app.utils.session_state import init_session_state, reset_pagination, navigate_to, clear_search


# --- Tests for formatters.py ---

def test_format_datetime():
    # Test valid datetime
    dt = pd.Timestamp("2023-01-01 10:30:00")
    assert format_datetime(dt) == "2023-01-01 10:30"
    
    # Test NaT/None
    assert format_datetime(pd.NaT) == "-"
    
    # Test fallback string
    assert format_datetime("not a date") == "not a date"

def test_format_coordinates():
    # Test valid
    assert format_coordinates(45.123, -10.456) == "45.12, -10.46"
    
    # Test invalid
    assert format_coordinates(None, 10) == "-"
    assert format_coordinates(10, float('nan')) == "-"

def test_format_text():
    # Test short text
    assert format_text("Hello", 10) == "Hello"
    
    # Test truncation
    assert format_text("Hello World", 5) == "Hello..."
    
    # Test None
    assert format_text(None) == "-"

def test_format_metric():
    # Test integer/float
    assert format_metric(10.5) == 10
    assert format_metric(100) == 100
    
    # Test None with default
    assert format_metric(None, default=0) == 0
    assert format_metric(float('nan'), default=99) == 99

# --- Tests for session_state.py ---

class MockSessionState(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(key)
    def __setattr__(self, key, value):
        self[key] = value

def test_init_session_state():
    # Mock st.session_state
    if hasattr(st, 'session_state'):
        del st.session_state
    st.session_state = MockSessionState()
    
    init_session_state()
    
    assert st.session_state.action == 'list'
    assert st.session_state.page_number == 1
    assert st.session_state.items_per_page == 10
    
    # Test it respects existing values
    st.session_state.page_number = 5
    init_session_state()
    assert st.session_state.page_number == 5

def test_reset_pagination():
    st.session_state = MockSessionState({'page_number': 10})
    reset_pagination()
    assert st.session_state.page_number == 1

def test_navigate_to():
    st.session_state = MockSessionState({'action': 'list', 'selected_operation_id': None})
    st.rerun = MagicMock()
    
    navigate_to('view', 123)
    
    assert st.session_state.action == 'view'
    assert st.session_state.selected_operation_id == 123
    st.rerun.assert_called_once()

def test_clear_search():
    st.session_state = MockSessionState({'search_operation_id': '123', 'page_number': 5})
    
    clear_search()
    
    assert st.session_state.search_operation_id == ""
    assert st.session_state.page_number == 1
