from os import getcwd, listdir, path, mknod, getcwd
from datetime import datetime

from psycopg2.extras import register_uuid

from api.db import dbm
from common.logging import get_logger
from schema.data.add_data import add_data


logger = get_logger(__name__)
register_uuid()


MUTEX_ID = "1625475538359"


def migrate():
    migrate_dev()


def migrate_dev():
    try:
        sorted_sql_files = get_sorted_sql_files()
        _apply_migration(sorted_sql_files)
    except Exception as e:
        logger.error("could not migrate dev environment", extra={"exception": e})
        _release_mutex_lock()
        raise (e)


def _apply_migration(sorted_sql_files: dict):
    _get_mutex_lock()

    result_set = dbm.fetch_one(
        """
        select exists (
            select from information_schema.tables
            where table_schema = 'migrations'
                and table_name = 'migrations'
        )
    """
    )
    migrations_exist = result_set.get("exists") or False

    if migrations_exist:
        migrations = dbm.fetch_one(
            """
                select max(version)
                from migrations.migrations
            """
        )
        current_version = migrations[0]
    else:
        current_version = 0

    for version, filename in sorted_sql_files.items():
        if version > current_version:
            with open(
                str(getcwd()) + "/schema/migrations/" + filename, "r"
            ) as sql_file:
                sql = sql_file.read()
                dbm.execute(sql)

    max_version = max(sorted_sql_files.keys())
    dbm.execute(
        """
            insert into migrations.migrations (version) values (%(version)s);
        """,
        {"version": max_version},
    )
    logger.info("migrated to new database version", extra={"version": max_version})

    _release_mutex_lock()


def _get_mutex_lock():
    lock = dbm.fetch_one(
        "select pg_advisory_lock(%(mutex_id)s);", {"mutex_id": MUTEX_ID}
    )
    if not lock:
        raise Exception("could not get lock")
    logger.info("got mutex lock", extra={"mutex_id": MUTEX_ID})


def _release_mutex_lock():
    dbm.execute("select pg_advisory_unlock(%(mutex_id)s);", {"mutex_id": MUTEX_ID})
    logger.info("released mutex lock", extra={"mutex_id": MUTEX_ID})


def create_db():
    migrate_dev()
    add_data()
    data_files = listdir(str(getcwd()) + "/schema/data")
    for f in data_files:
        if f.endswith(".sql"):
            with open(str(getcwd()) + "/schema/data/" + f, "r") as sql_file:
                sql = sql_file.read()
                dbm.execute(sql)
                logger.info("ran sql", extra={"file": f, "sql": sql})


def destroy_db():
    dbm.execute("drop schema if exists public cascade;")
    dbm.execute("create schema public;")
    dbm.execute("drop schema if exists migrations cascade;")
    dbm.execute("create schema migrations;")
    logger.info("destroy db")


def get_sorted_sql_files() -> dict:
    sql_files = listdir(str(getcwd()) + "/schema/migrations")
    sql_files_to_sort = {}
    for f in sql_files:
        if f.endswith(".sql"):
            version = int(f.split("_")[0])
            sql_files_to_sort[version] = f
    return dict(sorted(sql_files_to_sort.items()))


def create_migration(name):
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{now}_{name}.sql"
    filepath = f"schema/migrations/{filename}"
    if not path.exists(filepath):
        mknod(filepath)

    with open(filepath, "w") as f:
        f.write("begin;\n\n--add sql below here\n\n\ncommit;\n")
