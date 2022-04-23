# mondaydotcom-utils

A collection of Monday.com utilities, many specific to our use.

## Getting Started

This uses the `poetry` instead of setuptools. Install it with pip.

    pip install poetry


## To Install

TODO consider PyPI for this but until so,

    pip install git+https://github.com/CUHealthAI/mondaydotcom-utils.git

## Building

To test:

    pytest

To build: 

    poetry build

## Acknowlegements

Quite a bit of heavy lifting against the Monday.com API is done using the (ProdPerfect)[https://github.com/ProdPerfect/monday package. 

Much of the linting and great pep8, pulled from a [cookiecutter template](https://github.com/timothycrosley/cookiecutter-python).
