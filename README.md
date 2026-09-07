[![Build Status](https://github.com/woudc/pywoudc/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/woudc/pywoudc/actions)

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

### pip

Install latest stable version from [PyPI](https://pypi.org/project/pywoudc).

```bash
pip3 install pywoudc
```

### From source
Install latest development version.

```bash
python3 -m venv pywoudc
cd pywoudc
. bin/activate
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

# get a GeoJSON dict of all deployments
client.get_metadata('deployments')
```

## Development

```bash
python3 -m venv pywoudc
cd pywoudc
source bin/activate
git clone https://github.com/woudc/pywoudc.git
cd pywoudc
pip3 install .
pip3 install ".[dev]"
```

### Running Tests

```bash
python3 tests/run_tests.py
```

## Releasing

```bash
# create release (x.y.z is the release version)
vi pyproject.toml  # update [project]/version
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 -m build
twine upload dist/*

# publish release on GitHub (https://github.com/woudc/pywoudc/releases/new)

# bump version back to dev
vi pyproject.toml  # update [project]/version
git commit -am 'back to dev'
git push origin master
```

### Code Conventions

pywoudc code conventions are as per
[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/woudc/pywoudc/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
