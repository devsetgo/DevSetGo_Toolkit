# -*- coding: utf-8 -*-
import asyncio

import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from devsetgo_toolkit import (
    AsyncDatabase,
    DatabaseOperationException,
    DatabaseOperations,
    DBConfig,
)

config = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": True,
    "future": True,
    "pool_recycle": 3600,
}
db_config = DBConfig(config)
async_db = AsyncDatabase(db_config)
db_ops = DatabaseOperations(async_db)


# Define User class here
class User(async_db.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)


class TestDatabaseOperations:
    @pytest.fixture(scope="session")
    def db_ops(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(async_db.create_tables())
        return db_ops

    @pytest.mark.asyncio
    async def test_count_query(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        count = await db_ops.count_query(select(User))
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_query_sqlalchemy_error(self, db_ops, mocker):
        # Mock the execute method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db, "get_db_session", side_effect=SQLAlchemyError
        )

        # Check that count_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.count_query(select(User))

    @pytest.mark.asyncio
    async def test_count_query_general_exception(self, db_ops, mocker):
        # Mock the execute method to raise an Exception
        mocker.patch.object(db_ops.async_db, "get_db_session", side_effect=Exception)

        # Check that count_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.count_query(select(User))

    @pytest.mark.asyncio
    async def test_get_query(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        result = await db_ops.get_query(select(User))
        assert result == []

    @pytest.mark.asyncio
    async def test_get_query_sqlalchemy_error(self, db_ops, mocker):
        # Mock the execute method to raise an SQLAlchemyError with a message
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that get_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.get_query(select(User))

    @pytest.mark.asyncio
    async def test_get_query_general_exception(self, db_ops, mocker):
        # Mock the execute method to raise an Exception
        mocker.patch.object(db_ops.async_db, "get_db_session", side_effect=Exception)

        # Check that get_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.get_query(select(User))

    @pytest.mark.asyncio
    async def test_get_queries(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        queries = {"all_users": select(User)}
        results = await db_ops.get_queries(queries)
        assert results["all_users"] == []

    @pytest.mark.asyncio
    async def test_insert_many(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        users = [User(name=f"User{i}") for i in range(10)]
        await db_ops.insert_many(users)
        count = await db_ops.count_query(select(User))
        assert count != 0  # 10 from this test, 1 from the previous test

    @pytest.mark.asyncio
    async def test_get_queries_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that get_queries raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.get_queries({"query1": select(User)})

    @pytest.mark.asyncio
    async def test_get_queries_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that get_queries raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.get_queries({"query1": select(User)})

    @pytest.mark.asyncio
    async def test_insert_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        user = User(name="Mike")
        await db_ops.insert_one(user)
        count = await db_ops.count_query(select(User))
        assert count != 0

    @pytest.mark.asyncio
    async def test_insert_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that insert_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.insert_one(User(name="test"))

    @pytest.mark.asyncio
    async def test_insert_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that insert_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.insert_one(User(name="test"))

    @pytest.mark.asyncio
    async def test_insert_many_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that insert_many raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.insert_many([User(name="test1"), User(name="test2")])

    @pytest.mark.asyncio
    async def test_insert_many_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that insert_many raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.insert_many([User(name="test1"), User(name="test2")])

    @pytest.mark.asyncio
    async def test_insert_one_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=IntegrityError(None, None, None, None),
        )

        # Check that insert_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.insert_one(User(name="test"))

    @pytest.mark.asyncio
    async def test_insert_many_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=IntegrityError(None, None, None, None),
        )

        # Check that insert_many raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.insert_many([User(name="test1"), User(name="test2")])

    @pytest.mark.asyncio
    async def test_update_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly

        user = User(name="Mike12345")
        user_record = await db_ops.insert_one(user)
        updated_user = {"name": "John12345"}
        await db_ops.update_one(
            table=User, record_id=user_record.id, new_values=updated_user
        )
        updated_user_db = await db_ops.get_query(
            select(User).where(User.id == user_record.id)
        )
        # print(updated_user_db)
        assert updated_user_db[0].name == "John12345"

    @pytest.mark.asyncio
    async def test_update_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that update_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.update_one(
                table=User, record_id=1, new_values={"name": "test"}
            )

    @pytest.mark.asyncio
    async def test_update_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that update_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.update_one(
                table=User, record_id=1, new_values={"name": "test"}
            )

    @pytest.mark.asyncio
    async def test_delete_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        user = User(name="Mike12345")
        user_record = await db_ops.insert_one(user)
        await db_ops.delete_one(table=User, record_id=user_record.id)
        deleted_user_db = await db_ops.get_query(
            select(User).where(User.id == user_record.id)
        )
        assert not deleted_user_db

    @pytest.mark.asyncio
    async def test_delete_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=SQLAlchemyError("Test error message"),
        )

        # Check that delete_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.delete_one(table=User, record_id=1)

    @pytest.mark.asyncio
    async def test_delete_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(
            db_ops.async_db,
            "get_db_session",
            side_effect=Exception("Test error message"),
        )

        # Check that delete_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.delete_one(table=User, record_id=1)
