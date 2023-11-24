import pytest
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from devsetgo_toolkit.async_database import AsyncDatabase, DBConfig, DatabaseOperations,DatabaseOperationException
import asyncio

from sqlalchemy.exc import IntegrityError,SQLAlchemyError


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
    name = Column(String,unique=True)


class TestDatabaseOperations:
    @pytest.fixture(scope="session")
    def db_ops(self):
        loop = asyncio.get_event_loop()
        # config = {
        #     "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
        #     "echo": True,
        #     "future": True,
        #     "pool_recycle": 3600,
        # }
        # db_config = DBConfig(config)
        # async_db = AsyncDatabase(db_config)
        # db_ops = DatabaseOperations(async_db)
        
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
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=SQLAlchemyError)

        # Check that count_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.count_query(select(User))

    @pytest.mark.asyncio
    async def test_count_query_general_exception(self, db_ops, mocker):
        # Mock the execute method to raise an Exception
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=Exception)

        # Check that count_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.count_query(select(User))

    @pytest.mark.asyncio
    async def test_fetch_query(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        result = await db_ops.fetch_query(select(User))
        assert result == []

    @pytest.mark.asyncio
    async def test_fetch_query_sqlalchemy_error(self, db_ops, mocker):
        # Mock the execute method to raise an SQLAlchemyError with a message
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=SQLAlchemyError("Test error message"))

        # Check that fetch_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.fetch_query(select(User))

    @pytest.mark.asyncio
    async def test_fetch_query_general_exception(self, db_ops, mocker):
        # Mock the execute method to raise an Exception
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=Exception)

        # Check that fetch_query raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.fetch_query(select(User))

    @pytest.mark.asyncio
    async def test_fetch_queries(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        queries = {
            "all_users": select(User)
        }
        results = await db_ops.fetch_queries(queries)
        assert results["all_users"] == []

    @pytest.mark.asyncio
    async def test_execute_one(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        user = User(name="Mike")
        await db_ops.execute_one(user)
        count = await db_ops.count_query(select(User))
        assert count == 1

    @pytest.mark.asyncio
    async def test_execute_many(self, db_ops):
        # db_ops is already awaited by pytest, so you can use it directly
        users = [User(name=f"User{i}") for i in range(10)]
        await db_ops.execute_many(users)
        count = await db_ops.count_query(select(User))
        assert count == 11  # 10 from this test, 1 from the previous test

    @pytest.mark.asyncio
    async def test_fetch_queries_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=SQLAlchemyError("Test error message"))

        # Check that fetch_queries raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.fetch_queries({"query1": select(User)})

    @pytest.mark.asyncio
    async def test_fetch_queries_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=Exception("Test error message"))

        # Check that fetch_queries raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.fetch_queries({"query1": select(User)})

    @pytest.mark.asyncio
    async def test_execute_one_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=SQLAlchemyError("Test error message"))

        # Check that execute_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.execute_one(User(name="test"))

    @pytest.mark.asyncio
    async def test_execute_one_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=Exception("Test error message"))

        # Check that execute_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.execute_one(User(name="test"))

    @pytest.mark.asyncio
    async def test_execute_many_sqlalchemy_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an SQLAlchemyError
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=SQLAlchemyError("Test error message"))

        # Check that execute_many raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.execute_many([User(name="test1"), User(name="test2")])

    @pytest.mark.asyncio
    async def test_execute_many_general_exception(self, db_ops, mocker):
        # Mock the get_db_session method to raise an Exception
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=Exception("Test error message"))

        # Check that execute_many raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.execute_many([User(name="test1"), User(name="test2")])

    @pytest.mark.asyncio
    async def test_execute_one_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=IntegrityError(None, None, None, None))

        # Check that execute_one raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.execute_one(User(name="test"))

    @pytest.mark.asyncio
    async def test_execute_many_integrity_error(self, db_ops, mocker):
        # Mock the get_db_session method to raise an IntegrityError
        mocker.patch.object(db_ops.async_db, 'get_db_session', side_effect=IntegrityError(None, None, None, None))

        # Check that execute_many raises a DatabaseOperationException
        with pytest.raises(DatabaseOperationException):
            await db_ops.execute_many([User(name="test1"), User(name="test2")])
