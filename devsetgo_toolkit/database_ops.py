# -*- coding: utf-8 -*-

"""
This script handles various database operations.
It includes functionality to count rows in a query,
fetch a limited set of results from a query or multiple queries,
and execute database operations like insert and update on one or many records.

The DatabaseOperations class encapsulates these functionalities and
can be used to interact with the database asynchronously.

Setup to use class
settings_dict = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
}
async_db = AsyncDatabase(settings_dict=settings_dict)
db_ops = DatabaseOperations(async_db)

"""

import logging

# Importing required modules and libraries
from typing import List
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

# Importing database connector module
from devsetgo_toolkit.database_connector import AsyncDatabase


# Custom Exception Class
class DatabaseOperationException(Exception):
    # Constructor method
    def __init__(self, status_code, detail):
        self.status_code = status_code  # Status Code attribute
        self.detail = detail  # Detail attribute


# Class to handle Database operations
class DatabaseOperations:
    def __init__(self, async_db):
        self.async_db = async_db

    async def count_query(self, query):
        async with self.async_db.get_db_session() as session:
            result = await session.execute(select(func.count()).select_from(query))
            return result.scalar()

    async def fetch_query(self, query, limit=500, offset=0):
        async with self.async_db.get_db_session() as session:
            result = await session.execute(query.limit(limit).offset(offset))
            return result.scalars().all()

    async def fetch_queries(self, queries: dict, limit=500, offset=0):
        results = {}
        async with self.async_db.get_db_session() as session:
            for query_name, query in queries.items():
                result = await session.execute(query.limit(limit).offset(offset))
                results[query_name] = result.scalars().all()
        return results

    async def execute_one(self, record):
        try:
            async with self.async_db.get_db_session() as session:
                session.add(record)
                await session.commit()
            logging.info("Record operation successful")
            return record
        except IntegrityError as ex:
            logging.error(f"IntegrityError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except SQLAlchemyError as ex:
            logging.error(f"SQLAlchemyError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except Exception as ex:
            logging.error(f"Exception Failed to perform operation on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

    async def execute_many(self, records: List):
        try:
            async with self.async_db.get_db_session() as session:
                session.add_all(records)
                await session.commit()

                num_records = len(records)
                logging.info(
                    f"Record operations were successful. {num_records} records were created."
                )

                return records
        except Exception as ex:
            error_only = str(ex).split("[SQL:")[0]
            logging.error(f"Failed to perform operations on records: {ex}")
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
