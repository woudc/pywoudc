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

import csv
import json
import logging
import shapefile
from StringIO import StringIO
import zipfile

from owslib.etree import etree
from owslib.wfs import WebFeatureService

LOGGER = logging.getLogger(__name__)


class WoudcClient(object):
    """constructor"""

    def __init__(self):
        """initializer"""

        self.url = 'http://geo.woudc.org/ows'
        self.outputformat = 'application/json; subtype=geojson'

        LOGGER.info('Contacting %s', self.url)
        self.server = WebFeatureService(self.url, '1.1.0')

        LOGGER.info('Getting supported formats')
        operation = self.server.getOperationByName('GetFeature')
        self.formats = operation.parameters['outputFormat']['values']

    def set_outputformat(self, outputformat):
        """set outputformat for responses"""

        if outputformat not in self.formats:
            msg = 'Invalid outputformat \'%s\'' % self.outputformat
            LOGGER.exception(msg)
            raise ValueError(msg)
        LOGGER.info('Setting outputformat to %s', outputformat)
        self.outputformat = outputformat

    def get_station_metadata(self, station_id=None):
        """get WOUDC station metadata"""

        LOGGER.info('Fetching station metadata')
        return self._get_metadata('stations')

    def get_instrument_metadata(self, instrument_id=None):
        """get WOUDC instrument metadata"""

        LOGGER.info('Fetching instrument metadata')
        return self._get_metadata('instruments')

    def get_contributor_metadata(self, contributor_id=None):
        """get WOUDC contributor metadata"""

        LOGGER.info('Fetching contributor metadata')
        return self._get_metadata('contributors')

    def get_data(self, typename, **kwargs):
        """generic design pattern to download WOUDC metadata"""

        constraints = []
        sort_property = None
        sort_descending = False

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

        if self.outputformat not in self.formats:
            msg = 'Invalid outputformat \'%s\'' % self.outputformat
            LOGGER.exception(msg)
            raise ValueError(msg)

        LOGGER.debug('Fetching data from server')
        features = self.server.getfeature(typename=typename, maxfeatures=2,
                                          outputFormat=self.outputformat)

        LOGGER.debug('Processing response')
        output = self._handle_response(features)

        if self.outputformat == 'application/json; subtype=geojson':
            if sort_property is not None:
                output.sort(key=lambda e: e['properties'][sort_property],
                            reverse=sort_descending)
        return output

    def _get_metadata(self, typename):
        """generic design pattern to download WOUDC metadata"""

        if self.outputformat not in self.formats:
            msg = 'Invalid outputformat \'%s\'' % self.outputformat
            LOGGER.exception(msg)
            raise ValueError(msg)

        LOGGER.debug('Fetching data from server')
        features = self.server.getfeature(typename=typename, maxfeatures=2,
                                          outputFormat=self.outputformat)

        LOGGER.debug('Processing response')
        return self._handle_response(features)

    def _handle_response(self, features):
        """generic design pattern to decode WOUDC response formats"""

        if self.outputformat == 'application/json; subtype=geojson':
            msg = 'Serializing json object'
            output = json.loads(features.read())['features']
        elif 'xml' in self.outputformat:
            msg = 'Serializing etree.Element object'
            output = etree.fromstring(features.read())
        elif 'csv' in self.outputformat.lower():
            msg = 'Serializing csv.DictReader object'
            with open(StringIO(features)) as csvfile:
                output = csv.DictReader(csvfile)
        elif 'shape' in self.outputformat.lower():
            msg = 'Serializing shapefile.Reader object'
            with zipfile.ZipFile(features) as zipf:
                for name in zipf.namelist():
                    if '.shp' in name:
                        shp = StringIO(zipf.read(name))
                    if '.dbf' in name:
                        dbf = StringIO(zipf.read(name))
                    if '.shx' in name:
                        shx = StringIO(zipf.read(name))
            output = shapefile.Reader(shp=shp, dbf=dbf, shx=shx)
        else:
            msg = 'Unsupported format %s' % self.outputformat
            LOGGER.exception(msg)
            raise NotImplementedError(msg)

        LOGGER.debug(msg)
        return output
