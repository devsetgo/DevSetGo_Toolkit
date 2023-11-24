# -*- coding: utf-8 -*-

import secrets
import string
from datetime import datetime, timezone  # For handling date and time related tasks
from random import choices
from typing import List
from uuid import uuid4  # For generating unique identifiers

from fastapi import FastAPI, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import Column, Select, String
from tqdm import tqdm

from devsetgo_toolkit import AsyncDatabase, DatabaseOperations, DBConfig
from devsetgo_toolkit.logger import logger

app = FastAPI()


# Create a DBConfig instance
config = {
    # "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres",
    "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "echo": False,
    "future": True,
    # "pool_pre_ping": True,
    # "pool_size": 10,
    # "max_overflow": 10,
    "pool_recycle": 3600,
    # "pool_timeout": 30,
}

db_config = DBConfig(config)
# Create an AsyncDatabase instance
async_db = AsyncDatabase(db_config)

# Create a DatabaseOperations instance
db_ops = DatabaseOperations(async_db)


@app.on_event("startup")
async def startup_event():
    await async_db.create_tables()
    # Create a list to hold the user data

    # Create a loop to generate user data

    for i in tqdm(range(20), desc="executing one"):
        value = secrets.token_hex(16)
        user = User(
            name_first=f"First{value}",
            name_last=f"Last{value}",
            email=f"user{value}@example.com",
        )
        await db_ops.execute_one(user)

    users = []
    # Create a loop to generate user data
    for i in tqdm(range(2000), desc="executing many"):
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
