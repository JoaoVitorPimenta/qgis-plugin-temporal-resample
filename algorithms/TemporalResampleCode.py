import pandas as pd
import scipy as sp
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsVectorLayer,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry)

def extract_coord_and_datetime (layer,field):
    datas = layer.getFeatures()
    dateTimeList = []
    listX = []
    listY = []
    for data in datas:
        dateTime = (data[field[0]])
        dateTimeList.append(dateTime)
        X = data.geometry().asPoint().x()
        Y = data.geometry().asPoint().y()
        listX.append(X)
        listY.append(Y)
    return listX,listY,dateTimeList

def create_dataframe (listX,listY,dateTimeList,format):
    dateTimeIndex = pd.to_datetime(dateTimeList,format=format)
    df = pd.DataFrame({'y': listY, 'x': listX}, columns=['y', 'x'],index=dateTimeIndex)
    return df

def processDataFrame (df,deltaDateTime,method):
    dfWD = df[~df.index.duplicated(keep='first')]
    newIndex = pd.date_range(start=dfWD.index.min(), end=dfWD.index.max(), freq=deltaDateTime +'ms')
    dfReindexed = dfWD.reindex(newIndex)
    dfInterpolated = dfReindexed.interpolate(method=method)
    dfResampled = dfInterpolated.resample(deltaDateTime+'ms',origin='start').asfreq()
    return dfResampled
    
def create_layer (df):
    rLayer = QgsVectorLayer("Point?crs=EPSG:4326", "resampledLayer", "memory")
    pr = rLayer.dataProvider()

    pr.addAttributes([
        QgsField("DateTime", QVariant.String)
    ])
    rLayer.updateFields()

    for idx, row in df.iterrows():
        feature = QgsFeature()
        point = QgsPointXY(row['x'], row['y'])
        feature.setGeometry(QgsGeometry.fromPointXY(point))
        feature.setAttributes([row.name.strftime('%Y-%m-%d %H:%M:%S')])
        pr.addFeature(feature)

    rLayer.updateExtents()
    return rLayer

def executePluginForPoints (layer,field,delta,method,format):
    listX,listY,dateTimeList = extract_coord_and_datetime (layer,field)
    df = create_dataframe (listX,listY,dateTimeList,format)
    dfPreprocessed = processDataFrame(df,delta,method)
    layerResampled = create_layer (dfPreprocessed)
    return layerResampled