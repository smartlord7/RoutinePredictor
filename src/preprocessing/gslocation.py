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

# import sqlalchemy as db
import pandas as pd
import psycopg2

"""
This script retrieves session data for a specific user from a PostgreSQL database and plots the sessions on a map using the QGIS Python API.

Usage:
- Update the database connection configurations in the script according to your PostgreSQL database.
- Set the value of `user_id` to the ID of the user for whom you want to plot the sessions.
- Ensure that the script is executed within the QGIS environment.

Output:
- Visualization of the user's sessions on a map in the QGIS interface.

"""


# Database connection configurations
POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'leopoldo'
POSTGRES_PASSWORD = '1234'
POSTGRES_DBNAME = 'suscity'

db_uri = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:{POSTGRES_PORT}/{POSTGRES_DBNAME}'

conn = psycopg2.connect(database=POSTGRES_DBNAME, user=POSTGRES_USERNAME,
                        password=POSTGRES_PASSWORD, host=POSTGRES_ADDRESS,
                        port=POSTGRES_PORT)

conn.autocommit = True

session_file_name = 'user_sessions_number.txt'

user_id = 464  # Change this to whatever user

sessions = pd.read_sql_query(f'SELECT * FROM session WHERE user_id = {user_id} ORDER BY start_time', conn)

# Unique sessions this user has
user_sessions = list(sessions['session_id'])

max_sessions = 5  # Max sessions to put on the map
counter = 0  # Counter for the max sessions

# This part only runs in QGIS!!!
for index, session_id in enumerate(user_sessions):
    location_points = pd.read_sql_query(f'SELECT * FROM gslocation WHERE session_id = {session_id}', conn)

    if location_points.empty:
        print('empty')
        continue

    session_start_time = (sessions.loc[sessions['session_id'] == session_id])['start_time'].values[0]

    date_time = pd.to_datetime(session_start_time, unit='s', origin='unix')
    date_str = date_time.strftime('%d/%m/%Y, %H:%M:%S')

    uri = QgsDataSourceUri() # Estas partes do codigo so existem no QGIS, ele usa um interpretador do python "modificado"
    uri.setConnection(POSTGRES_ADDRESS, POSTGRES_PORT, POSTGRES_DBNAME, POSTGRES_USERNAME, POSTGRES_PASSWORD)
    uri.setDataSource('public', 'gslocation', 'geom', aSql=f'session_id = {session_id}')

    layer = QgsVectorLayer(uri.uri(), f'{session_id} - {date_str}', 'postgres')

    if not layer.isValid():
        print('Layer did not load')
    else:
        QgsProject.instance().addMapLayer(layer)

    counter += 1
    if counter == max_sessions:
        break