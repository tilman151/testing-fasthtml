import multiprocessing
import os
from time import sleep

import pytest
import requests
import sqlalchemy as sa
import uvicorn
from starlette.testclient import TestClient

from app import database

_DB_URL_ENV_VAR = "APP_DATABASE_URL"


@pytest.fixture
def server(clean_database, setup_server):
    return setup_server


@pytest.fixture
def client(clean_database, monkeypatch):
    monkeypatch.setenv(_DB_URL_ENV_VAR, clean_database)

    from app.main import app

    client = TestClient(app)
    client.headers["HX-Request"] = "true"
    database.connect(clean_database)

    yield client

    database.disconnect()


@pytest.fixture
def clean_database(tmp_database):
    yield tmp_database

    engine = sa.create_engine(tmp_database)
    with engine.connect() as connection:
        database.metadata.drop_all(connection)
        connection.commit()
    _init_database(engine)
    engine.dispose()


@pytest.fixture(scope="module")
def setup_server(tmp_database):
    process = multiprocessing.Process(
        target=_setup_server,
        args=("app.main:app",),
        kwargs={"host": "localhost", "port": 5001, "database_url": tmp_database},
        daemon=True,
    )
    process.start()
    for i in range(50):  # 5-second timeout
        sleep(0.1)
        try:
            requests.get("http://localhost:5001")
        except requests.ConnectionError:
            continue
        else:
            break
    else:
        raise TimeoutError("Server did not start in time")

    yield process

    process.terminate()


@pytest.fixture(scope="module")
def tmp_database(tmp_database_path):
    engine = sa.create_engine(tmp_database_path)
    _init_database(engine)
    engine.dispose()

    return tmp_database_path


@pytest.fixture(scope="module")
def tmp_database_path(tmp_path_factory, request):
    path = tmp_path_factory.mktemp(request.module.__name__ + "_data", numbered=True)
    path = path / "history.db"

    return f"sqlite:///{path}"


def _setup_server(*args, **kwargs):
    if (database_url := kwargs.pop("database_url")) is None:
        raise ValueError("database_url is a required kwarg")
    os.environ[_DB_URL_ENV_VAR] = database_url
    uvicorn.run(*args, **kwargs)


def _init_database(engine):
    with engine.connect() as connection:
        database.metadata.create_all(connection)
