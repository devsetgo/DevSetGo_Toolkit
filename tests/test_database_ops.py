# -*- coding: utf-8 -*-
import pytest
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError
from devsetgo_toolkit.database_connector import AsyncDatabase
from devsetgo_toolkit.database_ops import DatabaseOperations, DatabaseOperationException


@pytest.fixture
async def db_operations(event_loop):
    settings_dict = {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
    async_db = AsyncDatabase(settings_dict=settings_dict)
    await async_db.__aenter__()  # Initialize the app before the tests
    db_ops = DatabaseOperations(async_db)
    yield db_ops
    await async_db.__aexit__(None, None, None)  # Close connection after test


async def test_count_query(db_operations, mocker):
    mock_query = MagicMock()
    db_operations = await db_operations
    session_mock = mocker.patch.object(db_operations.async_db, "get_db_session")
    count = db_operations.count_query(mock_query)
    assert count == 10


# test_fetch_query
@pytest.mark.asyncio
async def test_fetch_query(db_operations, mocker):
    mock_query = MagicMock()
    db_operations = await db_operations
    session_mock = mocker.patch.object(
        db_operations.async_db, "get_db_session", new=AsyncMock()
    )

    async with session_mock() as session:
        session.execute.return_value.scalars.all.return_value = ["result1", "result2"]
        results = await db_operations.fetch_query(mock_query)
        assert results == ["result1", "result2"]


# test_execute_one_success
@pytest.mark.asyncio
async def test_execute_one_success(db_operations, mocker):
    mock_record = MagicMock()
    session_mock = mocker.patch.object(
        db_operations.async_db, "get_db_session", new=AsyncMock()
    )

    result = await db_operations.execute_one(mock_record)
    assert result == mock_record


# test_execute_one_failure
@pytest.mark.asyncio
async def test_execute_one_failure(db_operations, mocker):
    mock_record = MagicMock()
    session_mock = mocker.patch.object(
        db_operations.async_db, "get_db_session", new=AsyncMock()
    )
    session_mock().__aenter__().add.side_effect = IntegrityError(None, None, None)

    with pytest.raises(DatabaseOperationException):
        await db_operations.execute_one(mock_record)


# test_execute_many_success
@pytest.mark.asyncio
async def test_execute_many_success(db_operations, mocker):
    mock_records = [MagicMock(), MagicMock()]
    session_mock = mocker.patch.object(
        db_operations.async_db, "get_db_session", new=AsyncMock()
    )

    result = await db_operations.execute_many(mock_records)
    assert result == mock_records


# test_execute_many_failure
@pytest.mark.asyncio
async def test_execute_many_failure(db_operations, mocker):
    mock_records = [MagicMock(), MagicMock()]
    session_mock = mocker.patch.object(
        db_operations.async_db, "get_db_session", new=AsyncMock()
    )
    session_mock().__aenter__().add_all.side_effect = Exception()

    with pytest.raises(DatabaseOperationException):
        await db_operations.execute_many(mock_records)
