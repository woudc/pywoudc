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

import json
import logging

from owslib.wfs import WebFeatureService

LOGGER = logging.getLogger(__name__)


class WoudcClient(object):
    """constructor"""

    def __init__(self):
        """initializer"""

        self.url = 'http://geo.woudc.org/ows'
        self.outputformat = 'application/json; subtype=geojson'
        self.maxfeatures = 25000

        LOGGER.info('Contacting %s', self.url)
        self.server = WebFeatureService(self.url, '1.1.0')

    def get_station_metadata(self):
        """get WOUDC station metadata"""

        LOGGER.info('Fetching station metadata')
        return self._get_metadata('stations')

    def get_instrument_metadata(self):
        """get WOUDC instrument metadata"""

        LOGGER.info('Fetching instrument metadata')
        return self._get_metadata('instruments')

    def get_contributor_metadata(self):
        """get WOUDC contributor metadata"""

        LOGGER.info('Fetching contributor metadata')
        return self._get_metadata('contributors')

    def get_data(self, typename, **kwargs):
        """generic design pattern to download WOUDC observations"""

        constraints = []
        sort_property = None
        sort_descending = False
        startindex = 0
        output = []

        LOGGER.info('Downloading dataset %s', typename)

        LOGGER.info('Assembling query parameters')
        for key, value in kwargs.iteritems():
            if key == 'bbox':
                bbox = value
            if key == 'time':
                time = value
            if key == 'property_name':
                property_name = value
            if key == 'property_value':
                property_value = value

            if key == 'sortby':
                sort_property = value
            if key == 'descending':
                sort_descending = value

        LOGGER.info('Fetching observations')
        # page download and assemble single list of JSON features
        while True:
            LOGGER.info('Fetching features %d - %d',
                         startindex, startindex+self.maxfeatures)

            payload = self.server.getfeature(
                typename=typename,
                startindex=startindex,
                maxfeatures=self.maxfeatures,
                outputFormat=self.outputformat).read()

            LOGGER.debug('Processing response')
            if payload.isspace():
                LOGGER.debug('Empty response. Exiting')
                break

            features = json.loads(payload)['features']
            len_features = len(features)

            LOGGER.debug('Found %d features', len_features)

            output.extend(features)

            if len_features < self.maxfeatures:
                break

            startindex = startindex + self.maxfeatures

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
