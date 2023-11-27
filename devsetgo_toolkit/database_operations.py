# -*- coding: utf-8 -*-

"""
"""

import logging as logger
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

from .async_database import AsyncDatabase


class DatabaseOperations:
    """
    A class used to manage the database operations in an asynchronous manner.

    This class provides methods for executing various types of database operations, including count queries, fetch queries, record insertions, updates, and deletions. It uses an instance of the AsyncDatabase class to perform these operations asynchronously.

    Attributes
    ----------
    async_db : AsyncDatabase
        An instance of AsyncDatabase class for performing asynchronous database operations.

    Methods
    -------
    count_query(query):
        Executes a count query and returns the result.
    get_query(query, limit=500, offset=0):
        Executes a fetch query and returns the result.
    get_queries(queries: dict, limit=500, offset=0):
        Executes multiple fetch queries and returns the results.
    insert_one(record):
        Adds a single record to the database.
    insert_many(records: List):
        Adds multiple records to the database.
    update_one(table, record_id: str, new_values: dict):
        Updates a single record in the database.
    delete_one(table, record_id):
        Deletes a single record from the database.
    """

    def __init__(self, async_db: AsyncDatabase):
        """
        Initializes a new instance of the DatabaseOperations class.

        This method sets up the DatabaseOperations instance with an AsyncDatabase instance, which is used for performing asynchronous database operations.

        Parameters:
        async_db (AsyncDatabase): An instance of AsyncDatabase class for performing asynchronous database operations.

        Returns: None
        """
        # Set the async_db attribute with the provided AsyncDatabase instance
        self.async_db = async_db
        # Log the initialization of the DatabaseOperations instance
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
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform count query: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "General Exception", "details": error_only}

    async def get_query(self, query, limit=500, offset=0):
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
        logger.debug("Starting get_query operation")
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
            return {"error": "SQLAlchemyError", "details": error_only}

        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during get query: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def get_queries(self, queries: Dict[str, str], limit=500, offset=0):
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
        logger.debug("Starting get_queries operation")
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
            return {"error": "SQLAlchemyError", "details": error_only}

        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during get queries: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def insert_one(self, record):
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
        logger.debug("Starting insert_one operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Add the record to the session and commit
                logger.debug(f"Record insert: {record}")
                session.add(record)
                await session.commit()
            logger.info(f"Record operation was successful: {record}.")
            return record
        except IntegrityError as ex:
            # Handle IntegrityError
            logger.error(f"IntegrityError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "IntegrityError", "details": error_only}
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during insert one: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def insert_many(self, records: List[dict]):
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
        logger.debug("Starting insert_many operation")
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
            return {"error": "IntergityError", "details": error_only}

        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError, which is a base class for all SQLAlchemy exceptions
            logger.error(f"SQLAlchemyError on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform operations on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "General Exception", "details": error_only}

    async def update_one(self, table, record_id: str, new_values: dict):
        non_updatable_fields = ["id", "date_created"]

        logger.debug(
            f"Starting update_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            async with self.async_db.get_db_session() as session:
                # Fetch the record to be updated
                logger.debug(f"Fetching record with id: {record_id}")
                record = await session.get(table, record_id)
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                # Update the record with new values
                logger.debug(f"Updating record with new values: {new_values}")
                for key, value in new_values.items():
                    if key not in non_updatable_fields:
                        logger.debug(f"Updating field: {key} with value: {value}")
                        setattr(record, key, value)
                    else:
                        logger.debug(f"Skipping non-updatable field: {key}")

                # Commit the changes
                logger.debug(f"Committing changes to the database for ID: {record_id}")
                await session.commit()

                logger.info(
                    f"Record update was successful: ID: {record_id}, Record: {record}"
                )
                return record
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on update: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during update: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def delete_one(self, table, record_id):
        try:
            async with self.async_db.get_db_session() as session:
                # Fetch the record to be deleted
                record = await session.get(table, record_id)

                # If the record doesn't exist, return None
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                # Delete the record
                await session.delete(record)

                # Commit the changes
                await session.commit()

                return {"success": "Record deleted successfully"}

        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on delete: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}

        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during delete one: {ex}")
            return {"error": "General Exception", "details": str(ex)}
