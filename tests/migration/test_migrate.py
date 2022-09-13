from schema.db_tools import migrate_dev, destroy_db


def test_migrate():
    destroy_db()
    migrate_dev()
