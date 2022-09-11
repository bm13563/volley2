from schema.db_tools import migrate_dev, reset_db


def test_migrate():
    reset_db()
    migrate_dev()
