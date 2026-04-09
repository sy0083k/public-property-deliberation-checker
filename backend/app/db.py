from __future__ import annotations

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool


def create_db_engine(db_url: str) -> Engine:
    connect_args = {}
    engine_kwargs = {}

    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if ":memory:" in db_url:
            engine_kwargs["poolclass"] = StaticPool
        else:
            engine_kwargs["poolclass"] = NullPool

    engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)

    if db_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-redef]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
