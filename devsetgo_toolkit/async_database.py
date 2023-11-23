from typing import Dict, List
import time
from sqlalchemy import MetaData, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import asynccontextmanager
from devsetgo_toolkit.logger import logger

Base = declarative_base()


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
        self.config = config
        self.engine = create_async_engine(self.config["database_uri"])
        self.metadata = MetaData()
        logger.debug(f"Database engine created with URI: {self.config['database_uri']}")

    @asynccontextmanager
    async def get_db_session(self):
        logger.debug("Creating new database session")
        try:
            async with sessionmaker(
                self.engine, expire_on_commit=False, class_=AsyncSession
            )() as session:
                yield session
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred: {str(e)}")
            raise
        finally:
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
        self.db_config = db_config
        self.Base = Base
        self.Base.metadata.bind = self.db_config.engine
        logger.debug("AsyncDatabase initialized")

    def get_db_session(self):
        logger.debug("Getting database session")
        return self.db_config.get_db_session()

    async def create_tables(self):
        logger.debug("Creating tables")
        try:
            async with self.db_config.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as e:
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
    # Constructor method
    def __init__(self, status_code, detail):
        self.status_code = status_code  # Status Code attribute
        self.detail = detail  # Detail attribute


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
        self.async_db = async_db
        logger.info("DatabaseOperations initialized")

    async def count_query(self, query):
        logger.debug("Starting count_query operation")
        async with self.async_db.get_db_session() as session:
            logger.debug(f"Count Query: {query}")
            result = await session.execute(select(func.count()).select_from(query))
            count = result.scalar()
            logger.info(f"Count Result: {count}")
            return count

    async def fetch_query(self, query, limit=500, offset=0):
        logger.debug("Starting fetch_query operation")
        async with self.async_db.get_db_session() as session:
            logger.debug(f"Fetch Query: {query}")
            result = await session.execute(query.limit(limit).offset(offset))
            data = result.scalars().all()
            logger.info(f"Fetch Result: {data}")
            return data

    async def fetch_queries(self, queries: dict, limit=500, offset=0):
        logger.debug("Starting fetch_queries operation")
        results = {}
        async with self.async_db.get_db_session() as session:
            logger.debug(f"Fetch Queries: {queries}")
            for query_name, query in queries.items():
                logger.debug(f"Fetch Query: {query}")
                result = await session.execute(query.limit(limit).offset(offset))
                data = result.scalars().all()
                logger.info(f"Fetch Result: {data}")
                results[query_name] = data
        return results

    async def execute_one(self, record):
        logger.debug("Starting execute_one operation")
        try:
            async with self.async_db.get_db_session() as session:
                logger.debug(f"Record: {record}")
                session.add(record)
                await session.commit()
            logger.info(f"Record operation was successful: {record}.")
            return record
        except IntegrityError as ex:
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
        logger.debug("Starting execute_many operation")
        try:
            t0 = time.time()
            async with self.async_db.get_db_session() as session:
                logger.debug(f"Adding {len(records)} records to session")
                session.add_all(records)
                await session.commit()

                num_records = len(records)
                t1 = time.time() - t0
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )
                return records
        except Exception as ex:
            error_only = str(ex).split("[SQL:")[0]
            logger.error(f"Failed to perform operations on records: {ex}")
            raise DatabaseOperationException(
                status_code=400,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )

