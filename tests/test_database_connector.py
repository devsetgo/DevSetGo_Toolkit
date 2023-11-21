# -*- coding: utf-8 -*-
# # tests/test_async_database.py

# from unittest.mock import AsyncMock, MagicMock, patch

# import pytest
# from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
# from sqlalchemy.orm import sessionmaker

# from devsetgo_toolkit import AsyncDatabase  # replace with actual module path


# # Define the AsyncContextManagerMock class
# class AsyncContextManagerMock(AsyncMock):
#     async def __aenter__(self):
#         return self

#     async def __aexit__(self, exc_type, exc_val, exc_tb):
#         pass


# # Test that __init__ method correctly initializes engine, base model, and sessionmaker
# def test_init():
#     db_instance = AsyncDatabase(
#         {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
#     )

#     assert db_instance.DATABASE_URL == "sqlite+aiosqlite:///:memory:?cache=shared"
#     assert db_instance.metadata is not None
#     assert isinstance(db_instance.engine, AsyncEngine)
#     assert isinstance(db_instance.sessionmaker, sessionmaker)


# # Test that create_tables method correctly creates tables
# @pytest.mark.asyncio
# async def test_create_tables():
#     db_instance = AsyncDatabase(
#         {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
#     )

#     # Mock engine on the instance
#     db_instance.engine = MagicMock()

#     # Create a mock connection
#     mock_conn = AsyncContextManagerMock()

#     # The begin method should return the mock connection
#     db_instance.engine.begin.return_value = mock_conn

#     await db_instance.create_tables()

#     # Assert that run_sync was called on the mock connection
#     mock_conn.run_sync.assert_called_once_with(
#         lambda: db_instance.Base.metadata.create_all()
#     )


# # Test that get_db_session context manager correctly manages a database session
# @pytest.mark.asyncio
# async def test_get_db_session():
#     db_instance = AsyncDatabase(
#         {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
#     )

#     # Mock sessionmaker on the instance
#     db_instance.sessionmaker = MagicMock()

#     # Create a mock session
#     mock_session = AsyncMock(spec=AsyncSession)

#     # Configure __aenter__ and __aexit__ for the mock session
#     mock_session.__aenter__.return_value = mock_session
#     mock_session.__aexit__.return_value = False  # No exception handling

#     # The sessionmaker method should return the mock session
#     db_instance.sessionmaker.return_value = mock_session

#     async with db_instance.get_db_session() as session:
#         assert session == mock_session

#     mock_session.commit.assert_called_once()
#     mock_session.close.assert_called_once()


# # tests/test_database_connector.py

# import pytest
# from unittest.mock import MagicMock, patch, AsyncMock
# from devsetgo_toolkit.database_connector import AsyncDatabase
# from sqlalchemy.ext.asyncio import AsyncSession

# @pytest.mark.asyncio
# @patch("devsetgo_toolkit.database_connector.AsyncDatabase.engine")
# async def test_create_tables(mock_engine):
#     # Create a real database instance
#     db_instance = AsyncDatabase(
#         {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
#     )

#     # Mock the engine's begin method
#     mock_conn = MagicMock()
#     mock_engine.begin.return_value.__aenter__.return_value = mock_conn

#     # Call the function under test
#     await db_instance.create_tables()

#     # Check if the function calls are correct
#     mock_conn.run_sync.assert_called_once_with(db_instance.Base.metadata.create_all)


# @pytest.mark.asyncio
# @patch(
#     "devsetgo_toolkit.database_connector.AsyncDatabase.sessionmaker",
#     return_value=MagicMock(spec=AsyncSession),
# )
# async def test_get_db_session(mock_sessionmaker):
#     # Create a real database instance
#     db_instance = AsyncDatabase(
#         {"database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"}
#     )

#     # Use the context manager
#     async with db_instance.get_db_session() as session:
#         # Check if the correct session is returned
#         assert isinstance(session, AsyncSession)

#     # Check if commit and close were called once
#     session.commit.assert_called_once()
#     session.close.assert_called_once()
