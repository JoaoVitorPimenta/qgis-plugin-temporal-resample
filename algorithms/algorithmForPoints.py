import pandas as pd
from scipy.interpolate import interp1d
from qgis.PyQt.QtCore import QVariant
from qgis.core import (QgsVectorLayer,
                       QgsField,
                       QgsFeature,
                       QgsPointXY,
                       QgsGeometry,
                       QgsProcessingException)

def executePluginForPoints (layer,field,delta,method,dateTimeFormat,order):
    """Use all functions needed to execute
    the Plugin for a point Layer."""
    listX,listY,dateTimeList = extractCoordAndDatetime (layer,field)
    df = create_dataframe (listX,listY,dateTimeList,dateTimeFormat)
    dfReindexed = reIndexDataFrame(df,delta)
    dfInterpolated = interpolateDataFrame(dfReindexed,method,order)
    dfResampled = resampleDataFrame(dfInterpolated,delta)
    layerResampled = createLayerWithFeatures (dfResampled)
    return layerResampled
def extractCoordAndDatetime (layer,field):
    """Extract the coordinates
    and Datetime of each feacture in the layer."""
    datas = layer.getFeatures()
    dateTimeList = []
    listX = []
    listY = []
    for data in datas:
        dateTime = data[field[0]]
        dateTimeList.append(dateTime)
        X = data.geometry().asPoint().x()
        Y = data.geometry().asPoint().y()
        listX.append(X)
        listY.append(Y)
    return listX,listY,dateTimeList
def create_dataframe (listX,listY,dateTimeList,dateTimeFormat):
    """Transform the coordinates
    in a dataframe with datetime as a index."""
    dateTimeIndex = pd.to_datetime(dateTimeList,format=dateTimeFormat)
    df = pd.DataFrame({'y': listY, 'x': listX},
                      columns=['y', 'x'],
                      index=dateTimeIndex)
    return df
def reIndexDataFrame (df,deltaDateTime):
    """Reindex the DataFrame with the
    all DateTimes that pass through the input delta."""
    dfWD = df[~df.index.duplicated(keep='first')]
    newIndex = pd.date_range(start=dfWD.index.min(),
                             end=dfWD.index.max(),
                             freq=deltaDateTime +'ms')
    dfReindexed = dfWD.reindex(newIndex)
    return dfReindexed
def interpolateDataFrame (df,method,order):
    """Interpolate the coordinates in new
    DateTime index, using the method given."""
    if method in ('spline', 'polynomial'):
        if method == 'polynomial':
            if order % 2 == 0:
                raise QgsProcessingException(
                    'The order of the polynomial cannot be even for orders greater than 2, for the polynomial method.'
                )
        dfInterpolated = df.interpolate(method=method,order=order)
        return dfInterpolated
    dfInterpolated = df.interpolate(method=method)
    return dfInterpolated
def resampleDataFrame (df, deltaDateTime):
    """Resample the DataFrame, to just use
    the coordinates that pass through deltaDateTime."""
    dfResampled = df.resample(deltaDateTime+'ms',origin='start').asfreq()
    return dfResampled
def createLayerWithFeatures (df):
    """Create a QGIS Layer, with the DataFrame
    Resampled, add features to this layer and
    the DateTime, as a attribute."""
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
