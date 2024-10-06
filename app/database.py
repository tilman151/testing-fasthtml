import logging
from typing import Optional

import sqlalchemy as sa

from app.models import Question

logger = logging.getLogger("uvicorn.info")

_ENGINE: Optional[sa.Engine] = None
metadata = sa.MetaData()

history = sa.Table(
    "history",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("question", sa.String, nullable=False),
    sa.Column("answer", sa.String, nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)


def connect(connection_string: str = "sqlite:///history.db"):
    global _ENGINE

    if _ENGINE is None:
        logger.info(f"Connecting to '{connection_string}' database")
        _ENGINE = sa.create_engine(connection_string)


def init():
    logger.info("Creating tables if they do not exist")
    metadata.create_all(_ENGINE)


def disconnect():
    logger.info("Disconnecting from database")
    _ENGINE.dispose()


def append_to_history(question: str, answer: str):
    with _get_connection() as conn:
        conn.execute(history.insert().values(question=question, answer=answer))
        conn.commit()


def get_recent_questions(
    limit: int = 10,
) -> list[Question]:
    with _get_connection() as conn:
        fetched = conn.execute(
            sa.select(history.c.question, history.c.created_at)
            .order_by(history.c.created_at.desc())
            .limit(limit)
        ).fetchall()
        fetched = [Question(*row) for row in fetched]

    return fetched


def _get_connection():
    if _ENGINE is None:
        raise RuntimeError("Not connected to a database")

    return _ENGINE.connect()
