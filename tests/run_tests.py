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
# Copyright (c) 2025 Government of Canada
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

from datetime import date, datetime
import unittest

from pywoudc import WoudcClient, date2string


class WoudcClientTest(unittest.TestCase):
    """Test suite for package pywoudc.WoudcClient"""

    def setUp(self):
        """bootstrap"""

        self.client = WoudcClient('https://api.woudc.org')

    def tearDown(self):
        """destroy"""
        pass

    def test_smoke_test(self):
        """test basic properties"""

        self.assertEqual(self.client.url, 'https://api.woudc.org/',
                         'Expected specific URL')

        self.assertEqual(self.client.about,
                         'https://woudc.org/en/data/data-access',
                         'Expected specific about URL')

        self.assertEqual(self.client.limit, 25000,
                         'Expected specific default limit')

    def test_get_metadata(self):
        """test get various requests for metadata"""

        for collection in ['stations', 'contributors']:
            data = self.client.collection_items(collection)

            self.assertTrue(isinstance(data, dict),
                            'Expected specific instance')

            self.assertTrue('type' in data,
                            'Expected GeoJSON header')

            self.assertEqual(data['type'], 'FeatureCollection',
                             'Expected GeoJSON header')

            self.assertTrue('features' in data,
                            'Expected GeoJSON header')

            self.assertTrue(len(data['features']) > 0,
                            'Expected non-empty list')

            data = self.client.collection_items(collection)

    def test_get_data(self):
        """test get data handling"""

        dataset = 'totalozone'

        with self.assertRaises(RuntimeError):
            _ = self.client.get_data(dataset, bbox=[42, -52, 84])

        with self.assertRaises(ValueError):
            _ = self.client.get_data(dataset, datetime_=[date(2000, 11, 11)])

        with self.assertRaises(RuntimeError):
            _ = self.client.get_data(dataset, sortby=['bad', 'asc'])

        data = self.client.get_data(
            'totalozone', datetime_=[datetime(2024, 11, 11), None])

        self.assertTrue(len(data['features']) > 0)

    def test_date2string(self):
        """test date handling"""

        with self.assertRaises(ValueError):
            _ = date2string('2000-10-10', direction='begin')

        with self.assertRaises(ValueError):
            _ = date2string('2001-11-11', direction='end')

        with self.assertRaises(ValueError):
            _ = date2string('2000-10-10 02:22:28')

        self.assertEqual(date2string(date(2000, 11, 30), 'begin'),
                         '2000-11-30T00:00:00Z',
                         'Expected specific date string from date object')

        self.assertEqual(date2string(date(2011, 11, 30), 'end'),
                         '2011-11-30T23:59:59Z',
                         'Expected specific date string from date object')

        self.assertEqual(date2string(
                         datetime(2002, 10, 30, 11, 11, 11)),
                         '2002-10-30T11:11:11Z',
                         'Expected specific date string from datetime object')

        self.assertEqual(date2string(
                         datetime(2011, 11, 30, 12, 12, 12)),
                         '2011-11-30T12:12:12Z',
                         'Expected specific date string from datetime object')


if __name__ == '__main__':
    unittest.main()
