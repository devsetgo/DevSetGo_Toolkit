# -*- coding: utf-8 -*-

"""
async_database.py

This module contains several classes that handle database operations in an asynchronous manner using SQLAlchemy and asyncio.

Classes:
    - DBConfig: Manages the database configuration.
    - AsyncDatabase: Manages the asynchronous database operations.
    - DatabaseOperationException: A custom exception class for handling database operation errors.
    - DatabaseOperations: Manages the database operations.

The DBConfig class initializes the database configuration and creates a SQLAlchemy engine and a MetaData instance.

The AsyncDatabase class uses an instance of DBConfig to perform asynchronous database operations. It provides methods to get a database session and to create tables in the database.

The DatabaseOperationException class is a custom exception class that is used to handle errors that occur during database operations. It includes the HTTP status code and a detailed message about the error.

The DatabaseOperations class uses an instance of AsyncDatabase to perform various database operations such as executing count queries, fetch queries, and adding records to the database. It handles errors by raising a DatabaseOperationException with the appropriate status code and detail message.

This module uses the logger from the devsetgo_toolkit for logging.
"""

import time  # Importing time module to work with times
from contextlib import (
    asynccontextmanager,
)  # Importing asynccontextmanager from contextlib for creating context managers
from typing import Dict, List  # Importing Dict and List from typing for type hinting

from sqlalchemy import (
    MetaData,
    func,
)  # Importing MetaData and func from sqlalchemy for database operations
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)  # Importing specific exceptions from sqlalchemy for error handling
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)  # Importing AsyncSession and create_async_engine from sqlalchemy for asynchronous database operations
from sqlalchemy.future import (
    select,
)  # Importing select from sqlalchemy for making select queries
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)  # Importing declarative_base and sessionmaker from sqlalchemy for ORM operations

from devsetgo_toolkit.logger import (
    logger,
)  # Importing logger from devsetgo_toolkit for logging

Base = declarative_base()  # Creating a base class for declarative database models


class DBConfig:
    """
    A class used to manage the database configuration.

    ...

    Attributes
    ----------
    config : Dict
        a dictionary containing the database configuration
    engine : Engine
        the SQLAlchemy engine created with the database URI from the config
    metadata : MetaData
        the SQLAlchemy MetaData instance

    Methods
    -------
    get_db_session():
        Returns a context manager that provides a new database session.
    """

    def __init__(self, config: Dict):
        # Initialize the DBConfig class with a dictionary containing the database configuration
        self.config = config
        # Create a SQLAlchemy engine with the database URI from the config
        self.engine = create_async_engine(self.config["database_uri"])
        # Create a SQLAlchemy MetaData instance
        self.metadata = MetaData()
        logger.debug(f"Database engine created with URI: {self.config['database_uri']}")

    @asynccontextmanager
    async def get_db_session(self):
        # This method returns a context manager that provides a new database session
        logger.debug("Creating new database session")
        try:
            # Create a new database session
            async with sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )() as session:
                # Yield the session to the context manager
                yield session
        except SQLAlchemyError as e:
            # Log the error and raise it
            logger.error(f"Database error occurred: {str(e)}")
            raise
        finally:
            # Log the end of the database session
            logger.debug("Database session ended")


class AsyncDatabase:
    """
    A class used to manage the asynchronous database operations.

    ...

    Attributes
    ----------
    db_config : DBConfig
        an instance of DBConfig class containing the database configuration
    Base : Base
        the declarative base model for SQLAlchemy

    Methods
    -------
    get_db_session():
        Returns a context manager that provides a new database session.
    create_tables():
        Asynchronously creates all tables in the database.
    """

    def __init__(self, db_config: DBConfig):
        # Initialize the AsyncDatabase class with an instance of DBConfig
        self.db_config = db_config
        self.Base = Base
        # Bind the engine to the metadata of the base class,
        # so that declaratives can be accessed through a DBSession instance
        self.Base.metadata.bind = self.db_config.engine
        logger.debug("AsyncDatabase initialized")

    def get_db_session(self):
        # This method returns a context manager that provides a new database session
        logger.debug("Getting database session")
        return self.db_config.get_db_session()

    async def create_tables(self):
        # This method asynchronously creates all tables in the database
        logger.debug("Creating tables")
        try:
            # Begin a new transaction
            async with self.db_config.engine.begin() as conn:
                # Run a function in a synchronous manner
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as e:
            # Log the error and raise it
            logger.error(f"Error creating tables: {e}")
            raise


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

    ...

    Attributes
    ----------
    async_db : AsyncDatabase
        an instance of AsyncDatabase class for performing asynchronous database operations

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
        # Initialize the DatabaseOperations class with an instance of AsyncDatabase
        self.async_db = async_db
        logger.info("DatabaseOperations initialized")

    async def count_query(self, query):
        # This method executes a count query and returns the result
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
        # This method executes a fetch query and returns the result
        logger.debug("Starting fetch_query operation")
        async with self.async_db.get_db_session() as session:
            # Execute the fetch query
            logger.debug(f"Fetch Query: {query}")
            result = await session.execute(query.limit(limit).offset(offset))
            data = result.scalars().all()
            logger.info(f"Fetch Result: {data}")
            return data

    async def fetch_queries(self, queries: dict, limit=500, offset=0):
        # This method executes multiple fetch queries and returns the results
        logger.debug("Starting fetch_queries operation")
        try:
            results = {}
            async with self.async_db.get_db_session() as session:
                # Execute each fetch query
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
        # This method adds a single record to the database
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

    async def execute_many(self, records: List):
        # This method adds multiple records to the database
        logger.debug("Starting execute_many operation")
        try:
            t0 = time.time()
            async with self.async_db.get_db_session() as session:
                # Add all the records to the session and commit
                logger.debug(f"Adding {len(records)} records to session")
                session.add_all(records)
                await session.commit()

                num_records = len(records)
                t1 = time.time() - t0
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )
                return records
        except IntegrityError as ex:
            # Handle IntegrityError
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
            # Handle SQLAlchemyError
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
