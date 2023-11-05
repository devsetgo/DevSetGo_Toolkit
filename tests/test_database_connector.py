# -*- coding: utf-8 -*-
# tests/test_database_connector.py

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from devsetgo_toolkit.database_connector import AsyncDatabase
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
@patch("devsetgo_toolkit.database_connector.AsyncDatabase")
async def test_create_tables(mock_db_class):
    # Create a mock database instance with mocked engine and Base
    db_instance = mock_db_class.return_value
    db_instance.create_tables = AsyncMock()

    # Call the function under test
    await db_instance.create_tables()

    # Check if the function calls are correct
    db_instance.create_tables.assert_called_once()


@pytest.mark.asyncio
@patch.object(AsyncSession, "__init__", return_value=None)
@patch.object(AsyncSession, "commit")
@patch.object(AsyncSession, "close")
async def test_get_db_session(mock_close, mock_commit, mock_init):
    # Create an instance of the real AsyncDatabase class
    db_instance = AsyncDatabase(
        {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
    )

    # Use the context manager
    async with db_instance.get_db_session() as session:
        # Check if the correct session is returned
        assert isinstance(session, AsyncSession)

    # Check if commit and close were called once
    mock_commit.assert_called_once()
    mock_close.assert_called_once()
