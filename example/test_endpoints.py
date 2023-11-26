import httpx
import asyncio
import uuid
from tqdm import tqdm


async def get_users():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:5000/users?limit=1000")
        return response.json()


async def update_user_first_name_and_email(user_id, new_first_name):
    new_email = f"{uuid.uuid4()}@example.com"  # Generate a unique email
    async with httpx.AsyncClient() as client:
        # Check if the new email already exists
        response = await client.get(f"http://localhost:5000/users?email={new_email}")
        if response.json():
            return "Email already exists"

        # If the email doesn't exist, proceed with the update operation
        response = await client.put(
            f"http://localhost:5000/users/{user_id}",
            json={"first_name": new_first_name, "email": new_email},
        )
        if response.content:
            return response.json()
        else:
            return None


async def delete_user(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://localhost:5000/users/{user_id}")
        return response.json()


async def confirm_user_deleted(user_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:5000/users/{user_id}")
        if response.status_code == 404:
            return True
        return False


async def main():
    response = await get_users()
    for user in tqdm(response["users"]):
        user_id = user["_id"]
        # print(f"User {user_id} exists")
        await update_user_first_name_and_email(user_id, "NewName")
        await delete_user(user_id)
        is_deleted = await confirm_user_deleted(user_id)
        # print(f"User {user_id} deleted: {is_deleted}")


asyncio.run(main())
