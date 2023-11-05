# -*- coding: utf-8 -*-

"""
This script handles various database operations.
It includes functionality to count rows in a query,
fetch a limited set of results from a query or multiple queries,
and execute database operations like insert and update on one or many records.

The DatabaseOperations class encapsulates these functionalities and
can be used to interact with the database asynchronously.
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
    # Method to count rows in a query
    @classmethod
    async def count_query(cls, query):
        # Create an asynchronous context manager for the database session
        async with AsyncDatabase().get_db_session() as session:
            # Execute the SQL COUNT function on the given query and return the result
            result = await session.execute(select(func.count()).select_from(query))
            return result.scalar()

    # Method to fetch a limited set of results from a query
    @classmethod
    async def fetch_query(cls, query, limit=500, offset=0):
        # Create an asynchronous context manager for the database session
        async with AsyncDatabase().get_db_session() as session:
            # Execute the given query with limit and offset, and return all results
            result = await session.execute(query.limit(limit).offset(offset))
            return result.scalars().all()

    # Method to fetch a limited set of results from multiple queries
    @classmethod
    async def fetch_queries(cls, queries: dict, limit=500, offset=0):
        results = {}
        # Create an asynchronous context manager for the database session
        async with AsyncDatabase().get_db_session() as session:
            # Iterate over each query in the queries dictionary
            for query_name, query in queries.items():
                # Execute each query with limit and offset, and store all results in the results dictionary
                result = await session.execute(query.limit(limit).offset(offset))
                results[query_name] = result.scalars().all()
        return results

    # Method to execute a single database operation (like insert, update) on one record
    @classmethod
    async def execute_one(cls, record):
        try:
            # Create an asynchronous context manager for the database session
            async with AsyncDatabase().get_db_session() as session:
                # Add the given record to the session
                session.add(record)
                # Commit the session to save changes
                await session.commit()
            logging.info("Record operation successful")
            return record
        except IntegrityError as ex:
            logging.error(f"IntegrityError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            # Raise custom exception if an IntegrityError occurs
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
            # Raise custom exception if an SQLAlchemyError occurs
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
            # Raise custom exception if a general exception occurs
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

    # Method to execute multiple database operations (like bulk insert, update) on many records
    @classmethod
    async def execute_many(cls, records: List):
        try:
            # Create an asynchronous context manager for the database session
            async with AsyncDatabase().get_db_session() as session:
                # Add all given records to the session
                session.add_all(records)
                # Commit the session to save changes
                await session.commit()

                num_records = len(records)
                logging.info(
                    f"Record operations were successful. {num_records} records were created."
                )

                return records
        except Exception as ex:
            error_only = str(ex).split("[SQL:")[0]
            logging.error(f"Failed to perform operations on records: {ex}")
            # Raise custom exception if a general exception occurs
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
