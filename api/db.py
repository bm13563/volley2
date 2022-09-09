from logging import getLogger
from os import environ
from time import sleep

from psycopg2 import connect
from psycopg2.extras import RealDictCursor


logger = getLogger(__name__)


class DbManager:
    def __init__(self):
        self.db = self.connect()

    def connect(self):
        attempts = 0
        while attempts < 5:
            try:
                return connect(
                    host=environ.get("DB_HOST"),
                    database=environ.get("DB_NAME"),
                    user=environ.get("DB_USER"),
                    password=environ.get("DB_PASSWORD"),
                )
            except Exception as e:
                attempts += 1
                logger.warn(
                    "failed to connect to database, retrying",
                    extra={
                        "attempt": attempts,
                        "exception": e,
                    },
                )
                sleep(1)
        else:
            logger.error("failed to connect to database, exiting")
            exit(1)

    def _ensure_connected(self):
        if self.db.closed > 0:
            self.db = connect()

    def execute(self, cursor, query, params=None):
        self._ensure_connected()
        try:
            logger.info("executing query", extra={"query": query, "params": params})
            cursor.execute(query, params)
            self.db.commit()
        except Exception as e:
            logger.error(
                "failed to execute query",
                extra={"query": query, "params": params, "exception": e},
            )
            self.db.rollback()
            raise (e)
        return cursor

    def fetch(self, query, params=None):
        cursor = self.db.cursor(cursor_factory=RealDictCursor)
        self.execute(cursor, query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=None):
        cursor = self.db.cursor(cursor_factory=RealDictCursor)
        self.execute(cursor, query, params)
        return cursor.fetchone()
