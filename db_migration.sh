#!/bin/bash

if [[ $# < 1 ]]; then
    echo "Usage: $0 <username> [<database>]" >&2
    exit 1
fi

if [[ $# == 2 ]]; then
    DATABASE=$2
else
    DATABASE=datalovers
fi

USERNAME=$1
python manage.py syncdb --noinput > /dev/null
python manage.py reset --noinput auth piston give > /dev/null
cat db_migration.sql | sed "s/{{datalovers}}/$DATABASE/g" | mysql -p -u ${USERNAME} ${DATABASE}

