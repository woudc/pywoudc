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

__version__ = '0.3.1'

from copy import deepcopy
from datetime import date, datetime
import logging
from typing import Union

import click
from owslib.ogcapi.features import Features
from prettytable import PrettyTable

LOGGER = logging.getLogger(__name__)


class WoudcClient(Features):
    """WOUDC Client"""

    def __init__(self, url='https://api.woudc.org', timeout=30):
        """
        Initialize a WOUDC Client.

        :returns: instance of pywoudc.WoudcClient
        """

        super().__init__(url)

        self.about = 'https://woudc.org/en/data/data-access'
        """The About Data Access page"""

        self.limit = 1000
        """The default limit of features to return"""

        LOGGER.info(f'Contacting {self.url}')
        self.server = Features(self.url, timeout=self.timeout)
        """The main WOUDC server"""

    def get_stations(self) -> dict:
        """
        Download WOUDC station metadata

        :returns: `dict` of GeoJSON payload
        """

        LOGGER.info('Fetching station metadata')
        return self.collection_items('stations', limit=self.limit)

    def get_station(self, woudc_id: str = None, gaw_id: str = None) -> dict:
        """
        Download WOUDC station metadata for a single station.  Note
        that one of `woudc_id` or `gaw_id` is required.

        :param woudc_id: `str` of WOUDC platform identifier
        :param gaw_id: `str` of GAW identifier

        :returns: `dict` of GeoJSON payload
        """

        property_filters = {}

        if None in [woudc_id, gaw_id] and None not in [woudc_id, gaw_id]:
            msg = 'One of WOUDC platform or GAW identifier required'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        if woudc_id is not None:
            property_filters['woudc_id'] = woudc_id

        if gaw_id is not None:
            property_filters['gaw_id'] = gaw_id

        LOGGER.info('Fetching station metadata')
        return self.collection_items('stations', **property_filters)

    def get_instruments(self) -> dict:
        """
        Download WOUDC instrument metadata

        :returns: `dict` of GeoJSON payload
        """

        LOGGER.info('Fetching instrument metadata')
        return self.collection_items('instruments', limit=self.limit)

    def get_contributors(self) -> dict:
        """
        Download WOUDC contributor metadata

        :returns: `dict` of GeoJSON payload
        """

        LOGGER.info('Fetching contributor metadata')
        return self.collection_items('contributors', limit=self.limit)

    def get_metadata(self, metadata_type: str) -> dict:
        """
        Download WOUDC metadata

        :param type: type of metadata (stations, instruments, contributors)

        :returns: `dict` of GeoJSON feature collection
        """

        if metadata_type == 'stations':
            return self.get_stations()
        elif metadata_type == 'instruments':
            return self.get_instruments()
        elif metadata_type == 'contributors':
            return self.get_contributors()

    def get_data(self, collection: str,
                 datetime_: Union[Union[date, datetime, None], list[date, datetime, None]] = None,  # noqa
                 bbox: list = [],
                 limit: int = 1000,
                 offset: int = 0,
                 filters: dict = {},
                 sortby: list = []) -> dict:
        """
        Download WOUDC observations

        :param collection: `str` of dataset name
        :param bbox: a list representing a bounding box spatial
                     filter (`minx, miny, maxx, maxy`)
        :param datetime_: a list (time period start/end) which accepts the
                          following types:

                          - :py:class:`datetime.date`
                          - :py:class:`datetime.datetime`
                          - :py:class:`None`
        :param filters: `dict` of key-value pairs of property names and
                        values.  Constructs exclusive search
        :param limit: `int` of maximum features
        :param offset: `int` of start position of query results
        :param sortby: `list` of the property on which
                       to sort results and `str` of sort order of response
                       (``asc`` or ``desc``)

        :returns: `dict` of WOUDC observations GeoJSON payload
        """

        params = {
            'collection_id': collection
        }
        feature_collection = {
            'type': 'FeatureColletion',
            'features': []
        }

        if collection == 'ozonesonde':
            limit = 100

        datetime2 = None

        LOGGER.debug('Assembling query parameters')
        if bbox:
            params['bbox'] = bbox

        if datetime_ is not None:
            if len(datetime_) != 2:
                msg = 'datetime_ must have a list of begin/end'
                raise ValueError(msg)

            LOGGER.info('Setting temporal extent')
            start = date2string(datetime_[0], 'begin')
            end = date2string(datetime_[1], 'end')
            datetime2 = f'{start}/{end}'

            params['datetime_'] = datetime2

        if 'filters':
            params.update(filters)

        if sortby:
            if sortby[1] not in ['asc', 'desc']:
                raise ValueError('sort order must be asc or desc')
            params['sortby'] = sortby

        LOGGER.info(f'Query parameters: {params}')

        LOGGER.info(f'Downloading dataset {collection}')
        # page download and assemble single list of JSON features
        while True:
            LOGGER.debug(f'Fetching features {offset} - {offset + limit}')

            params2 = deepcopy(params)
            params2['limit'] = limit
            params2['offset'] = offset

            features = self.collection_items(**params2)
            LOGGER.debug(f'Features: {features}')

            if len(features['features']) == 0:
                LOGGER.info('Query produced no results')
                break

            LOGGER.debug(f"Found {len(features['features'])} features")

            feature_collection['features'].extend(features['features'])

            if len(feature_collection['features']) >= features['numberMatched']:  # noqa
                break

            offset += limit

        len_feature_collection = len(feature_collection['features'])
        LOGGER.info(f'Found {len_feature_collection} total features')

        if sortby:
            LOGGER.info(f'Sorting response by {sortby[0]}')
            feature_collection['features'].sort(
                key=lambda e: e['properties'][sortby[0]],
                reverse=(sortby[1] == 'desc'))

        feature_collection['numberMatched'] = len_feature_collection
        feature_collection['numberReturned'] = len_feature_collection

        return feature_collection


def date2string(dateval: Union[date, datetime, None],
                direction: str = 'begin'):
    """Utility function (private)"""

    date_as_string = None

    if dateval is None:
        return '..'

    if direction == 'begin':
        default_time = '00:00:00'
    elif direction == 'end':
        default_time = '23:59:59'
    else:
        raise ValueError('Direction value must be begin or end')

    if isinstance(dateval, datetime):
        date_as_string = dateval.strftime('%Y-%m-%dT%H:%M:%SZ')
    elif isinstance(dateval, date):
        date_as_string = f"{dateval.strftime('%Y-%m-%d')}T{default_time}Z"
    else:
        raise ValueError('Expecting date or datetime type')

    return date_as_string


@click.group()
@click.version_option(version=__version__)
def cli():
    pass


@click.command()
@click.pass_context
def stations(ctx):
    """Get WOUDC station metdata"""

    field_names = ['woudc_id', 'gaw_id', 'name', 'active', 'url']

    client = WoudcClient()
    data = client.collection_items('stations', limit=client.limit)

    pt = PrettyTable()
    pt.align = 'l'
    pt.field_names = field_names

    for item in data['features']:
        row = []
        for fn in field_names:
            if fn == 'url':
                woudc_id = item['id']
                row.append(f'https://woudc.org/en/data/stations/{woudc_id}')
            else:
                row.append(item['properties'][fn])
        pt.add_row(row)

    click.echo(pt.get_string())


@click.command()
@click.pass_context
@click.argument('woudc_id')
def station(ctx, woudc_id):
    """Get WOUDC station report"""

    field_names = ['woudc_id', 'gaw_id', 'name', 'active', 'url']

    client = WoudcClient()
    data = client.collection_items(
        'stations',
        woudc_id=woudc_id,
        limit=client.limit)

    pt = PrettyTable()
    pt.align = 'l'
    pt.field_names = field_names

    for item in data['features']:
        row = []
        for fn in field_names:
            if fn == 'url':
                row.append(f'https://woudc.org/en/data/stations/{woudc_id}')
            else:
                row.append(item['properties'][fn])
        pt.add_row(row)

    click.echo(pt.get_string())


cli.add_command(stations)
cli.add_command(station)
