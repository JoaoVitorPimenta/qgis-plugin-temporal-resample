# -*- coding: utf-8 -*-

"""
/***************************************************************************
 TemporalResample
                                 A QGIS plugin
 This plugin resamples a vector layer based on a delta time
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-11-08
        copyright            : (C) 2024 by João Vitor Pimenta
        email                : jvpjoaopimenta@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'João Vitor Pimenta'
__date__ = '2024-11-08'
__copyright__ = '(C) 2024 by João Vitor Pimenta'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingParameterField,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterDuration,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterNumber)
from .algorithms.algorithmForPoints import executePluginForPoints
from .exceptions.inputExceptions import verifyDateTimeFormatInput

class TemporalResampleAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    VLAYERRESAMPLED = 'VLAYERRESAMPLED'
    VLAYER = 'VLAYER'
    FIELD = 'FIELD'
    FORMAT ='FORMAT'
    DELTATIME = 'DELTATIME'
    METHOD = 'METHOD'
    ORDER = 'ORDER'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.VLAYER,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.FIELD,
                self.tr('Field with datetime'),
                parentLayerParameterName='VLAYER',
                type=QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.FORMAT,
                self.tr('Date time format'),
                defaultValue = '%Y-%m-%d %H:%M:%S'
            )
        )

        self.addParameter(
            QgsProcessingParameterDuration(
                self.DELTATIME,
                self.tr('Delta time'),
                defaultValue = 1
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METHOD,
                self.tr('Method'),
                options = [
                           'nearest',
                           'zero',
                           'linear',
                           'quadratic',
                           'cubic',
                           'polynomial',
                           'barycentric',
                           'time',
                           'slinear',
                           'spline'],
                usesStaticStrings = True
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.ORDER,
                'Order number',
                type=QgsProcessingParameterNumber.Integer
                                        )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.VLAYERRESAMPLED,
                self.tr('Resampled layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.VLAYER, context)
        field = self.parameterAsString(parameters, self.FIELD, context)
        format = self.parameterAsString(parameters, self.FORMAT, context)
        deltatime = self.parameterAsString(parameters, self.DELTATIME, context)
        method = self.parameterAsString(parameters, self.METHOD, context)
        order = self.parameterAsInt(parameters, self.ORDER, context)

        verifyDateTimeFormatInput(source,field,format)

        layerResampled = executePluginForPoints(source,field,deltatime,method,format,order)

        (lR, dest_id) = self.parameterAsSink(parameters,
                                              self.VLAYERRESAMPLED,
                                              context,
                                              layerResampled.fields(),
                                              layerResampled.wkbType(),
                                              layerResampled.sourceCrs(),
                                              layerOptions=["ENCODING=UTF-8"])

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / layerResampled.featureCount() if layerResampled.featureCount() else 0
        features = layerResampled.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break

            # Add a feature in the sink
            lR.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.VLAYERRESAMPLED: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Temporal Resample'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return self.tr("""
        <html>
            <body>
                <p>       
        This tool interpolates points based on a datetime field, an interpolation method and a temporal spacing        
                </p>
                <p>
        <strong>Input Layer: </strong>The layer with each feature representing a point in time.
        <strong>Field with datetime: </strong>The field with datetime values.
        <strong>Date time format: </strong>The datetime format that the field values ​​are in.
        <strong>Delta time: </strong>The new time difference in features after resampling.
        <strong>Method: </strong>Mathematical method for interpolating coordinates.
        <strong>Order: </strong>If the method is slinear or polynomial, the order of the function.
        <strong>Output layer: </strong>The path to the resampled layer.
                       
        For more information about methods, see: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.interpolate.html
                </p>
            </body>
        </html>
                    """)

    def createInstance(self):
        return TemporalResampleAlgorithm()
