# import sqlalchemy as db
import pandas as pd
import psycopg2

"""
Este foi o ultimo que tive a modificar, basicamente é usar outras tabelas para ir buscar o ponto inicial e final das sessoes
Uso o user 464 pq é o que tem mais sessoes
Isto nao está acabado!!!!!!!!!!
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

# Aqui venho buscar ao ficheiro/tabela sessions, e mais á frente ao processed_sessions,
# Pq o processed_sessions nao tem informação sobre o user_id, apenas o daily_user_id
# Entao vou buscar as sessoes referentes ao user ao ficheiro session e dps vou buscar os pontos iniciais e finais á tabela processed_session (que ja os tem)
sessions = pd.read_sql_query(f'SELECT * FROM session WHERE user_id = {user_id} ORDER BY start_time', conn)

# Unique sessions this user has
user_sessions = list(sessions['session_id'])

max_sessions = 5
counter = 0

for index, session_id in enumerate(user_sessions):
    processed_session = pd.read_sql_query(f'SELECT * FROM processed_session WHERE session_id = {session_id}', conn)

    if processed_session.empty:
        print('empty')
        continue

    session_start_lat = processed_session['lat_start'].values[0]
    session_start_lon = processed_session['lon_start'].values[0]
    session_end_lat = processed_session['lat_end'].values[0]
    session_end_lon = processed_session['lon_end'].values[0]

    session_start_time = processed_session['seconds_start'].values[0]

    date_time = pd.to_datetime(session_start_time, unit='s', origin='unix')
    date_str = date_time.strftime('%d/%m/%Y, %H:%M:%S')

    layer = QgsVectorLayer('Point?crs=epsg:4326', f'{session_id} - {date_str}', 'memory')
    pr = layer.dataProvider()

    feat1 = QgsFeature()
    feat2 = QgsFeature()

    start_point = QgsPointXY(session_start_lon, session_start_lat)
    end_point = QgsPointXY(session_end_lon, session_end_lat)

    feat1.setGeometry(QgsGeometry.fromPointXY(start_point))
    feat2.setGeometry(QgsGeometry.fromPointXY(end_point))

    pr.addFeatures([feat1, feat2])

    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)

    if not layer.isValid():
        print('Layer did not load')
    else:
        QgsProject.instance().addMapLayer(layer)

    counter += 1
    if counter == max_sessions:
        break