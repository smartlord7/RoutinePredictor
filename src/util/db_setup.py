"""
------------WayAhead: Predicting a person's routine------------
 University of Coimbra
 Masters in Intelligent Systems
 Ubiquitious Systems
 1st year, 2nd semester
 Authors:
 Alexandre Gameiro Leopoldo, 2019219929, uc2019219929@student.uc.pt
 Sancho Amaral Simões, 2019217590, uc2019217590@student.uc.pt
 Tiago Filipe Santa Ventura, 2019243695, uc2019243695@student.uc.pt
 Credits to:
 Carlos Bento
 Coimbra, 29th May 2023
 ---------------------------------------------------------------------------
"""

import json
import psycopg2

EXTENSION_DB_CONFIG = '.json'
PATH_DB_CONFIG = 'db_config' + EXTENSION_DB_CONFIG


def db_setup(path=PATH_DB_CONFIG):
    """
        Sets up the database connection using the configuration from the specified file.

        Parameters:
        -----------
        path: str, optional
            The file path of the database configuration file. Default is `PATH_DB_CONFIG`.

        Returns:
        --------
        tuple
            A tuple containing the database configuration dictionary, the database URI, and the database connection.

        Raises:
        -------
        FileNotFoundError
            If the specified database configuration file is not found.
    """
    with open(PATH_DB_CONFIG, 'r') as f:
        db_config = json.load(f)

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
