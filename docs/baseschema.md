# Base Schema Module

This module defines the base schema for database models in the application. It uses SQLAlchemy as the ORM and provides a `SchemaBase` class that all other models should inherit from. The `SchemaBase` class includes common columns that are needed for most models like `id`, `date_created`, and `date_updated`.

## Columns

- `id`: A unique identifier for each record. It's a string representation of a UUID.
- `date_created`: The date and time when a particular row was inserted into the table. It defaults to the current UTC time when the instance is created.
- `date_updated`: The date and time when a particular row was last updated. It defaults to the current UTC time whenever the instance is updated.

## Usage

To use this module, import it and extend the `SchemaBase` class to create new database models. Here's an example:

```python
from base_schema import SchemaBase
from sqlalchemy import Column, Integer, String

class User(SchemaBase):
    __tablename__ = 'users'

    name = Column(String, index=True)
    age = Column(Integer)

```

### Full Example
This example can be found in the example [folder of the repo](https://github.com/devsetgo/DevSetGo_Toolkit/tree/main/example).

```python
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List

from dsg_lib.logging_config import config_log
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# from sqlalchemy.future import select
from sqlalchemy import Column, Select, String

from example import health_check

# , tools
# from .database_ops import DatabaseOperations
# from .database_connector import AsyncDatabase
# from .base_schema import SchemaBase
from devsetgo_toolkit import AsyncDatabase, DatabaseOperations, SchemaBase

config_log(
    logging_directory="logs",
    log_name="log.log",
    logging_level="INFO",
    log_rotation="100 MB",
    log_retention="1 days",
    log_backtrace=True,
    log_format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    log_serializer=False,
)

settings_dict = {
    # "database_uri": "sqlite+aiosqlite:///:memory:?cache=shared",
    "database_uri": "postgresql+asyncpg://postgres:postgres@db/postgres",
}

async_db = AsyncDatabase(settings_dict=settings_dict)
db_ops = DatabaseOperations(async_db)


class User(SchemaBase, async_db.Base):
    __tablename__ = "users"

    name_first = Column(String, unique=False, index=True)
    name_last = Column(String, unique=False, index=True)
    email = Column(String, unique=True, index=True, nullable=True)


class UserBase(BaseModel):
    name_first: str = Field(
        ...,
        # alias="firstName",
        description="the users first or given name",
        examples=["Bob"],
    )
    name_last: str = Field(
        ...,
        # alias="lastName",
        description="the users last or surname name",
        examples=["Fruit"],
    )
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: str
    date_created: datetime
    date_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: List[UserBase]


app = FastAPI(title="FastAPI Base Schema Example", description="Using Base Schema class with a FastAPI app.")


@app.on_event("startup")
async def startup_event():
    await async_db.create_tables()

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
    users = await db_ops.read_query(query=query, limit=limit, offset=offset)
    return {
        "query_data": {"total_count": total_count, "count": len(users)},
        "users": users,
    }


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase):
    db_user = User(
        name_first=user.name_first, name_last=user.name_last, email=user.email
    )
    created_user = await db_ops.create_one(db_user)
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
    created_users = await db_ops.create_many(db_users)
    return created_users


import random
import string


@app.get(
    "/users/bulk/auto",
    response_model=List[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_users_auto(qty: int = Query(100, le=1000, ge=1)):
    created_users: list = []
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
        created_user = await db_ops.create_one(db_user)
        created_users.append(created_user)

    return created_users


@app.get("/users/{userid}", response_model=UserResponse)
async def read_user(userid: str):
    users = await db_ops.read_query(Select(User).where(User.id == userid))
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[0]

```
