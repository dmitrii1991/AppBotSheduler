import datetime
import json
from asyncio import AbstractEventLoop

import pytest
import nest_asyncio
from loguru import logger
from fastapi.testclient import TestClient

from .test_data import TEST_HEADERS, TEST_HEADERS1, PASSWORD, TEST_AUTH_HEADERS, TEST_USER
from app.models import EventTortModel, UserTortModel
from app.pymodels import UserGlobal
from app.enum import *
from settings import config

config["extra"]["WORKER"] = "PyTest_API"
logger.configure(**config)
nest_asyncio.apply()

today = datetime.datetime.now().date()


@pytest.mark.api
class TestApiBase:
    """Checking basic models"""

    @pytest.mark.asyncio
    async def test_post_token(self, client: TestClient, event_loop: AbstractEventLoop):
        payload = f'username={TEST_USER["username"]}&password={PASSWORD.decode()}&' \
                  f'grant_typ=&scope=&client_id=&client_secret='
        response = client.post(
            "/token", data=payload, headers=TEST_AUTH_HEADERS)
        assert response.status_code == 200, f'{TEST_USER["username"]} {PASSWORD.decode()}'
        assert response.json()["token_type"] == "bearer", response.text


class TestApiUsers:
    """Checking basic models"""

    @pytest.mark.asyncio
    async def test_get_users_me(self, client: TestClient, event_loop: AbstractEventLoop):
        response = client.get("users/me/", headers=TEST_HEADERS)
        assert response.status_code == 200, response.text
        data = response.json()
        for key, value in TEST_USER.items():
            if key != "password_hash":
                assert data[key] == value, f"key={key} data[key]={data[key]} != value={value}"

    @pytest.mark.asyncio
    async def test_put_users_me(self, client: TestClient, event_loop: AbstractEventLoop):
        test_data = json.dumps({"email": "444444444@sdwd.ru"})
        response = client.put("users/me/", data=test_data, headers=TEST_HEADERS)
        assert response.status_code == 200, response.text
        test_data = json.dumps({"email": TEST_USER["email"]})
        response = client.put("users/me/", data=test_data, headers=TEST_HEADERS)
        assert response.json()["email"] == TEST_USER["email"], response.text

    @pytest.mark.asyncio
    async def test_post_users_event(self, client: TestClient, event_loop: AbstractEventLoop):
        test_data = json.dumps({
            "name": "вау",
            "type_event": "EVENT",
            "date": "2021-10-11",
            "days_reminder": 3})
        response = client.post("users/event/", data=test_data, headers=TEST_HEADERS)
        assert response.status_code == 400, response.text
        test_data = json.dumps({
            "name": "вау",
            "type_event": "BIRTHDATE",
            "date": "2999-10-11",
            "days_reminder": 3})
        response = client.post("users/event/", data=test_data, headers=TEST_HEADERS)
        assert response.status_code == 400, response.text
        test_data = json.dumps({
            "name": "вау",
            "type_event": "EVENT",
            "date": "2999-10-11",
            "days_reminder": 3})
        response = client.post("users/event/", data=test_data, headers=TEST_HEADERS)
        assert response.status_code == 201, response.text

    @pytest.mark.asyncio
    async def test_get_events(self, client: TestClient, event_loop: AbstractEventLoop):
        response = client.get("users/event/", headers=TEST_HEADERS)
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list), response.text
        fields = EventTortModel.model_fields()
        for element in response.json():
            assert set(element.keys()).intersection(fields)

    @pytest.mark.asyncio
    async def test_put_event(self, client: TestClient, event_loop: AbstractEventLoop, headers: dict = TEST_HEADERS,
                             path: str = "users/event"):
        user = await UserTortModel.first()
        events = await EventTortModel.filter(user=user)
        for event in events:
            fields = event.fields()
            id_field = fields["id"]
            type_event = fields["type_event"]
            response = client.put(f"{path}/{id_field}", headers=headers,
                                  data=json.dumps({"date": str(fields["date"] + datetime.timedelta(days=1))}))
            assert response.status_code == 422, response.text

            response = client.put(f"{path}/{id_field}", headers=headers,
                                  data=json.dumps({"name": fields["name"] + "1"}))
            assert response.status_code == 422, response.text

            if type_event == TypeEventEnum.BIRTH:
                response = client.put(f"{path}/{id_field}", headers=headers, data=json.dumps({
                    "name": fields["name"] + "1",
                    "date": str(fields["date"] - datetime.timedelta(days=1000)),
                    "type_event": type_event,
                    "days_reminder": fields["days_reminder"] + 1
                }))
                event = await EventTortModel.get(id=id_field)
                assert response.status_code == 200, response.text
                assert response.json()["name"] == event.name == fields["name"] + "1"
                assert response.json()["date"] == str(event.date) == str(fields["date"] - datetime.timedelta(days=1000))
                assert response.json()["days_reminder"] == event.days_reminder == fields["days_reminder"] + 1
            else:
                response = client.put(f"{path}/{id_field}", headers=headers, data=json.dumps({
                      "name": fields["name"] + "1",
                      "date": str(fields["date"] + datetime.timedelta(days=1)),
                      "days_reminder": fields["days_reminder"] + 1
                }))
                event = await EventTortModel.get(id=id_field)
                assert response.status_code == 200, response.text
                assert response.json()["name"] == event.name == fields["name"] + "1"
                assert response.json()["date"] == str(event.date) == str(fields["date"] + datetime.timedelta(days=1))
                assert response.json()["days_reminder"] == event.days_reminder == fields["days_reminder"] + 1

    @pytest.mark.asyncio
    async def test_delete_event(self, client: TestClient, event_loop: AbstractEventLoop):
        response = client.delete("users/event/23232323", headers=TEST_HEADERS)
        assert response.status_code == 404, response.text
        user = await UserTortModel.first()
        events = await EventTortModel.filter(user=user)
        for event in events:
            id_ = event.id
            response = client.delete(f"users/event/{id_}", headers=TEST_HEADERS)
            assert response.status_code == 200, response.text
            assert await EventTortModel.get_or_none(id=id_) is None, response.text

    @pytest.mark.asyncio
    async def test_delete_all_event(self, client: TestClient, event_loop: AbstractEventLoop):
        response = client.delete("users/event/", headers=TEST_HEADERS)
        assert response.status_code == 200, response.text
        user = await UserTortModel.first()
        events = await EventTortModel.filter(user=user)
        assert events == [], response.text


class TestApiAdmin:
    """Checking basic models"""

    @pytest.mark.asyncio
    async def test_get_users(self, client: TestClient, event_loop: AbstractEventLoop):
        response = client.get("admin/users", headers=TEST_HEADERS)
        assert response.status_code == 200, response.text
        assert len(response.json()) == 2, response.text
        assert set(TEST_USER.keys()).intersection(set(response.json()[0].keys())), response.text
        response_not_admin = client.get("admin/users", headers=TEST_HEADERS1)
        assert response_not_admin.status_code == 403, response.text

    @pytest.mark.asyncio
    async def test_get_user(self, client: TestClient, event_loop: AbstractEventLoop):
        user = await UserTortModel.get(id=1)
        response = client.get(f"admin/users/{user.id}", headers=TEST_HEADERS)
        assert response.status_code == 200, response.text
        assert set(TEST_USER.keys()).intersection(set(response.json().keys())), response.text
        response = client.get(f"admin/users/{user.id}", headers=TEST_HEADERS1)
        assert response.status_code == 403, response.text

    @pytest.mark.asyncio
    async def test_post_user(self, client: TestClient, event_loop: AbstractEventLoop):
        response_excess_field = client.post(f"admin/users", headers=TEST_HEADERS, data=json.dumps(TEST_USER))
        assert response_excess_field.status_code == 422, response_excess_field.text
        assert response_excess_field.json() == \
               {"detail": [{"loc": ["body", "password_hash"], "msg":"extra fields not permitted",
                            "type":"value_error.extra"}]}
        data_user = TEST_USER
        del TEST_USER["password_hash"]
        response_fail = client.post(f"admin/users", headers=TEST_HEADERS, data=json.dumps(data_user))
        assert response_fail.json() == \
               {"detail": [{"loc": [], "msg": "UNIQUE constraint failed: user.phone", "type": "IntegrityError"}]}
        assert response_fail.status_code == 422, response_fail.text
        response = client.post(f"admin/users", headers=TEST_HEADERS, data=json.dumps({
            "teleg_id": 749905993,
            "teleg_is_bot": False,
            "teleg_first_name": "Dima3",
            "teleg_username": "PyCry3",
            "teleg_lang": "ru",
            "username": "PyCry3",
            "firstname": "Дмитрий3",
        }))
        assert response.status_code == 201, response.text

    @pytest.mark.asyncio
    async def test_put_user(self, client: TestClient, event_loop: AbstractEventLoop):
        user = await UserTortModel.get(id=2)
        user_data = await UserGlobal.from_tortoise_orm(user)
        user_data = user_data.dict()
        name = user_data["username"]
        user_data["username"] = name + '1'
        response = client.put(f"admin/users/2", headers=TEST_HEADERS, data=json.dumps(user_data))
        user = await UserTortModel.get(id=2)
        assert response.status_code == 201, response.text
        assert user_data["username"] == user.username == response.json()["username"], response.text
        response = client.put(f"admin/users/2", headers=TEST_HEADERS1, data=json.dumps(user_data))
        assert response.status_code == 401, response.text

    @pytest.mark.asyncio
    async def test_delete_user(self, client: TestClient, event_loop: AbstractEventLoop):
        user = await UserTortModel.get_or_none(id=2)
        events = await EventTortModel.filter(user=user)
        response = client.delete(f"admin/users/2", headers=TEST_HEADERS)
        user = await UserTortModel.get_or_none(id=2)
        assert response.status_code == 200, response.text
        assert user is None
        for event in events:
            ev = await EventTortModel.get_or_none(id=event.id)
            assert ev is None
