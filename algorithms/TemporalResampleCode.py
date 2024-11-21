import pandas as pd
import scipy as sp
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsVectorLayer,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry)

def extractCoordAndDatetime (layer,field):
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

#reindex dataframe
#interpolate dataframe
# resample dataframe
def reIndexDataFrame (df,deltaDateTime):
    dfWD = df[~df.index.duplicated(keep='first')]
    newIndex = pd.date_range(start=dfWD.index.min(), end=dfWD.index.max(), freq=deltaDateTime +'ms')
    dfReindexed = dfWD.reindex(newIndex)
    return dfReindexed

def interpolateDataFrame (df,method):
    dfInterpolated = df.interpolate(method=method)
    return dfInterpolated

def resampleDataFrame (df, deltaDateTime):
    dfResampled = df.resample(deltaDateTime+'ms',origin='start').asfreq()
    return dfResampled
    
def createLayerWithFeatures (df):
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
    listX,listY,dateTimeList = extractCoordAndDatetime (layer,field)
    df = create_dataframe (listX,listY,dateTimeList,format)
    dfReindexed = reIndexDataFrame(df,delta)
    dfInterpolated = interpolateDataFrame(dfReindexed,method)
    dfResampled = resampleDataFrame(dfInterpolated,delta)
    layerResampled = createLayerWithFeatures (dfResampled)
    return layerResampled