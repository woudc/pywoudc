[![Build Status](https://travis-ci.org/woudc/pywoudc.png?branch=master)](https://travis-ci.org/woudc/pywoudc) [![Build status](https://ci.appveyor.com/api/projects/status/02koln2pe4ap5kvd/branch/master?svg=true)](https://ci.appveyor.com/project/tomkralidis/pywoudc)
[![Downloads this month on PyPI](https://img.shields.io/pypi/dm/pywoudc.svg)](http://pypi.python.org/pypi/pywoudc)
[![Latest release](https://img.shields.io/pypi/v/pywoudc.svg)](http://pypi.python.org/pypi/pywoudc)
[![License](https://img.shields.io/github/license/woudc/pywoudc.svg)](https://github.com/woudc/pywoudc)

# pywoudc

High level package providing Pythonic access to [WOUDC](http://geo.woudc.org)
data services.

## Overview

The World Ozone and Ultraviolet Radiation Data Centre (WOUDC) is one of six
World Data Centres which are part of the
[Global Atmosphere Watch](http://www.wmo.int/gaw) programme of the World
Meteorological Organization.

The WOUDC archive is made available via
[OGC Web Services](http://geo.woudc.org).  These web services are publically
available and can be used within a GIS environment and / or software supporting
the OGC standards.  pywoudc provides a high level library using Python idioms
(API, data structures) which provides Python implementations a simple,
straightforward bridge without requiring intimate knowledge of the OGC
standards.

## Installation

### Requirements

pywoudc requires Python 2.7 or greater.  pywoudc works with Python 3.

## Dependencies

pywoudc requires the [OWSLib](https://geopython.github.io/OWSLib) library.
Installing via `pip` or `easy_install` will ensure that OWSlib is installed
as part of pywoudc.

### Installing the Package

```bash
# via pip
pip install pywoudc
# via easy_install
easy_install pywoudc
```

## Using the API

```python
from pywoudc import WoudcClient
client = WoudcClient()
```

## Development

```bash
virtualenv pywoudc
cd pywoudc
source bin/activate
git clone https://github.com/woudc/pywoudc.git
cd pywoudc
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running tests

```bash
# via distutils
python setup.py test
# manually
python tests/run_tests.py
```

### Code Conventions

pywoudc code conventions are as per
[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/woudc/pywoudc/issues
