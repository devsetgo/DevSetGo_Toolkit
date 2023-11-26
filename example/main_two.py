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
import logging
import random
import string
import tracemalloc
from contextlib import asynccontextmanager

# Import necessary libraries and modules
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import Column, Select, String

from devsetgo_toolkit import AsyncDatabase, DatabaseOperations, SchemaBase

# from devsetgo_toolkit.logger import logger

logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.WARNING)

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracemalloc.start()
    # Create the tables in the database
    await async_db.create_tables()

    yield

    tracemalloc.stop()


# Create an instance of the FastAPI class
app = FastAPI(
    title="FastAPI Example",  # The title of the API
    description="This is an example of a FastAPI application.",  # A brief description of the API
    version="0.1.0",  # The version of the API
    docs_url="/docs",  # The URL where the API documentation will be served
    redoc_url="/redoc",  # The URL where the ReDoc documentation will be served
    openapi_url="/openapi.json",  # The URL where the OpenAPI schema will be served
    debug=True,  # Enable debug mode
    middleware=[],  # A list of middleware to include in the application
    routes=[],  # A list of routes to include in the application
    lifespan=lifespan,
)


# Define a route for the root ("/") URL
@app.get("/")
async def root():
    # When this route is accessed, redirect the client to "/docs" with a 307 status code
    return RedirectResponse("/docs", status_code=307)


# Define a route for the "/users/count" URL
@app.get("/users/count")
async def count_users():
    # Execute a count query on the User table
    count = await db_ops.count_query(Select(User))
    # Return the count as a JSON object
    return {"count": count}


# Define a route for the "/users" URL
@app.get("/users")
async def read_users(
    limit: int = Query(
        None, alias="limit", ge=1, le=1000
    ),  # Query parameter for the maximum number of users to return
    offset: int = Query(
        None, alias="offset"
    ),  # Query parameter for the number of users to skip before starting to return users
):
    # If no limit is provided, default to 500
    if limit is None:
        limit = 500

    # If no offset is provided, default to 0
    if offset is None:
        offset = 0

    # Create a SELECT query for the User table
    query_count = Select(User)
    # Execute the count query to get the total number of users
    total_count = await db_ops.count_query(query=query_count)
    # Create a SELECT query for the User table
    query = Select(User)
    # Execute the SELECT query to get the users, with the provided limit and offset
    users = await db_ops.get_query(query=query, limit=limit, offset=offset)
    # Return the total number of users, the number of users returned, and the users themselves
    return {
        "query_data": {"total_count": total_count, "count": len(users)},
        "users": users,
    }


# Define a route for the "/users/" URL that responds to POST requests
@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase):
    # Create a new User instance from the provided data
    db_user = User(
        name_first=user.name_first, name_last=user.name_last, email=user.email
    )
    # Insert the new user into the database
    created_user = await db_ops.insert_one(db_user)
    # Return the created user
    return created_user


# Define a route for the "/users/bulk/" URL that responds to POST requests
@app.post(
    "/users/bulk/",
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users(user_list: UserList):
    # Create a list of new User instances from the provided data
    db_users = [
        User(name_first=user.name_first, name_last=user.name_last, email=user.email)
        for user in user_list.users
    ]
    # Insert the new users into the database
    created_users = await db_ops.insert_many(db_users)
    # Log the created users
    logger.info(f"created_users: {created_users}")
    # Return the created users
    return created_users


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
        name_first = "".join(random.choices(string.ascii_lowercase, k=5))
        name_last = "".join(random.choices(string.ascii_lowercase, k=5))

        # Generate a random email
        random_email_part = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        email = f"user{random_email_part}@yahoo.com"

        # Create a new User instance and add it to the list
        db_user = User(name_first=name_first, name_last=name_last, email=email)
        db_users.append(db_user)

    # Insert the new users into the database
    created_users = await db_ops.insert_many(db_users)

    # Log the number of created users
    logger.info(f"created_users: {len(created_users)}")
    # Return the created users
    return created_users


# Define a route for the "/users/{user_id}" URL
@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str):
    # Execute a SELECT query to get the user with the specified ID
    users = await db_ops.get_query(Select(User).where(User._id == user_id))
    # If no users were found, raise a 404 error
    if not users:
        logger.info(f"user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    # Log the found user
    logger.info(f"users: {users}")
    # Return the found user
    return users[0]


from devsetgo_toolkit import system_health_endpoints

# User configuration
config = {
    # "enable_status_endpoint": False, # on by default
    # "enable_uptime_endpoint": False, # on by default
    "enable_heapdump_endpoint": True,  # off by default
}


# Health router
health_router = system_health_endpoints(config)
app.include_router(health_router, prefix="/api/health", tags=["system-health"])
