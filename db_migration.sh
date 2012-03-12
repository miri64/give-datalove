#!/bin/bash

if [[ $# < 1 ]]; then
    echo "Usage: $0 <username>" >&2
    exit 1
fi

USERNAME=$1
python manage.py syncdb --noinput > /dev/null
python manage.py reset --noinput auth piston give > /dev/null
mysql -p -u ${USERNAME} datalovers < db_migration.sql
