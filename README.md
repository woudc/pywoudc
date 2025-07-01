[![Build Status](https://github.com/woudc/pywoudc/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/woudc/pywoudc/actions)
[![Downloads this month on PyPI](https://img.shields.io/pypi/dm/pywoudc.svg)](http://pypi.python.org/pypi/pywoudc)
[![Latest release](https://img.shields.io/pypi/v/pywoudc.svg)](http://pypi.python.org/pypi/pywoudc)

# pywoudc

High level package providing Pythonic access to [WOUDC](https://woudc.org/en/data/data-access)
data services.

## Overview

The World Ozone and Ultraviolet Radiation Data Centre (WOUDC) is one of six
World Data Centres which are part of the
[Global Atmosphere Watch](http://www.wmo.int/gaw) programme of the World
Meteorological Organization.

The WOUDC archive is made available via
[OGC APIs](https://api.woudc.org).  These APIs are publically
available and can be used with any environment and / or software supporting
the OGC API standards.  pywoudc provides a high level library using Python idioms
(API, data structures) which provides Python implementations a simple,
straightforward bridge without requiring intimate knowledge of the OGC
standards.

## Installation

### Requirements
- [Python](https://www.python.org) 3 and above
- [virtualenv](https://virtualenv.pypa.io)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during pywoudc installation.

### Installing pywoudc

```bash
# setup virtualenv
python3 -m venv --system-site-packages pywoudc
cd pywoudc
source bin/activate

# clone codebase and install
git clone https://github.com/woudc/pywoudc.git
cd pywoudc
pip3 install .
```

## Running

From the command line:

```bash
pywoudc --version

# get all stations
pywoudc stations

# get station report
pywoudc station <woudc_id>

# get instruments
pywoudc instruments

# get instrument report
pywoudc instrument <instrument_id>
```

## Using the API

```python
from pywoudc import WoudcClient
client = WoudcClient()

# get a GeoJSON dict of all contributors
client.get_metadata('contributors')

# get a GeoJSON dict of all stations
client.get_metadata('stations')

# get a GeoJSON dict of all instruments
client.get_metadata('instruments')
```

## Development

```bash
virtualenv pywoudc
cd pywoudc
source bin/activate
git clone https://github.com/woudc/pywoudc.git
cd pywoudc
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```

### Running tests

```bash
# via setuptools
python3 setup.py test
# manually
python3 tests/run_tests.py
```

### Code Conventions

pywoudc code conventions are as per
[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/woudc/pywoudc/issues
