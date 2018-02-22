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
# Copyright (c) 2016 Government of Canada
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

__version__ = '0.1.9'

import datetime
import json
import logging

from owslib import fes
from owslib.wfs import WebFeatureService

LOGGER = logging.getLogger(__name__)


class WoudcClient(object):
    """WOUDC Client"""

    def __init__(self, url='https://geo.woudc.org/ows', timeout=30):
        """
        Initialize a WOUDC Client.

        :returns: instance of pywoudc.WoudcClient
        """

        self.url = url
        """The URL of the WOUDC data service"""

        self.timeout = timeout
        """Time (in seconds) after which requests should timeout"""

        self.about = 'https://woudc.org/about/data-access.php'
        """The About Data Access page"""

        self.outputformat = 'application/json; subtype=geojson'
        """The default outputformat when requesting WOUDC data"""

        self.maxfeatures = 25000
        """The default limit of records to return"""

        LOGGER.info('Contacting %s', self.url)
        self.server = WebFeatureService(self.url, '1.1.0',
                                        timeout=self.timeout)
        """The main WOUDC server"""

        try:
            mf = int(self.server.constraints['DefaultMaxFeatures'].values[0])
            self.maxfeatures = mf
        except KeyError:
            LOGGER.info('Using default maxfeatures')

    def get_station_metadata(self, raw=False):
        """
        Download WOUDC station metadata

        :param raw: a boolean specifying whether to return the raw GeoJSON
                    payload as a string (default is False)
        :returns: dictionary of GeoJSON payload
        """

        LOGGER.info('Fetching station metadata')
        return self._get_metadata('stations', raw)

    def get_instrument_metadata(self, raw=False):
        """
        Download WOUDC instrument metadata

        :param raw: a boolean specifying whether to return the raw GeoJSON
                    payload as a string (default is False)
        :returns: dictionary of GeoJSON payload
        """

        LOGGER.info('Fetching instrument metadata')
        return self._get_metadata('instruments', raw)

    def get_contributor_metadata(self, raw=False):
        """
        Download WOUDC contributors metadata

        :param raw: a boolean specifying whether to return the raw GeoJSON
                    payload as a string (default is False)
        :returns: dictionary of GeoJSON payload
        """

        LOGGER.info('Fetching contributor metadata')
        return self._get_metadata('contributors', raw)

    def get_data(self, typename, **kwargs):
        """
        Download WOUDC observations

        :param bbox: a list representing a bounding box spatial
                     filter (`minx, miny, maxx, maxy`)
        :param temporal: a list of two elements representing a time period
                         (start, end) which accepts the following types:

                          - :py:class:`datetime.date`
                          - :py:class:`datetime.datetime`
                          - string date (e.g. ``2012-10-30``)
                          - string datetime (e.g. ``2012-10-30 11:11:11``)

        :param property_name: a string representing the property name to apply
                              as filter against
        :param property_value: a string representing the value which filters
                               against `property_name`
        :param variables: a list of variables to return
                          as part of the response (default returns all)
        :param sort_property: a string representing the property on which
                              to sort results (default ``instance_datetime``)
        :param sort_order: a string representing sort order of response
                           (``asc`` or ``desc``).  Default is ``asc``.
                           Applied if `sort_property` is specified

        :returns: list of WOUDC observations GeoJSON payload
        """

        constraints = []
        variables = '*'
        filter_string = None
        bbox = None
        temporal = None
        property_name = None
        property_value = None
        sort_property = None
        sort_order = 'asc'
        startindex = 0
        features = None
        feature_collection = None
        sort_descending = False

        LOGGER.info('Downloading dataset %s', typename)

        LOGGER.debug('Assembling query parameters')
        for key, value in kwargs.items():
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
            if key == 'sort_order':
                sort_order = value

        LOGGER.debug('Assembling constraints')
        if property_name is not None and property_value is not None:
            constraints.append(fes.PropertyIsEqualTo(property_name,
                                                     property_value))
        if bbox is not None:
            if not isinstance(bbox, list) or len(bbox) != 4:
                raise ValueError('bbox must be list of minx, miny, maxx, maxy')

            LOGGER.debug('Setting spatial constraint')
            constraints.append(fes.BBox(bbox))

        if temporal is not None:
            if not isinstance(temporal, list) or len(temporal) != 2:
                msg = 'temporal must be list of start date, end date'
                raise ValueError(msg)

            LOGGER.info('Setting temporal constraint')
            temporal_start = date2string(temporal[0], 'begin')
            temporal_end = date2string(temporal[1], 'end')

            constraints.append(fes.PropertyIsBetween(
                'instance_datetime', temporal_start, temporal_end))

        if sort_order not in ['asc', 'desc']:
            raise ValueError('sort_order must be asc or desc')
        else:
            if sort_order == 'desc':
                sort_descending = True

        if variables != '*':
            if not isinstance(variables, list):
                raise ValueError('variables must be list')

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
                features = json.loads(payload)
            except ValueError:
                msg = 'Query produced no results'
                LOGGER.info(msg)
                return None

            len_features = len(features['features'])

            LOGGER.debug('Found %d features', len_features)

            if feature_collection is None:
                feature_collection = features
            else:
                feature_collection['features'].extend(features['features'])

            if len_features < self.maxfeatures:
                break

            startindex = startindex + self.maxfeatures

        len_feature_collection = len(feature_collection['features'])
        LOGGER.info('Found %d total features', len_feature_collection)

        if sort_property is not None:
            LOGGER.info('Sorting response by %s', sort_property)
            feature_collection['features'].sort(
                key=lambda e: e['properties'][sort_property],
                reverse=sort_descending)

        return feature_collection

    def _get_metadata(self, typename, raw=False):
        """generic design pattern to download WOUDC metadata"""

        LOGGER.debug('Fetching data from server')
        features = self.server.getfeature(typename=typename,
                                          outputFormat=self.outputformat)

        LOGGER.debug('Processing response')
        if raw:
            LOGGER.info('Emitting raw GeoJSON response')
            return features.read()
        LOGGER.info('Emitting GeoJSON features as list')
        return json.loads(features.read())


def date2string(dateval, direction='begin'):
    """Utility function (private)"""

    date_as_string = None

    if direction == 'begin':
        default_time = '00:00:00'
    elif direction == 'end':
        default_time = '23:59:59'
    else:
        raise ValueError('direction value must be begin or end')

    if isinstance(dateval, str):
        if len(dateval) == 10:  # date
            date_as_string = '%s %s' % (dateval, default_time)
        elif len(dateval) > 10:  # datetime
            date_as_string = dateval
    elif isinstance(dateval, datetime.datetime):
        date_as_string = dateval.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dateval, datetime.date):
        date_as_string = '%s %s' % (dateval.strftime('%Y-%m-%d'), default_time)

    return date_as_string
