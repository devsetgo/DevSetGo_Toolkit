# -*- coding: utf-8 -*-
"""
This module defines the FastAPI application and its endpoints.

The application uses SQLAlchemy for database operations and Pydantic for request and response models. It includes endpoints for creating, reading, and counting users. It also includes a health check endpoint and a tools endpoint.

The User model is defined with first name, last name, and email fields. The UserBase Pydantic model is used for request validation when creating a new user, and the UserResponse Pydantic model is used for the response.

The application uses the AsyncDatabase and DatabaseOperations classes from the devsetgo_toolkit library for asynchronous database operations.

The application is configured to log to a file with a custom format and rotation policy.

The application includes a startup event that creates the database tables if they don't exist.

The application's root endpoint redirects to the /docs endpoint, which provides an interactive API documentation.

The application includes a /users/count endpoint that returns the total number of users, a /users endpoint that returns a list of users with pagination, a /users/ endpoint that creates a new user, a /users/bulk/ endpoint that creates multiple users, a /users/bulk/auto endpoint that automatically generates and creates multiple users, and a /users/{user_id} endpoint that returns the details of a specific user.

The application includes a /api/v1/tools endpoint and a /api/health endpoint, which are defined in separate routers.
"""
# Import necessary libraries and modules
from datetime import datetime
from typing import List

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field
from sqlalchemy import Column
from sqlalchemy import Select
from sqlalchemy import String

from devsetgo_toolkit import AsyncDatabase
from devsetgo_toolkit import DatabaseOperations
from devsetgo_toolkit import SchemaBase
from example import health_check
from devsetgo_toolkit.logger import logger



import logging
 
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.WARNING)

# Define a dictionary with the settings for the database connection
settings_dict = {
    # "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",  # SQLite connection string (commented out)
    "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres",  # PostgreSQL connection string
}

# Create an instance of AsyncDatabase with the settings from settings_dict
async_db = AsyncDatabase(settings_dict=settings_dict)

# Create an instance of DatabaseOperations with the AsyncDatabase instance
db_ops = DatabaseOperations(async_db)


# User class inherits from SchemaBase and async_db.Base
# This class represents the User table in the database
class User(SchemaBase, async_db.Base):
    __tablename__ = "users"  # Name of the table in the database

    # Define the columns of the table
    name_first = Column(String, unique=False, index=True)  # First name of the user
    name_last = Column(String, unique=False, index=True)  # Last name of the user
    email = Column(
        String, unique=True, index=True, nullable=True
    )  # Email of the user, must be unique


# UserBase class inherits from BaseModel
# This class is used for request validation when creating a new user
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


# UserResponse class inherits from UserBase
# This class is used for the response when retrieving a user
class UserResponse(UserBase):
    _id: str  # ID of the user
    date_created: datetime  # Date when the user was created
    date_updated: datetime  # Date when the user was last updated

    model_config = ConfigDict(
        from_attributes=True
    )  # Configuration for the Pydantic model


# UserList class inherits from BaseModel
# This class is used for the response when retrieving a list of users
class UserList(BaseModel):
    users: List[UserBase]  # List of users


app = FastAPI(
    title="FastAPI Example",
    description="This is an example of a FastAPI application.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=True,
    middleware=[],
    routes=[],
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup_event():
    await async_db.create_tables()


@app.on_event("shutdown")
async def shutdown_event():
    # add your code here
    pass


@app.get("/")
async def root():
    return RedirectResponse("/docs", status_code=307)


@app.get("/users/count")
async def count_users():
    count = await db_ops.count_query(Select(User))
    return {"count": count}


@app.get("/users")
async def read_users(
    limit: int = Query(None, alias="limit", ge=1, le=1000),
    offset: int = Query(None, alias="offset"),
):
    if limit is None:
        limit = 500

    if offset is None:
        offset = 0

    query_count = Select(User)
    total_count = await db_ops.count_query(query=query_count)
    query = Select(User)
    users = await db_ops.fetch_query(query=query, limit=limit, offset=offset)
    return {
        "query_data": {"total_count": total_count, "count": len(users)},
        "users": users,
    }


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase):
    db_user = User(
        name_first=user.name_first, name_last=user.name_last, email=user.email
    )
    created_user = await db_ops.execute_one(db_user)
    return created_user


@app.post(
    "/users/bulk/",
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users(user_list: UserList):
    db_users = [
        User(name_first=user.name_first, name_last=user.name_last, email=user.email)
        for user in user_list.users
    ]
    created_users = await db_ops.execute_many(db_users)
    logger.info(f"created_users: {created_users}")
    return created_users


import random
import string

@app.get(
    "/users/bulk/auto",
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users_auto(qty: int = Query(100, le=1000, ge=1)):
    db_users: list = []
    for i in range(qty):
        # Generate a random first name, last name
        name_first = "".join(random.choices(string.ascii_lowercase, k=5))
        name_last = "".join(random.choices(string.ascii_lowercase, k=5))

        # Generate a random email
        random_email_part = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        email = f"user{random_email_part}@yahoo.com"

        db_user = User(name_first=name_first, name_last=name_last, email=email)
        db_users.append(db_user)

    created_users = await db_ops.execute_many(db_users)
    
    logger.info(f"created_users: {len(created_users)}")
    return created_users



@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    users = await db_ops.fetch_query(Select(User).where(User._id == user_id))
    if not users:
        logger.info(f"user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"users: {users}")
    return users[0]

@app.get("/health/status")
async def health():
    return {"status": "UP"}