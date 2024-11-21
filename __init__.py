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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'João Vitor Pimenta'
__date__ = '2024-11-08'
__copyright__ = '(C) 2024 by João Vitor Pimenta'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load TemporalResample class from file TemporalResample.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .TemporalResample import TemporalResamplePlugin
    return TemporalResamplePlugin()
