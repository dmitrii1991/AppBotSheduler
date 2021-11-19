from app.utils import Secret, JWT

PASSWORD: bytes = Secret.get_new_password()
PASSWORD1: bytes = Secret.get_new_password()

TEST_AUTH_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
}

TEST_USER = {
    "teleg_id": 749905997,
    "teleg_is_bot": False,
    "teleg_first_name": "Dima",
    "teleg_username": "PyCry",
    "teleg_lang": "ru",
    "username": "PyCry",
    "firstname": "Дмитрий",
    "email": "123@123.ru",
    "phone": "12345678910",
    "password_hash": Secret.hashpw(PASSWORD).decode(),
    "is_admin": True,
}

TEST_USER1 = {
    "teleg_id": 749905998,
    "teleg_is_bot": False,
    "teleg_first_name": "Dima2",
    "teleg_username": "PyCry2",
    "teleg_lang": "ru",
    "username": "PyCry2",
    "firstname": "Дмитрий2",
    "email": "1232@123.ru",
    "phone": "12345678912",
    "password_hash": Secret.hashpw(PASSWORD1).decode(),
    "is_admin": False,
}

TEST_EVENTS = [{
        "name": "Days",
        "type_event": "EVENT",
        "repetition": "YEAR",
        "date": "2099-10-11",
        "days_reminder": 6,
    },
    {
        "name": "Dmitriy Kul",
        "type_event": "BIRTHDATE",
        "date": "1991-12-10",
        "days_reminder": 6,
    },
    {
        "name": "legs",
        "type_event": "DOCUMENT",
        "repetition": "YEAR",
        "date": "2077-12-10",
        "days_reminder": 6,
    },
]

TEST_JWT = JWT.create_access_token({"sub": TEST_USER["username"]})
TEST_JWT1 = JWT.create_access_token({"sub": TEST_USER1["username"]})

TEST_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TEST_JWT}",
}

TEST_HEADERS1 = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TEST_JWT1}",
}
