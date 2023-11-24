# -*- coding: utf-8 -*-

"""
"""

import time  # Importing time module to work with times
from contextlib import (  # Importing asynccontextmanager from contextlib for creating context managers
    asynccontextmanager,
)
from typing import Dict, List  # Importing Dict and List from typing for type hinting

from sqlalchemy import (  # Importing MetaData and func from sqlalchemy for database operations
    MetaData,
    func,
)
from sqlalchemy.exc import (  # Importing specific exceptions from sqlalchemy for error handling
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.ext.asyncio import (  # Importing AsyncSession and create_async_engine from sqlalchemy for asynchronous database operations
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.future import (  # Importing select from sqlalchemy for making select queries
    select,
)
from sqlalchemy.orm import (  # Importing declarative_base and sessionmaker from sqlalchemy for ORM operations
    declarative_base,
    sessionmaker,
)

from devsetgo_toolkit.logger import (  # Importing logger from devsetgo_toolkit for logging
    logger,
)

from .async_database import AsyncDatabase


class DatabaseOperationException(Exception):
    """
    A custom exception class for handling database operation errors.

    ...

    Attributes
    ----------
    status_code : int
        an integer representing the HTTP status code of the error
    detail : str
        a string providing detailed information about the error

    Methods
    -------
    __init__(status_code, detail):
        Initializes the DatabaseOperationException with a status code and detail.
    """

    def __init__(self, status_code, detail):
        """
        Constructor method for DatabaseOperationException class.

        Parameters:
        status_code (int): The HTTP status code of the error
        detail (str): Detailed information about the error
        """
        self.status_code = (
            status_code  # Assign the status code to the instance variable
        )
        self.detail = detail  # Assign the detail to the instance variable


class DatabaseOperations:
    """
    A class used to manage the database operations.

    This class provides methods for executing various types of database operations, including count queries, fetch queries, and record insertions. It uses an instance of the AsyncDatabase class to perform these operations asynchronously.

    Attributes
    ----------
    async_db : AsyncDatabase
        An instance of AsyncDatabase class for performing asynchronous database operations.

    Methods
    -------
    count_query(query):
        Executes a count query and returns the result.
    fetch_query(query, limit=500, offset=0):
        Executes a fetch query and returns the result.
    fetch_queries(queries: dict, limit=500, offset=0):
        Executes multiple fetch queries and returns the results.
    execute_one(record):
        Adds a single record to the database.
    execute_many(records: List):
        Adds multiple records to the database.
    """

    def __init__(self, async_db: AsyncDatabase):
        """
        Constructor method for DatabaseOperations class.

        This method initializes a new instance of the DatabaseOperations class with a given instance of AsyncDatabase.

        Parameters:
        async_db (AsyncDatabase): An instance of AsyncDatabase class for performing asynchronous database operations.

        Returns: None
        """
        self.async_db = async_db
        logger.info("DatabaseOperations initialized")

    async def count_query(self, query):
        """
        Executes a count query and returns the result.

        This method takes a query, executes it against the database to count the number of matching records, and returns the count.

        Parameters:
        query (str): The SQL query to execute.

        Returns:
        int: The count of matching records.
        """
        logger.debug("Starting count_query operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Execute the count query
                logger.debug(f"Count Query: {query}")
                result = await session.execute(select(func.count()).select_from(query))
                count = result.scalar()
                logger.info(f"Count Result: {count}")
                return count
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on count query: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform count query: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

    async def fetch_query(self, query, limit=500, offset=0):
        """
        Executes a fetch query and returns the result.

        This method takes a SQL query, executes it against the database to fetch the matching records, and returns the records. It also supports pagination through the limit and offset parameters.

        Parameters:
        query (str): The SQL query to execute.
        limit (int, optional): The maximum number of records to return. Defaults to 500.
        offset (int, optional): The number of records to skip before starting to fetch the records. Defaults to 0.

        Returns:
        list: The list of matching records.
        """
        logger.debug("Starting fetch_query operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Execute the fetch query with the given limit and offset
                logger.debug(f"Fetch Query: {query}")
                result = await session.execute(query.limit(limit).offset(offset))
                data = result.scalars().all()
                logger.info(f"Fetch Result: {data}")
                return data
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on fetch query: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform fetch query: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

    async def fetch_queries(self, queries: Dict[str, str], limit=500, offset=0):
        """
        Executes multiple fetch queries and returns the results.

        This method takes a dictionary of SQL queries, executes each query against the database to fetch the matching records, and returns a dictionary of results. Each key in the result dictionary corresponds to a query name, and the value is a list of matching records for that query. The method also supports pagination through the limit and offset parameters.

        Parameters:
        queries (Dict[str, str]): A dictionary where the key is the query name and the value is the SQL query to execute.
        limit (int, optional): The maximum number of records to return for each query. Defaults to 500.
        offset (int, optional): The number of records to skip before starting to fetch the records for each query. Defaults to 0.

        Returns:
        Dict[str, list]: A dictionary where the key is the query name and the value is a list of matching records.
        """
        logger.debug("Starting fetch_queries operation")
        try:
            results = {}
            async with self.async_db.get_db_session() as session:
                # Execute each fetch query with the given limit and offset
                logger.debug(f"Fetch Queries: {queries}")
                for query_name, query in queries.items():
                    logger.debug(f"Fetch Query: {query}")
                    result = await session.execute(query.limit(limit).offset(offset))
                    data = result.scalars().all()
                    logger.info(f"Fetch Result: {data}")
                    results[query_name] = data
            return results
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on fetch queries: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform fetch queries: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

    async def execute_one(self, record):
        """
        Adds a single record to the database.

        This method takes a record, adds it to the database session, and commits the session. If the operation is successful, it returns the record. If an error occurs during the operation, it raises a DatabaseOperationException with detailed information about the error.

        Parameters:
        record (dict): The record to add to the database.

        Returns:
        dict: The record that was added to the database.

        Raises:
        DatabaseOperationException: If an error occurs during the database operation.
        """
        logger.debug("Starting execute_one operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Add the record to the session and commit
                logger.debug(f"Record: {record}")
                session.add(record)
                await session.commit()
            logger.info(f"Record operation was successful: {record}.")
            return record
        except IntegrityError as ex:
            # Handle IntegrityError
            logger.error(f"IntegrityError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform operation on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

    async def execute_many(self, records: List[dict]):
        """
        Adds multiple records to the database.

        This method takes a list of records, adds each record to the database session, and commits the session. If the operation is successful, it returns the list of records. If an error occurs during the operation, it raises a DatabaseOperationException with detailed information about the error.

        Parameters:
        records (List[dict]): The list of records to add to the database. Each record is a dictionary representing a row to be inserted into the database.

        Returns:
        List[dict]: The list of records that were added to the database.

        Raises:
        DatabaseOperationException: If an error occurs during the database operation.
        """
        logger.debug("Starting execute_many operation")
        try:
            t0 = time.time()  # Record the start time of the operation
            async with self.async_db.get_db_session() as session:
                # Add all the records to the session and commit
                logger.debug(f"Adding {len(records)} records to session")
                session.add_all(records)  # Add all records to the session
                await session.commit()  # Commit the session to save the records to the database

                num_records = len(records)  # Get the number of records added
                t1 = time.time() - t0  # Calculate the time taken for the operation
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )
                return records  # Return the list of records added
        except IntegrityError as ex:
            # Handle IntegrityError, which occurs when a database constraint is violated
            logger.error(f"IntegrityError on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError, which is a base class for all SQLAlchemy exceptions
            logger.error(f"SQLAlchemyError on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform operations on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )
