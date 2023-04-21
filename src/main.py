# import sqlalchemy as db
import pandas as pd
import psycopg2

"""
Este ficheiro já nao é usado, foi o primeiro que criei e dps deixei. Mas podes ver algumas coisas aqui
"""


# Database connection configurations
POSTGRES_ADDRESS = 'localhost'
POSTGRES_PORT = '5432'
POSTGRES_USERNAME = 'leopoldo'
POSTGRES_PASSWORD = '1234'
POSTGRES_DBNAME = 'suscity'

db_uri = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_ADDRESS}:{POSTGRES_PORT}/{POSTGRES_DBNAME}'



"""
conn = psycopg2.connect(database=POSTGRES_DBNAME, user=POSTGRES_USERNAME,
                        password=POSTGRES_PASSWORD, host=POSTGRES_ADDRESS,
                        port=POSTGRES_PORT)

conn.autocommit = True
cursor = conn.cursor()
"""

sessions = pd.read_sql_query('SELECT * FROM session', db_uri)
osmlocations = pd.read_sql_query('SELECT * FROM osmlocation', db_uri)

#Dict of user:[session list]
users = sessions['user_id'].unique()
user_session_dict = {}

print(f'There are {len(users)} users.')

#Get user that has the most session_ids locations
for index, user in enumerate(users):
    print(f'{index} - User {user}')
    user_sessions = sessions.loc[sessions['user_id'] == user]['session_id'].unique()

    for session_id in user_sessions:
        session_locations = osmlocations.loc[osmlocations['session_id'] == session_id]

        #Check if we have the location data of this session
        if not session_locations.empty:
            #Add to dict
            if user_session_dict.get(user) is None:
                user_session_dict[user] = [session_locations['session_id'].values[0]]
            else:
                user_session_dict[user].append(session_locations['session_id'].values[0])


users = user_session_dict

for user, s in users.items():
    print(f'User {user} has {len(s)} sessions.')

#Get user with most amount of sessions
max_user = max(users, key=lambda x:len(users.get(x)))
max_user_sessions = users[max_user]  # Ids of the user sessions!!

for session_id in max_user_sessions:

    #location_points = osmlocations.loc[osmlocations['session_id'] == session_id]

    uri = QgsDataSourceUri()
    uri.setConnection(POSTGRES_ADDRESS, POSTGRES_PORT, POSTGRES_DBNAME, POSTGRES_USERNAME, POSTGRES_PASSWORD)
    uri.setDataSource('public', 'osmlocation', 'geom', aSql=f'session_id = {session_id}')

    layer = QgsVectorLayer(uri.uri(), f'session - {session_id}', 'postgres')

    if not layer.isValid():
        print('Layer did not load')
    else:
        QgsProject.instance().addMapLayer(layer)
