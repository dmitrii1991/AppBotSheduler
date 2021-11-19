#  pytest -s -v --disable-pytest-warnings

import asyncio
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

from main import app
from settings import TEST_DB_URL

from app.models import UserTortModel, EventTortModel
from tests.test_data import TEST_USER, TEST_EVENTS, TEST_USER1


@pytest.fixture(autouse=True)
async def init() -> Generator:
    initializer(['app.models'], db_url=TEST_DB_URL)
    user = await UserTortModel.create(**TEST_USER)
    for event in TEST_EVENTS:
        await EventTortModel.create(user=user, **event)
    user = await UserTortModel.create(**TEST_USER1)
    for event in TEST_EVENTS:
        await EventTortModel.create(user=user, **event)
    yield
    finalizer()


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    yield asyncio.get_event_loop()


# @pytest.fixture(scope="module")
# def event_loop(client: TestClient) -> Generator:
#     yield client.task.get_loop()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client


# @pytest.fixture(scope="session")
# async def client() -> Generator:
#     initializer(['app.models'], db_url=TEST_DB_URL)
#     await UserTortModel.create(**TEST_USER)
#     with TestClient(app) as c:
#         yield c
#     finalizer()
