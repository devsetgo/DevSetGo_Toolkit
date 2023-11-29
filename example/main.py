# -*- coding: utf-8 -*-
import logging
import random
import secrets
import string
import tracemalloc
from contextlib import asynccontextmanager
from datetime import datetime, timezone  # For handling date and time related tasks
from random import choices
from typing import Any, Dict, List, Optional  # For type hinting
from uuid import uuid4  # For generating unique identifiers

from dsg_lib.logging_config import config_log
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import Column, Delete, Select, String, Update
from tqdm import tqdm

from devsetgo_toolkit import (
    AsyncDatabase,
    DatabaseOperations,
    DBConfig,
    SchemaBase,
    generate_code_dict,
    # system_health_endpoints,
    # system_tools_endpoints
)

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)


config_log(
    logging_directory="logs",
    log_name="log.log",
    logging_level="WARNING",
    log_rotation="100 MB",
    log_retention="2 days",
    log_backtrace=True,
    log_format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    log_serializer=True,
)


async def create_a_bunch_of_users(single_entry=0, many_entries=0):
    logger.info(f"single_entry: {single_entry}")
    await async_db.create_tables()
    # Create a list to hold the user data

    # Create a loop to generate user data

    for i in tqdm(range(single_entry), desc="executing one"):
        value = secrets.token_hex(16)
        user = User(
            first_name=f"First{value}",
            last_name=f"Last{value}",
            email=f"user{value}@example.com",
        )
        logger.info(f"created_users: {user}")
        await db_ops.create_one(user)

    users = []
    # Create a loop to generate user data
    for i in tqdm(range(many_entries), desc="executing many"):
        value_one = secrets.token_hex(4)
        value_two = secrets.token_hex(8)
        user = User(
            first_name=f"First{value_one}{i}{value_two}",
            last_name=f"Last{value_one}{i}{value_two}",
            email=f"user{value_one}{i}{value_two}@example.com",
        )
        logger.info(f"created_users: {user.first_name}")
        users.append(user)

    # Use db_ops to add the users to the database
    await db_ops.create_many(users)


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracemalloc.start()

    logger.info("starting up")
    # Create the tables in the database
    await async_db.create_tables()

    create_users = True
    if create_users:
        await create_a_bunch_of_users(single_entry=23, many_entries=2000)
    yield

    tracemalloc.stop()


# Create an instance of the FastAPI class
app = FastAPI(
    title="FastAPI Example",  # The title of the API
    description="This is an example of a FastAPI application using the DevSetGo Toolkit.",  # A brief description of the API
    version="0.1.0",  # The version of the API
    docs_url="/docs",  # The URL where the API documentation will be served
    redoc_url="/redoc",  # The URL where the ReDoc documentation will be served
    openapi_url="/openapi.json",  # The URL where the OpenAPI schema will be served
    debug=True,  # Enable debug mode
    middleware=[],  # A list of middleware to include in the application
    routes=[],  # A list of routes to include in the application
    lifespan=lifespan,
)


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


# User class inherits from SchemaBase and async_db.Base
# This class represents the User table in the database
class User(SchemaBase, async_db.Base):
    __tablename__ = "users"  # Name of the table in the database

    # Define the columns of the table
    first_name = Column(String, unique=False, index=True)  # First name of the user
    last_name = Column(String, unique=False, index=True)  # Last name of the user
    email = Column(
        String, unique=True, index=True, nullable=True
    )  # Email of the user, must be unique


# UserBase class inherits from BaseModel
# This class is used for request validation when creating a new user
class UserBase(BaseModel):
    first_name: str = Field(  # First name of the user
        ...,  # This means that the field is required
        description="the users first or given name",  # Description of the field
        examples=["Bob"],  # Example of a valid input
    )
    last_name: str = Field(  # Last name of the user
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
    id: str  # ID of the user
    date_created: datetime  # Date when the user was created
    date_updated: datetime  # Date when the user was last updated

    model_config = ConfigDict(
        from_attributes=True
    )  # Configuration for the Pydantic model


# UserList class inherits from BaseModel
# This class is used for the response when retrieving a list of users
class UserList(BaseModel):
    users: List[UserResponse]  # List of users


# UserUpdate class inherits from BaseModel
# This class is used for request validation when updating a user
class UserUpdate(BaseModel):
    first_name: Optional[str] = "Bob"
    last_name: Optional[str] = "Fruit"
    email: Optional[EmailStr] = "bob.fruit@example.com"


class QueryData(BaseModel):
    total_count: int
    current_count: int


class ReadUsersResponse(BaseModel):
    query_data: QueryData
    users: List[UserResponse]


class Message(BaseModel):
    message: str


# Define a route for the root ("/") URL
@app.get("/", tags=["root"])
async def root():
    # When this route is accessed, redirect the client to "/docs" with a 307 status code
    return RedirectResponse("/docs", status_code=307)


# Define a route for the "/users/count" URL
@app.get("/users/count", tags=["users"])
async def count_users():
    # Execute a count query on the User table
    count = await db_ops.count_query(Select(User))
    # Return the count as a JSON object
    # logger.info(f"count: {count}")
    # return {"count": count}
    return ORJSONResponse(content={"count": count})


# Define a route for the "/users" URL
@app.get("/users", tags=["users"])  # , response_model=ReadUsersResponse)
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
    users = await db_ops.read_query(query=query, limit=limit, offset=offset)
    # Calculate the current count
    current_count = len(users)
    # Return the total number of users, the number of users returned, and the users themselves
    return ReadUsersResponse(
        query_data=QueryData(
            total_count=total_count, count=len(users), current_count=current_count
        ),
        users=users,
    )


# Define a route for the "/users/bulk/auto" URL
@app.get(
    "/users/bulk/auto",
    tags=["users"],
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users_auto(qty: int = Query(100, le=1000, ge=1)):
    # Initialize an empty list to hold the new User instances
    db_users: list = []
    # Generate the specified quantity of users
    for i in range(qty):
        # Generate a random first name and last name
        first_name = "".join(random.choices(string.ascii_lowercase, k=5))
        last_name = "".join(random.choices(string.ascii_lowercase, k=5))

        # Generate a random email
        random_email_part = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        email = f"user{random_email_part}@yahoo.com"

        # Create a new User instance and add it to the list
        db_user = User(first_name=first_name, last_name=last_name, email=email)
        db_users.append(db_user)

    # Insert the new users into the database
    created_users = await db_ops.create_many(db_users)

    # Log the number of created users
    logger.info(f"created_users: {len(created_users)}")
    # Return the created users
    return created_users


# Define a route for the "/users/{user_id}" URL
@app.get("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def read_user(user_id: str):
    # Execute a SELECT query to get the user with the specified ID
    users = await db_ops.read_query(Select(User).where(User.id == user_id))
    # If no users were found, raise a 404 error
    if not users:
        logger.info(f"user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    # Log the found user
    logger.info(f"users: {users[0]}")
    print(f"users: {users}")
    # Return the found user
    return users[0]


# Define a route for the "/users/{user_id}" URL that responds to PUT requests
@app.put("/users/{user_id}", tags=["users"], response_model=UserResponse)
async def update_user(user_id: str, user: UserUpdate):
    # Prepare the new data for the user
    new_data = user.dict()
    print(new_data)
    # Execute the update_one function to update the user with the specified ID
    updated_user = await db_ops.update_one(
        table=User,
        record_id=user_id,
        new_values=new_data,  # Change record_id to record_id
    )

    # If no users were updated, raise a 404 error
    if updated_user is None:
        logger.info(f"user not found: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    # Return the updated user
    return updated_user


# Define a route for the "/users/{user_id}" URL that responds to DELETE requests
@app.delete("/users/{user_id}", tags=["users"])
async def delete_user(user_id: str):
    # Execute the delete_one function to delete the user with the specified ID
    result = await db_ops.delete_one(table=User, record_id=user_id)

    # If the delete was successful, return a success message
    if result:
        # return {"message": "User deleted successfully"}
        return ORJSONResponse(content={"message": "User deleted successfully"})
    # If the delete wasn't successful, return an error message
    else:
        raise HTTPException(status_code=404, detail="User not found")


# Define a route for the "/users/" URL that responds to POST requests
@app.post(
    "/users/",
    tags=["users"],
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserBase):
    # Create a new User instance from the provided data
    db_user = User(
        first_name=user.first_name, last_name=user.last_name, email=user.email
    )
    # Insert the new user into the database
    created_user = await db_ops.create_one(db_user)
    # Return the created user
    return created_user


# Define a route for the "/users/bulk/" URL that responds to POST requests
@app.post(
    "/users/bulk/",
    tags=["users"],
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users(user_list: UserList):
    # Create a list of new User instances from the provided data
    db_users = [
        User(first_name=user.first_name, last_name=user.last_name, email=user.email)
        for user in user_list.users
    ]
    # Insert the new users into the database
    created_users = await db_ops.create_many(db_users)
    # Log the created users
    logger.info(f"created_users: {created_users}")
    # Return the created users
    return created_users


# Endpoint configuration
config_health = {
    "enable_status_endpoint": True,  # on by default
    "enable_uptime_endpoint": True,  # on by default
    "enable_heapdump_endpoint": True,  # off by default
}

from devsetgo_toolkit.endpoints.system_health_endpoints import (
    create_health_router,
)  # , system_tools_endpoints

# # Health router
health_router = create_health_router(config=config_health)
app.include_router(health_router, prefix="/api/health", tags=["system-health"])


from devsetgo_toolkit import system_tools_endpoints

config_tools = {
    "enable_email-validation": True,
}

tool_router = system_tools_endpoints(config=config_tools)
app.include_router(tool_router, prefix="/tools", tags=["tools"])
