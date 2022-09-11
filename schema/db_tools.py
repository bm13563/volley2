from os import getcwd, environ, listdir, path, mknod, getcwd
from datetime import datetime

from dotenv import load_dotenv
from psycopg2 import connect

from common.logging import get_logger


logger = get_logger(__name__)


MUTEX_ID = "1625475538359"


def migrate():
    migrate_dev()


def migrate_dev():
    try:
        conn = get_dev_db_connection()
        sorted_sql_files = get_sorted_sql_files()
        _apply_migration(conn, sorted_sql_files)
        return conn
    except Exception as e:
        logger.error("could not migrate dev environment", extra={"exception": e})
        conn.rollback()
        _release_mutex_lock(conn)
        raise(e)


def _apply_migration(conn, sorted_sql_files: dict):
    _get_mutex_lock(conn)
    with conn.cursor() as cursor:
        cursor.execute("""
            select max(version)
            from migrations.migrations
        """)
        migrations = cursor.fetchone()
        current_version = migrations[0] if migrations[0] else 0

        for version, filename in sorted_sql_files.items():
            if version > current_version:
                with open(str(getcwd()) + "/schema/migrations/" + filename, "r") as sql_file:
                    sql = sql_file.read()
                    try:
                        cursor.execute(sql)
                        logger.info("ran sql", extra={"file": filename, "sql": sql})
                    except Exception as e:
                        conn.rollback()
                        logger.error("failed to run sql", extra={"file": filename, "sql": sql, "exception": e})
                        raise(e)

        conn.commit()
        max_version = max(sorted_sql_files.keys())
        cursor.execute("""
            insert into migrations.migrations (version) values (%(version)s)
        """, {"version": max_version})
        conn.commit()
        logger.info("migrated to new database version", extra={"version": max_version})

    _release_mutex_lock(conn)


def _get_mutex_lock(conn):
    with conn.cursor() as cursor:
        cursor.execute("select pg_advisory_lock(%(mutex_id)s);", {"mutex_id": MUTEX_ID})
        lock = cursor.fetchone()
        if not lock:
            raise Exception("could not get lock")
        logger.info("got mutex lock", extra={"mutex_id": MUTEX_ID})


def _release_mutex_lock(conn):
    with conn.cursor() as cursor:
        cursor.execute("select pg_advisory_unlock(%(mutex_id)s);", {"mutex_id": MUTEX_ID})
        logger.info("released mutex lock", extra={"mutex_id": MUTEX_ID})


def create_db():
    conn = migrate_dev()
    data_files = listdir(str(getcwd()) + "/schema/data")
    for f in data_files:
        with open(str(getcwd()) + "/schema/data/" + f, "r") as sql_file:
            sql = sql_file.read()
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
                logger.info("ran sql", extra={"file": f, "sql": sql})


def reset_db():
    conn = get_dev_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("drop schema if exists public cascade;")
        cursor.execute("create schema public;")
        cursor.execute("delete from migrations.migrations;")
        conn.commit()
        logger.info("reset db")


def get_dev_db_connection():
    load_dotenv(str(getcwd()) + "/dev.env")
    conn = connect(
        host=environ.get("DB_HOST"),
        database=environ.get("DB_NAME"),
        user=environ.get("DB_USER"),
        password=environ.get("DB_PASSWORD"),
    )
    logger.info(
        "got dev db connection",
        extra={
            "host": environ.get("DB_HOST"),
            "database": environ.get("DB_NAME"),
            "user": environ.get("DB_USER"),
        },
    )
    return conn


def get_sorted_sql_files() -> dict:
    sql_files = listdir(str(getcwd()) + "/schema/migrations")
    sql_files_to_sort = {}
    for f in sql_files:
        sortable = int(f.split("_")[0])
        sql_files_to_sort[sortable] = f

    return dict(sorted(sql_files_to_sort.items()))


def create_migration(name):
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{now}_{name}.sql"
    filepath = f"schema/migrations/{filename}"
    if not path.exists(filepath):
        mknod(filepath)

    with open(filepath, "w") as f:
        f.write("begin;\n\n--add sql below here\n\n\ncommit;\n")
