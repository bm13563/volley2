#!/bin/bash

case $1 in
    create-migration)
        python -c"from schema.db_tools import create_migration; create_migration('$2')"
    ;;
    migrate)
        python -c"from schema.db_tools import migrate; migrate()"
    ;;
    create-db)
        python -c"from schema.db_tools import create_db; create_db()"
    ;;
    destroy-db)
        python -c"from schema.db_tools import destroy_db; destroy_db()"
    ;;
    reset-db)
        python -c"from schema.db_tools import destroy_db; destroy_db()"
        python -c"from schema.db_tools import create_db; create_db()"
    ;;
esac