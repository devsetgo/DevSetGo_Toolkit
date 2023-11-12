# -*- coding: utf-8 -*-
# import pytest
# from devsetgo_toolkit import AsyncDatabase
# from devsetgo_toolkit import DatabaseOperations, DatabaseOperationException
# from sqlalchemy.future import select
# from asynctest import CoroutineMock

# # Mock settings_dict for AsyncDatabase
# settings_dict = {
#     "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
# }

# @pytest.mark.asyncio
# class TestDatabaseOperations:

#     @pytest.fixture
#     async def setup(self):
#         async_db = AsyncDatabase(settings_dict=settings_dict)
#         db_ops = DatabaseOperations(async_db)
#         return db_ops

#     async def test_count_query(self, setup):
#         setup.async_db.get_db_session = CoroutineMock()
#         mock_query = select(func.count()).select_from('')
#         result = await setup.count_query(mock_query)
#         assert result is not None

#     async def test_fetch_query(self, setup):
#         setup.async_db.get_db_session = CoroutineMock()
#         mock_query = select().from('your_table')
#         result = await setup.fetch_query(mock_query)
#         assert result is not None

#     async def test_fetch_queries(self, setup):
#         setup.async_db.get_db_session = CoroutineMock()
#         mock_queries = {'query1': select().from('table1'), 'query2': select().from('table2')}
#         result = await setup.fetch_queries(mock_queries)
#         assert result is not None

#     async def test_execute_one(self, setup):
#         setup.async_db.get_db_session = CoroutineMock()
#         mock_record = {}  # Your record here
#         result = await setup.execute_one(mock_record)
#         assert result is not None

#     async def test_execute_many(self, setup):
#         setup.async_db.get_db_session = CoroutineMock()
#         mock_records = [{}, {}]  # Your records here
#         result = await setup.execute_many(mock_records)
#         assert result is not None
