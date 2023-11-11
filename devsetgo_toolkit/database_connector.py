# -*- coding: utf-8 -*-

"""
This module defines the asynchronous database class `AsyncDatabase` for handling database connections and sessions in an
asynchronous context.

The `AsyncDatabase` class does the following:

- Initializes the database engine using the connection string from the settings.
- Defines the base model that is used to produce tables.
- Creates an asynchronous sessionmaker.
- Provides a method `create_tables` to create all tables in the database.
- Provides a context manager `get_db_session` to manage database sessions. It handles committing and closing the session,
  as well as error handling.

Import this module and use the `AsyncDatabase` class to interact with the database in an asynchronous manner.

example dictionary to pass into the class.

settings_dict = {
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
}
async_db = AsyncDatabase(settings_dict=settings_dict)
db_ops = DatabaseOperations(async_db)

"""

import logging
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


class AsyncDatabase:
    def __init__(self, settings_dict):
        # Initialize engine
        self.DATABASE_URL = settings_dict.get("database_uri", "")
        self.metadata = MetaData()
        self.engine = create_async_engine(
            self.DATABASE_URL,
            echo=False,
        )

        # Define base model to produce tables
        self.Base = declarative_base(metadata=self.metadata)

        # Create async sessionmaker
        self.sessionmaker = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # Dispose the engine (close all connections)
        self.engine.dispose()

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
        logging.info("Tables created successfully")

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
        logging.info("Tables created successfully")

    @asynccontextmanager
    async def get_db_session(self):
        db_session = self.sessionmaker()
        success = False
        try:
            yield db_session
            success = True
        except SQLAlchemyError as e:
            logging.error(f"An error occurred during session: {e}")
            raise
        finally:
            if success:
                await db_session.commit()
                logging.debug("Session committed successfully")
            await db_session.close()
            logging.debug("Session closed successfully")
