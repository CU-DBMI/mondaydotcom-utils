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

## Cleaning, Linting, and Testing with Dagger

Development may be assisted using [Dagger](https://docs.dagger.io/) and related files within this repo. Use the following steps to get started:

1. [Install Dagger](https://docs.dagger.io/1200/local-dev)
1. Open a terminal and navigate to the directory of this source.
1. Use `dagger project update` to populate dependencies.
1. Use the following to clean, lint, or test with Dagger:
    - Clean: `dagger do clean`
    - Lint: `dagger do lint`
    - Test: `dagger do test`

## Acknowlegements

Quite a bit of heavy lifting against the Monday.com API is done using the [ProdPerfect](<https://github.com/ProdPerfect/monday> package) SDK package.

Much of the linting and great pep8, pulled from a [cookiecutter template](https://github.com/timothycrosley/cookiecutter-python).
