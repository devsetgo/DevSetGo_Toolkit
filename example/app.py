import time
from contextlib import asynccontextmanager
from typing import Dict, List

from sqlalchemy import MetaData, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker

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
        try:
            async with self.async_db.get_db_session() as session:
                logger.debug(f"Count Query: {query}")
                result = await session.execute(select(func.count()).select_from(query))
                count = result.scalar()
                logger.info(f"Count Result: {count}")
                return count
        except SQLAlchemyError as ex:
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
        logger.debug("Starting fetch_query operation")
        async with self.async_db.get_db_session() as session:
            logger.debug(f"Fetch Query: {query}")
            result = await session.execute(query.limit(limit).offset(offset))
            data = result.scalars().all()
            logger.info(f"Fetch Result: {data}")
            return data

    async def fetch_queries(self, queries: dict, limit=500, offset=0):
        logger.debug("Starting fetch_queries operation")
        try:
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
        except SQLAlchemyError as ex:
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
        except IntegrityError as ex:
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
            logger.error(f"Exception Failed to perform operations on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            raise DatabaseOperationException(
                status_code=500,
                detail={
                    "error": error_only,
                    "details": "see logs for further information",
                },
            )


import secrets
import string
from datetime import datetime, timezone  # For handling date and time related tasks
from random import choices, randint
from uuid import uuid4  # For generating unique identifiers

from fastapi import FastAPI, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import Column, DateTime, Select, String
from tqdm import tqdm

# from example.async_database import AsyncDatabase, DatabaseOperations, DBConfig

app = FastAPI()


# Create a DBConfig instance
db_config = DBConfig(
    {
        "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared"
        # "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres"
    }
)

# Create an AsyncDatabase instance
async_db = AsyncDatabase(db_config)

# Create a DatabaseOperations instance
db_ops = DatabaseOperations(async_db)


@app.on_event("startup")
async def startup_event():
    await async_db.create_tables()
    # Create a list to hold the user data

    # Create a loop to generate user data

    for i in tqdm(range(randint(10, 50)), desc="executing one"):
        value = secrets.token_hex(16)
        user = User(
            name_first=f"First{value}",
            name_last=f"Last{value}",
            email=f"user{value}@example.com",
        )
        await db_ops.execute_one(user)

    users = []
    # Create a loop to generate user data
    for i in tqdm(range(randint(1000, 1500)), desc="executing many"):
        value_one = secrets.token_hex(4)
        value_two = secrets.token_hex(8)
        user = User(
            name_first=f"First{value_one}{i}{value_two}",
            name_last=f"Last{value_one}{i}{value_two}",
            email=f"user{value_one}{i}{value_two}@example.com",
        )
        users.append(user)

    # Use db_ops to add the users to the database
    await db_ops.execute_many(users)


from devsetgo_toolkit.base_schema import SchemaBase


class User(SchemaBase, async_db.Base):
    __tablename__ = "users"  # Name of the table in the database
    # Each instance in the table will have a unique id which is a string representation of a UUID
    # _id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))

    # # The date and time when a particular row was inserted into the table.
    # # It defaults to the current UTC time when the instance is created.
    # date_created = Column(
    #     DateTime, index=True, default=lambda: datetime.now(timezone.utc)
    # )

    # # The date and time when a particular row was last updated.
    # # It defaults to the current UTC time whenever the instance is updated.
    # date_updated = Column(
    #     DateTime,
    #     index=True,
    #     default=lambda: datetime.now(timezone.utc),
    #     onupdate=lambda: datetime.now(timezone.utc),
    # )

    # Define the columns of the table
    name_first = Column(String, unique=False, index=True)  # First name of the user
    name_last = Column(String, unique=False, index=True)  # Last name of the user
    email = Column(
        String, unique=True, index=True, nullable=True
    )  # Email of the user, must be unique


# Define a route for the root ("/") URL
@app.get("/")
async def root():
    # When this route is accessed, redirect the client to "/docs" with a 307 status code
    return RedirectResponse("/docs", status_code=307)


@app.get("/user/count")
async def user_count():
    # Use db_ops to perform database operations
    count = await db_ops.count_query(Select(User))
    return {"count": count}


class UserBase(BaseModel):
    name_first: str = Field(  # First name of the user
        ...,  # This means that the field is required
        description="the users first or given name",  # Description of the field
        examples=["Bob"],  # Example of a valid input
    )
    name_last: str = Field(  # Last name of the user
        ...,  # This means that the field is required
        description="the users last or surname name",  # Description of the field
        examples=["Fruit"],  # Example of a valid input
    )
    email: EmailStr  # Email of the user, must be a valid email address

    model_config = ConfigDict(
        from_attributes=True
    )  # Configuration for the Pydantic model


class UserResponse(UserBase):
    _id: str  # ID of the user
    date_created: datetime  # Date when the user was created
    date_updated: datetime  # Date when the user was last updated

    model_config = ConfigDict(
        from_attributes=True
    )  # Configuration for the Pydantic model


# Define a route for the "/users/bulk/auto" URL
@app.get(
    "/users/bulk/auto",
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users_auto(qty: int = Query(100, le=1000, ge=1)):
    # Initialize an empty list to hold the new User instances
    db_users: list = []
    # Generate the specified quantity of users
    for i in range(qty):
        # Generate a random first name and last name
        name_first = "".join(choices(string.ascii_lowercase, k=5))
        name_last = "".join(choices(string.ascii_lowercase, k=5))

        # Generate a random email
        random_email_part = "".join(
            choices(string.ascii_lowercase + string.digits, k=10)
        )
        email = f"user{random_email_part}@yahoo.com"

        # Create a new User instance and add it to the list
        db_user = User(name_first=name_first, name_last=name_last, email=email)
        db_users.append(db_user)

    # Insert the new users into the database
    created_users = await db_ops.execute_many(db_users)

    # Log the number of created users
    logger.info(f"created_users: {len(created_users)}")

    # Return the created users
    return created_users
