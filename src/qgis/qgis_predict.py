import os.path
import pandas as pd
import numpy as np

def create_qgis_arrow(start, end, color, layer_name):
    layer = QgsVectorLayer('LineString?crs=epsg:4326', layer_name, 'memory')
    layer.renderer().symbol().setWidth(1.0)

    pr = layer.dataProvider()

    start_point = QgsPointXY(start[1], start[0])
    end_point = QgsPointXY(end[1], end[0])

    # Create lines
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
            "color": color
        }
    )
    layer.renderer().symbol().changeSymbolLayer(0, arrow)

    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)

    if not layer.isValid():
        print('Layer did not load')
    else:
        QgsProject.instance().addMapLayer(layer)


USER_ID = 353
PATH_DATA = 'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\user_sequences\\' # Complete path because of QGis Interpreter
TMP_DATA = 'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\tmp\\'
EXTENSION_TEXT = '.txt'
PATH_USER_DATA = PATH_DATA + f'user_{USER_ID}_sequence' + EXTENSION_TEXT
TMP_USER_DATA = TMP_DATA + f'{USER_ID}' + EXTENSION_TEXT

# Check if tmp_file does not exist
# !! TODO
if not os.path.exists(TMP_USER_DATA):
    tmp_index = 3
else:
    with open(TMP_USER_DATA, 'r') as tmp_file:
        tmp_index = int(tmp_file.readline().strip())

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

prev = None

lst = []

with open(PATH_USER_DATA, 'r') as file:
    for index, line in enumerate(file.readlines()):
        vals = line.strip().split(',')
        day = int(vals[0])
        lat = float(vals[1])
        lon = float(vals[2])

        lst.append([lat, lon])

lst = np.array(lst)

start = lst[tmp_index - 1, :]
end_true = lst[tmp_index, :]
#end_pred = predict()

create_qgis_arrow(start, end_true, 'red', f'Index: {tmp_index} - True Position')



with open(TMP_USER_DATA, 'w') as tmp_file:
    tmp_file.write(str(tmp_index + 1))

