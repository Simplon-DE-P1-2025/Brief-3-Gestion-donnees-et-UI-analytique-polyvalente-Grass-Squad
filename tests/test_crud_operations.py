import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.crud.operations_crud import insert_operation, select_operation, update_operation, delete_operation

@pytest.fixture
def mock_db_connection():
    with patch('src.crud.operations_crud.get_db_connection') as mock_conn:
        mock_con_instance = MagicMock()
        mock_cursor = MagicMock()
        
        mock_conn.return_value = mock_con_instance
        mock_con_instance.cursor.return_value = mock_cursor
        
        yield mock_cursor

def test_insert_operation(mock_db_connection):
    # Setup
    mock_db_connection.fetchone.return_value = [1] # Return ID 1
    
    data = {
        "cross": "Test CROSS",
        "date_heure_reception_alerte": "2023-01-01 10:00:00"
    }
    
    # Execute
    op_id = insert_operation(data)
    
    # Assert
    assert op_id == 1
    assert mock_db_connection.execute.call_count >= 1 # Insert + Audit maybe (but audit writes to DB too so multiple calls)
    
def test_select_operation(mock_db_connection):
    # Setup
    # Mocking description and result for select
    mock_db_connection.description = [('operation_id',), ('cross',)]
    mock_db_connection.fetchone.return_value = (1, "Test CROSS")
    
    # Execute
    result = select_operation(1)
    
    # Assert
    assert result['operation_id'] == 1
    assert result['cross'] == "Test CROSS"

def test_select_operation_not_found(mock_db_connection):
    # Setup
    mock_db_connection.fetchone.return_value = None
    
    # Execute
    result = select_operation(999)
    
    # Assert
    assert result is None

def test_update_operation(mock_db_connection):
    # Setup
    # Need to mock the initial select to check for changes for audit
    mock_db_connection.description = [('operation_id',), ('cross',)]
    mock_db_connection.fetchone.return_value = (1, "Old CROSS")
    
    data = {
        "cross": "New CROSS"
    }
    
    # Execute
    success = update_operation(1, data)
    
    # Assert
    assert success is True
    # Verify update query was called
    # We can check specific calls but checking call_count is a basic sanity check
    assert mock_db_connection.execute.call_count >= 1

def test_delete_operation(mock_db_connection):
    # Setup
    mock_db_connection.fetchone.return_value = (1, "Test")
    mock_db_connection.description = [('operation_id',), ('cross',)]
    
    # Execute
    success = delete_operation(1)
    
    # Assert
    assert success is True
    # Ensure delete calls happened
    assert mock_db_connection.execute.call_count >= 1
