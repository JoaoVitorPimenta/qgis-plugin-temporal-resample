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

from qgis.core import QgsProcessingException
from datetime import datetime

def verifyDateTimeFormatInput (layer,field,dateTimeFormat):
    '''
    Checks if the date time input is in a standardized format
    '''
    features = layer.getFeatures()
    for feature in features:
        date = feature[field]
        try:
            datetime.strptime(date, dateTimeFormat)
        except Exception as exc:
            raise QgsProcessingException('The algorithm stopped on the feature '+str(feature.id())+' because it is not in the indicated datetime format') from exc

def verifyPolynomialOrderForPolynomialMethod(method,order):
    if method == 'polynomial':
        if order % 2 == 0:
            raise QgsProcessingException(
                'The order of the polynomial cannot be even for orders greater than 2, for the polynomial method.'
            )

def verifyPolynomialOrderForSplineMethod(method,order):
    if method == 'spline':
        if order == 0:
            raise QgsProcessingException(
                'The order of the spline cannot be 0, for the spline method.'
            )
