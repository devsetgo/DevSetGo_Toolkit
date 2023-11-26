# -*- coding: utf-8 -*-
import asyncio
import uuid

import httpx
from tqdm import tqdm


async def get_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:5000/users?limit=10")
        return response.json()


async def update_user_first_name_and_email(userid, new_first_name):
    new_email = f"{uuid.uuid4()}@example.com"  # Generate a unique email
    async with httpx.AsyncClient() as client:
        # Check if the new email already exists
        response = await client.get(f"http://localhost:5000/users?email={new_email}")
        if response.json():
            return "Email already exists"

        # If the email doesn't exist, proceed with the update operation
        response = await client.put(
            f"http://localhost:5000/users/{userid}",
            json={"first_name": new_first_name, "email": new_email},
        )
        if response.content:
            return response.json()
        else:
            return None


async def delete_user(userid):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://localhost:5000/users/{userid}")
        return response.json()


async def confirm_user_deleted(userid):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:5000/users/{userid}")
        if response.status_code == 404:
            return True
        return False


async def main():
    response = await get_users()
    for user in tqdm(response["users"]):
        # print(user)
        userid = user["id"]
        # print(f"User {userid} exists")
        await update_user_first_name_and_email(userid, "NewName")
        await delete_user(userid)
        is_deleted = await confirm_user_deleted(userid)
        # print(f"User {userid} deleted: {is_deleted}")


asyncio.run(main())
