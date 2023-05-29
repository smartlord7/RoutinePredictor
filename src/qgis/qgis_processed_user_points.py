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

import pandas as pd

"""
This script reads a user's sequence data from a text file and creates QGIS vector layers to display the movement between consecutive points in the sequence. Each vector layer represents a line connecting two points, with an arrow symbol indicating the direction of movement.

The script assumes the availability of QGIS and its Python API.

Usage:
- Set the value of `USER_ID` to the user's ID.
- Set the value of `PATH_DATA` to the directory path containing the user's sequence data.
- Ensure that the QGIS interpreter is configured correctly to execute the script.

Output:
- QGIS vector layers representing the movement between consecutive points in the user's sequence.

"""

USER_ID = 353
PATH_DATA = 'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\user_sequences\\' # Complete path because of QGis Interpreter
EXTENSION_TEXT = '.txt'
PATH_USER_DATA = PATH_DATA + f'user_{USER_ID}_sequence' + EXTENSION_TEXT

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
file = open(PATH_USER_DATA, 'r')

max_sessions = 4000
counter = 0

prev = None

for index, line in enumerate(file.readlines()):
    vals = line.strip().split(',')
    day = int(vals[0])
    lat = float(vals[1])
    lon = float(vals[2])

    if prev is None:
        prev = (day, lat, lon)
        continue

    layer = QgsVectorLayer('LineString?crs=epsg:4326', f'{index} - {weekdays[day]}', 'memory')
    layer.renderer().symbol().setWidth(1.0)

    pr = layer.dataProvider()

    start_point = QgsPointXY(prev[2], prev[1])
    end_point = QgsPointXY(lon, lat)


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
            "head_length": "1.5",
            "head_thickness": "1.5",
            "head_type": "0",
            "arrow_type": "0",
            "is_curved": "1",
            "arrow_start_width": "1",
            "color": "blue"
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

    prev = (day, lat, lon)