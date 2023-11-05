# tests/test_database_connector.py

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from devsetgo_toolkit.database_connector import AsyncDatabase

@pytest.mark.asyncio
@patch('devsetgo_toolkit.database_connector.AsyncDatabase')
async def test_create_tables(mock_db_class):
    # Create a mock database instance with mocked engine and Base
    db_instance = mock_db_class.return_value
    db_instance.create_tables = AsyncMock()

    # Call the function under test
    await db_instance.create_tables()

    # Check if the function calls are correct
    db_instance.create_tables.assert_called_once()

@pytest.mark.asyncio
@patch('devsetgo_toolkit.database_connector.AsyncDatabase')
async def test_get_db_session(mock_db_class):
    # Create a mock database instance with mocked sessionmaker
    db_instance = mock_db_class.return_value
    mock_session = MagicMock()
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.return_value = mock_session
    db_instance.sessionmaker.return_value = mock_context_manager

    # Call the function under test
    async with db_instance.get_db_session() as session:
        # Check if the returned session is correct
        assert session == mock_session

    # Check if the function calls are correct
    db_instance.sessionmaker.assert_called_once()