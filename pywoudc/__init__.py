# =================================================================
#
# Terms and Conditions of Use
#
# Unless otherwise noted, computer program source code of this
# distribution # is covered under Crown Copyright, Government of
# Canada, and is distributed under the MIT License.
#
# The Canada wordmark and related graphics associated with this
# distribution are protected under trademark law and copyright law.
# No permission is granted to use them outside the parameters of
# the Government of Canada's corporate identity program. For
# more information, see
# http://www.tbs-sct.gc.ca/fip-pcim/index-eng.asp
#
# Copyright title to all 3rd party software distributed with this
# software is held by the respective copyright holders as noted in
# those files. Users are asked to read the 3rd Party Licenses
# referenced with those assets.
#
# Copyright (c) 2014 Government of Canada
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

__version__ = '0.1.0'

import datetime
import json
import logging

from owslib import fes
from owslib.wfs import WebFeatureService

LOGGER = logging.getLogger(__name__)


class WoudcClient(object):
    """WOUDC Client"""

    def __init__(self):
        """
        Initialize a WOUDC Client.

        @rtype: pywoudc.WoudcClient
        @return: instance of pywoudc.WoudcClient
        """

        self.url = 'http://geo.woudc.org/ows'
        self.outputformat = 'application/json; subtype=geojson'
        self.maxfeatures = 25000

        LOGGER.info('Contacting %s', self.url)
        self.server = WebFeatureService(self.url, '1.1.0')

    def get_station_metadata(self):
        """
        Download WOUDC station metadata

        @rtype: dict
        @return: dictionary of GeoJSON payload
        """

        LOGGER.info('Fetching station metadata')
        return self._get_metadata('stations')

    def get_instrument_metadata(self):
        """
        Download WOUDC instrument metadata

        @rtype: dict
        @return: dictionary of GeoJSON payload
        """

        LOGGER.info('Fetching instrument metadata')
        return self._get_metadata('instruments')

    def get_contributor_metadata(self):
        """
        Download WOUDC contributors metadata

        @rtype: dict
        @return: dictionary of GeoJSON payload
        """

        LOGGER.info('Fetching contributor metadata')
        return self._get_metadata('contributors')

    def get_data(self, typename, **kwargs):
        """
        Download WOUDC observations

        @type bbox: list
        @param bbox: bounding box spatial filter (C{minx, miny, maxx, maxy})
        @type temporal: list
        @param temporal: temporal filter list (C{start}, C{end})
                         accepts the following types:
                             - C{datetime.date}
                             - C{datetime.datetime}
                             - string date (e.g. C{2012-10-30})
                             - string datetime (e.g. C{2012-10-30 11:11:11})
        @type property_name: string
        @param property_name: Property name to filter query
        @type property_value: string
        @param property_value: Property value / literal of property_name
        @type sort_property: string
        @param sort_property: Property to sort results
                              (default C{instance_datetime})
        @type sort_descending: bool
        @param sort_descending: whether to sort descending (default=C{False}).
                                Applied if C{sort_property} is specified

        @rtype: list
        @return: list of WOUDC observations GeoJSON payload
        """

        constraints = []
        variables = []
        filter_string = None
        bbox = None
        temporal = None
        property_name = None
        property_value = None
        sort_property = None
        sort_descending = False
        startindex = 0
        output = []

        LOGGER.info('Downloading dataset %s', typename)

        LOGGER.debug('Assembling query parameters')
        for key, value in kwargs.iteritems():
            if key == 'bbox':
                bbox = value
            if key == 'temporal':
                temporal = value
            if key == 'property_name':
                property_name = value
            if key == 'property_value':
                property_value = str(value)
            if key == 'variables':
                variables = value
            if key == 'sortby':
                sort_property = value
            if key == 'descending':
                sort_descending = value

        LOGGER.debug('Assembling constraints')
        if property_name is not None and property_value is not None:
            constraints.append(fes.PropertyIsEqualTo(property_name,
                                                     property_value))
        if bbox is not None:
            LOGGER.debug('Setting spatial constraint')
            constraints.append(fes.BBox(bbox))

        if temporal is not None:
            LOGGER.info('Setting temporal constraint')
            temporal_start, temporal_end = temporal.split('/')

            temporal_start, temporal_end = __temporal_dt2string(temporal)

            constraints.append(fes.PropertyIsBetween(
                'instance_datetime', temporal_start, temporal_end))

        if constraints:
            LOGGER.debug('Combining constraints')
            flt = fes.FilterRequest()
            if len(constraints) == 1:
                LOGGER.debug('Single constraint')
                filter_string = flt.setConstraint(constraints[0],
                                                  tostring=True)
            if len(constraints) > 1:
                LOGGER.debug('Multiple constraints')
                filter_string = flt.setConstraintList([constraints],
                                                      tostring=True)

        LOGGER.info('Fetching observations')
        LOGGER.info('Filters:')
        LOGGER.info('bbox: %r', bbox)
        LOGGER.info('temporal: %r', temporal)
        LOGGER.info('attribute query: %r = %r', property_name, property_value)

        # page download and assemble single list of JSON features
        while True:
            LOGGER.debug('Fetching features %d - %d',
                         startindex, startindex + self.maxfeatures)

            payload = self.server.getfeature(
                typename=typename,
                startindex=startindex,
                propertyname=variables,
                maxfeatures=self.maxfeatures,
                filter=filter_string,
                outputFormat=self.outputformat).read()

            LOGGER.debug('Processing response')
            if payload.isspace():
                LOGGER.debug('Empty response. Exiting')
                break

            try:
                features = json.loads(payload)['features']
            except ValueError:
                msg = 'Query produced no results'
                LOGGER.info(msg)
                return None

            len_features = len(features)

            LOGGER.debug('Found %d features', len_features)

            output.extend(features)

            if len_features < self.maxfeatures:
                break

            startindex = startindex + self.maxfeatures

        LOGGER.info('Found %d features', len(output))

        if sort_property is not None:
            LOGGER.info('Sorting response by %s', sort_property)
            output.sort(key=lambda e: e['properties'][sort_property],
                        reverse=sort_descending)

        return output

    def _get_metadata(self, typename):
        """generic design pattern to download WOUDC metadata"""

        LOGGER.debug('Fetching data from server')
        features = self.server.getfeature(typename=typename,
                                          outputFormat=self.outputformat)

        LOGGER.debug('Processing response')
        return json.loads(features.read())['features']


def __temporal_dt2string(self, temporal):
    """
    Utility function to convert list of start time / end time
    to list of strings (private)

    @type temporal: list
    @param temporal: list of datetime.date objects
    """

    return [
        __date_to_string(temporal[0], 'begin'),
        __date_to_string(temporal[1], 'end')
    ]


def __date_to_string(dateval, direction='begin'):
    """Utility function (private)"""

    date_as_string = None

    if direction == 'begin':
        default_time = '00:00:00'
    elif direction == 'end':
        default_time = '23:59:59'
    else:
        raise ValueError('span value must be begin or end')

    if isinstance(dateval, str):
        if len(dateval) == 10:  # date
            date_as_string = '%s %s' % (dateval, direction)
        elif len(dateval) > 10:  # datetime
            date_as_string = dateval
    elif isinstance(dateval, datetime.date):
        date_as_string = dateval.strftime('%Y-%m-%d %s' % default_time)
    elif isinstance(dateval, datetime.datetime):
        date_as_string = dateval.strftime('%Y-%m-%d %H:%M:%S')

    return date_as_string
