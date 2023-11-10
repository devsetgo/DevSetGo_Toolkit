# -*- coding: utf-8 -*-
import asyncio
import pytest
from unittest.mock import MagicMock, patch
from devsetgo_toolkit.database_connector import AsyncDatabase
from devsetgo_toolkit.database_ops import DatabaseOperationException, DatabaseOperations


# Mocking a session object for testing
class MockSession:
    def __init__(self):
        self.add_called = False
        self.commit_called = False

    async def add(self, record):
        self.add_called = True

    async def commit(self):
        self.commit_called = True


# Fixture providing settings dictionary
@pytest.fixture
def db_settings():
    return {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}


@patch.object(AsyncDatabase, "get_db_session")
def test_execute_one(mock_get_db_session, db_settings):
    mock_get_db_session.return_value.__aenter__.return_value = MockSession()

    db = AsyncDatabase(db_settings)
    record = {"id": 1, "name": "Test"}
    result = asyncio.run(DatabaseOperations(db).execute_one(record))

    assert isinstance(result, dict)
    assert result == record
    assert mock_get_db_session.return_value.__aenter__.return_value.add_called
    assert mock_get_db_session.return_value.__aenter__.return_value.commit_called


@patch.object(DatabaseOperations, "execute_one", side_effect=Exception)
def test_execute_one_with_exception(db_settings):
    db = AsyncDatabase(db_settings)
    record = {"id": 1, "name": "Test"}

    with pytest.raises(DatabaseOperationException):
        asyncio.run(DatabaseOperations(db).execute_one(record))


@patch.object(AsyncDatabase, "get_db_session")
def test_execute_many(mock_get_db_session, db_settings):
    mock_get_db_session.return_value.__aenter__.return_value = MockSession()

    db = AsyncDatabase(db_settings)
    records = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test 2"}]
    result = asyncio.run(DatabaseOperations(db).execute_many(records))

    assert isinstance(result, list)
    assert all(isinstance(record, dict) for record in result)
    assert result == records
    assert mock_get_db_session.return_value.__aenter__.return_value.add_called
    assert mock_get_db_session.return_value.__aenter__.return_value.commit_called


@patch.object(DatabaseOperations, "execute_many", side_effect=Exception)
def test_execute_many_with_exception(db_settings):
    db = AsyncDatabase(db_settings)
    records = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Test 2"}]

    with pytest.raises(DatabaseOperationException):
        asyncio.run(DatabaseOperations(db).execute_many(records))
