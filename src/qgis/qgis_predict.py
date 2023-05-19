import os
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
PATH_DATA = 'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\user_predictions\\' # Complete path because of QGis Interpreter
TMP_DATA = 'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\tmp\\'
EXTENSION_TEXT = '.txt'
TMP_USER_DATA = TMP_DATA + f'{USER_ID}' + EXTENSION_TEXT

predict_path = PATH_DATA + f'{USER_ID}_pred.txt'
true_path = PATH_DATA + f'{USER_ID}_true.txt'


# Check if tmp_file does not exist
if not os.path.exists(TMP_USER_DATA):
    tmp_index = 1
else:
    with open(TMP_USER_DATA, 'r') as tmp_file:
        tmp_index = int(tmp_file.readline().strip())

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

with open(true_path, 'r') as file:
    lines = file.readlines()

    # The start is always equal to the TRUE position
    start_line = lines[tmp_index - 1]
    vals = start_line.strip().split(',')
    start = [float(vals[0]), float(vals[1])]

    true_line = lines[tmp_index]
    vals = true_line.strip().split(',')
    end_true = [float(vals[0]), float(vals[1])]

    file.close()

with open(predict_path, 'r') as file:
    lines = file.readlines()

    pred_line = lines[tmp_index]
    vals = pred_line.strip().split(',')
    end_pred = [float(vals[0]), float(vals[1])]

    file.close()

create_qgis_arrow(start, end_true, 'red', f'Index: {tmp_index} - True Position')
create_qgis_arrow(start, end_pred, 'blue', f'Index: {tmp_index} - Predicted Position')

with open(TMP_USER_DATA, 'w') as tmp_file:
    tmp_file.write(str(tmp_index + 1))
