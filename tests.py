
import asyncio
from typing import List
from decouple import config

import httpx
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi import status

from models import LoginBase

from main import app


DB_URL = config('DB_URL', cast=str)
DB_TEST_NAME = config('DB_TEST_NAME', cast=str)

app.motor_client_test = AsyncIOMotorClient(DB_URL)
app.mongodb_test = app.motor_client_test[DB_TEST_NAME]


def get_test_database():
    return app.mongodb_test


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_client():
    app.dependency_overrides["mongodb"] = get_test_database
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app, base_url="http://app.io") as test_client:
            yield test_client


@pytest.mark.asyncio
class TestGet:
    async def test_home_endpoint(self, test_client: httpx.AsyncClient):
        response = await test_client.get("/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
class TestUsers:
    async def test_register(self, test_client: httpx.AsyncClient):
        payload = {"username": "ildevert", "email": "ildevert@gmail.com", "password": "auroredivine", "role": "ADMIN"}
        response = await test_client.post("/users/register", json=payload)
        assert response.status_code == status.HTTP_201_CREATED
    
    async def test_register_existing_user(self, test_client: httpx.AsyncClient):
        payload = {"username": "ildevert", "email": "ildevert@gmail.com", "password": "auroredivine", "role": "ADMIN"}
        response = await test_client.post("/users/register", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
    
    async def test_register_existing_username(self, test_client: httpx.AsyncClient):
        payload = {"username": "ildo", "email": "daisy@gmail.com", "password": "auroredivine", "role": "ADMIN"}
        response = await test_client.post("/users/register", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_register_existing_email(self, test_client: httpx.AsyncClient):
        payload = {"username": "john", "email": "ildevert@gmail.com", "password": "auroredivine", "role": "ADMIN"}
        response = await test_client.post("/users/register", json=payload)
        assert response.status_code == status.HTTP_409_CONFLICT
    
    async def test_invalid_payload(self, test_client: httpx.AsyncClient):
        payload = {"username": "ildevert", "email": "ildevert@gmail.com"}
        response = await test_client.post("/users/register", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestAuth:
    async def test_valid_login(self, test_client: httpx.AsyncClient):
        payload = {"email": "ildevert@gmail.com", "password": "auroredivine"}
        response = await test_client.post("/users/login", json=payload)
        assert response.status_code ==  status.HTTP_201_CREATED
    
    async def test_invalid_login(self, test_client: httpx.AsyncClient):
        payload = {"email": "john.doe@gmail.com", "password": "john1234"}
        response = await test_client.post("/users/login", json=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestUserInfo:
    async def test_user_infor(self, test_client: httpx.AsyncClient):
        login_payload = {"email": "ildevert@gmail.com", "password": "auroredivine"}
        login_response = await test_client.post("/users/login", json=login_payload)
        assert login_response.status_code == status.HTTP_201_CREATED
        access_token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await test_client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
    
    async def test_invalid_token(self, test_client: httpx.AsyncClient):
        headers = {"Authorization": "Bearer invalid_token"}
        response = await test_client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
class TestHotel:
    async def test_create_hotel(self, test_client: httpx.AsyncClient):
        login_payload = {"email": "ildevertdaisy@gmail.com", "password": "doli"}
        login_response = await test_client.post("/users/login", json=login_payload)
        assert login_response.status_code == status.HTTP_201_CREATED
        access_token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        hotel_payload = {"name": "SupHotel", "location": "Paris", "description": "lorem ipsum", "picture_list": "['https://images.unsplash.com/photo-1596386461350-326ccb383e9f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1113&q=80']",}
        response = await test_client.post("/hotels", headers=headers, json=hotel_payload)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT