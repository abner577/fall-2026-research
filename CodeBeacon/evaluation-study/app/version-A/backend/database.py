from flask import current_app, g
import psycopg
from psycopg.rows import dict_row


def get_db() -> psycopg.Connection:
    if "db" not in g:
        settings = current_app.config["SETTINGS"]
        g.db = psycopg.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            sslmode=settings.db_sslmode,
            connect_timeout=settings.db_connect_timeout_seconds,
            application_name="room_monitor",
            options="-c statement_timeout=15000 -c lock_timeout=5000 -c timezone=UTC",
            autocommit=True,
            row_factory=dict_row,
        )
    return g.db


def close_db(error: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()
