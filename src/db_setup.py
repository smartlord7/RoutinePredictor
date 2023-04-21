import json
import psycopg2

EXTENSION_DB_CONFIG = '.json'
PATH_DB_CONFIG = 'db_config' + EXTENSION_DB_CONFIG


def db_setup(path=PATH_DB_CONFIG):
    db_config = json.loads(PATH_DB_CONFIG)

    username = db_config['username']
    password = db_config['password']
    address = db_config['address']
    port = db_config['port']
    database = db_config['database']

    db_uri = f'postgresql://{username}:{password}@{address}:{port}/{database}'

    conn = psycopg2.connect(database=database, user=username,
                            password=password, host=address,
                            port=port)

    conn.autocommit = True

    return db_config, db_uri, conn