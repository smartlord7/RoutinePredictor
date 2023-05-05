# import sqlalchemy as db
import json

import pandas as pd
import psycopg2

#from src.db_setup import db_setup

"""
Este foi o ultimo que tive a modificar, basicamente é usar outras tabelas para ir buscar o ponto inicial e final das sessoes
Uso o user 464 pq é o que tem mais sessoes
Isto nao está acabado!!!!!!!!!!
"""

PATH_DATA = '../data/'
EXTENSION_TEXT = '.txt'
PATH_USER_SESSIONS = PATH_DATA + 'user_sessions_number' + EXTENSION_TEXT


# Database connection configurations
#db_config, db_uri, conn = db_setup()


#Sorry mas isto n corre no QGIS
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



user_id = 468  # Change this to whatever user, user with most sessions is 464
weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Aqui venho buscar ao ficheiro/tabela sessions, e mais á frente ao processed_sessions,
# Pq o processed_sessions nao tem informação sobre o user_id, apenas o daily_user_id
# Entao vou buscar as sessoes referentes ao user ao ficheiro session e dps vou buscar os pontos iniciais e finais á tabela processed_session (que ja os tem)
sessions = pd.read_sql_query(f'SELECT * FROM session WHERE user_id = {user_id} ORDER BY start_time', conn)

# Unique sessions this user has
user_sessions = list(sessions['session_id'])

max_sessions = 15
counter = 0

for index, session_id in enumerate(user_sessions):
    processed_session = pd.read_sql_query(f'SELECT * FROM processed_session WHERE session_id = {session_id}', conn)
    print(index)
    if processed_session.empty:
        print('empty')
        continue

    session_start_lat = processed_session['lat_start'].values[0]
    session_start_lon = processed_session['lon_start'].values[0]
    session_end_lat = processed_session['lat_end'].values[0]
    session_end_lon = processed_session['lon_end'].values[0]

    if session_start_lat == session_end_lat and session_start_lon == session_end_lon:
        print('same lat and lon')
        continue

    session_start_time = processed_session['seconds_start'].values[0]

    date_time = pd.to_datetime(session_start_time, unit='s', origin='unix')
    date_str = date_time.strftime('%d/%m/%Y, %H:%M:%S')

    week_index = date_time.weekday()
    if week_index > 4:
        # Session is on Saturday or Sunday
        continue

    #layer = QgsVectorLayer('Points?crs=epsg:4326', f'{session_id} - {weekdays[week_index]} - {date_str}', 'memory')
    layer = QgsVectorLayer('LineString?crs=epsg:4326', f'{session_id} - {weekdays[week_index]} - {date_str}', 'memory')
    layer.renderer().symbol().setWidth(1.0)

    #object_methods = [method_name for method_name in dir(layer.renderer().symbol())
                      #if callable(getattr(object, method_name))]
    #sprint(object_methods)

    pr = layer.dataProvider()

    start_point = QgsPointXY(session_start_lon, session_start_lat)
    end_point = QgsPointXY(session_end_lon, session_end_lat)


    #Create points
    #startPointFeat = QgsFeature()
    #endPointFeat = QgsFeature()
    #startPointFeat.setGeometry(QgsGeometry.fromPointXY(start_point))
    #endPointFeat.setGeometry(QgsGeometry.fromPointXY(end_point))
    #pr.addFeatures([startPointFeat, endPointFeat])
    #start_point = QgsPoint(start_point)  # Convert QgsPointXY into QgsPoint
    #end_point = QgsPoint(end_point)


    #Create lines
    lineFeat = QgsFeature()
    line = QgsGeometry.fromPolylineXY([start_point, end_point])
    lineFeat.setGeometry(line)

    pr.addFeature(lineFeat)

    # Make the symbols an arrow
    arrow = QgsArrowSymbolLayer.create(
        {
            "arrow_width": "1",
            "head_length": "1",
            "head_thickness": "1",
            "head_type": "0",
            "arrow_type": "0",
            "is_curved": "1",
            "arrow_start_width": "1",
            "color": "red"
        }
    )
    layer.renderer().symbol().changeSymbolLayer(0, arrow)

    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)

    if not layer.isValid():
        print('Layer did not load')
    else:
        QgsProject.instance().addMapLayer(layer)

    counter += 1
    if counter == max_sessions:
        break