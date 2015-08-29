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
# Copyright (c) 2015 Government of Canada
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

import datetime
import unittest

from owslib.feature.wfs110 import WebFeatureService_1_1_0

from pywoudc import WoudcClient, temporal2string


class WoudcClientTest(unittest.TestCase):
    """Test suite for package pywoudc.WoudcClient"""

    def setUp(self):
        """bootstrap"""
        pass

    def tearDown(self):
        """destroy"""
        pass

    def test_smoke_test(self):
        """test basic properties"""

        client = WoudcClient()

        self.assertEqual(client.url, 'http://geo.woudc.org/ows',
                         'Expected specific URL')

        self.assertEqual(client.outputformat,
                         'application/json; subtype=geojson',
                         'Expected specific default outputformat')

        self.assertEqual(client.maxfeatures, 25000,
                         'Expected specific default maxfeatures')

        self.assertTrue(isinstance(client.server, WebFeatureService_1_1_0),
                        'Expected specific instance')

    def test_get_data(self):
        """test get data handling"""

        dataset = 'totalozone'
        bad_bbox = [42, -52, 84]

        client = WoudcClient()

        with self.assertRaises(ValueError):
            client.get_data(dataset, bbox=bad_bbox)

        with self.assertRaises(ValueError):
            client.get_data(dataset, sort_descending='true')

    def test_temporal_to_string(self):
        """test temporal extent handling"""

        te_list = ['2000-10-10', '2001-11-11']
        self.assertEqual(temporal2string(te_list),
                         ['2000-10-10 00:00:00', '2001-11-11 23:59:59'],
                         'Expected specific temporal extent (strings)')

        te_list = ['2000-10-10 02:22:28', '2001-11-11 11:33:24']
        self.assertEqual(temporal2string(te_list),
                         ['2000-10-10 02:22:28', '2001-11-11 11:33:24'],
                         'Expected specific temporal extent (datetimes)')

        te_list = [datetime.date(2000, 11, 30), datetime.date(2011, 11, 30)]
        self.assertEqual(temporal2string(te_list),
                         ['2000-11-30 00:00:00', '2011-11-30 23:59:59'],
                         'Expected specific temporal extent (dates)')

        te_list = [datetime.datetime(2002, 10, 30, 11, 11, 11),
                   datetime.datetime(2011, 11, 30, 12, 12, 12)]
        self.assertEqual(temporal2string(te_list),
                         ['2002-10-30 11:11:11', '2011-11-30 12:12:12'],
                         'Expected specific temporal extent (datetimes)')

        te_list_strings = temporal2string(te_list)
        self.assertTrue(isinstance(te_list_strings, list),
                        'Expected specific instance')
        self.assertEqual(len(te_list_strings), 2,
                         'Expected specific list length')

if __name__ == '__main__':
    unittest.main()
