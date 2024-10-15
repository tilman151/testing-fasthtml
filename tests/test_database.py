import datetime
import importlib
from random import shuffle

import pytest
import sqlalchemy as sa


@pytest.fixture
def database_module():
    """Supply a freshly imported database module for each test."""
    from app import database

    importlib.reload(database)

    return database


def test_connect(database_module, clean_database):
    """It should connect the engine and set the _ENGINE attribute."""
    assert database_module._ENGINE is None
    database_module.connect(clean_database)
    assert isinstance(database_module._ENGINE, sa.engine.Engine)
    assert str(database_module._ENGINE.url) == clean_database


def test_disconnect(database_module, clean_database, mocker):
    """It should dispose the engine and set the _ENGINE attribute to None."""
    mock_engine = mocker.Mock(sa.engine.Engine)
    database_module._ENGINE = mock_engine

    database_module.disconnect()

    assert database_module._ENGINE is None
    mock_engine.dispose.assert_called_once()


def test_connect_only_once(database_module, clean_database):
    """Calling it multiple times shouldn't change the _ENGINE attribute."""
    database_module.connect(clean_database)
    engine = database_module._ENGINE
    database_module.connect(clean_database)
    assert database_module._ENGINE is engine


def test_init(database_module, clean_database):
    """It should create all tables."""
    database_module.connect(clean_database)
    database_module.metadata.drop_all(database_module._ENGINE)
    database_module.init()

    with database_module._get_connection() as conn:
        conn.execute(database_module.history.select()).fetchone()


def test_append_to_history(database_module, clean_database):
    """It should insert the question with the current timestamp."""
    database_module.connect(clean_database)
    database_module.append_to_history("question0", "answer0")
    database_module.append_to_history("question1", "answer1")

    with database_module._get_connection() as conn:
        result = conn.execute(database_module.history.select()).fetchall()

    assert len(result) == 2
    for i, row in enumerate(result):
        assert row.question == f"question{i}"
        assert row.answer == f"answer{i}"
        assert isinstance(row.created_at, datetime.datetime)
    assert result[0].created_at <= result[1].created_at


def test_get_recent_questions(database_module, clean_database):
    """It should return the last 10 questions ordered by timestamp."""
    database_module.connect(clean_database)
    now = datetime.datetime.now()
    values = [
        {
            "question": f"q{i}",
            "answer": f"a{i}",
            "created_at": now - datetime.timedelta(days=i),
        }
        for i in range(11)
    ]
    shuffle(values)  # insert in random order to test sorting
    with database_module._get_connection() as conn:
        conn.execute(database_module.history.insert(), values)
        conn.commit()

    result = database_module.get_recent_questions()

    assert len(result) == 10
    assert all(r.question == f"q{i}" for i, r in enumerate(result))
