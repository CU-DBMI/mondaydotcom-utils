#!/bin/bash
set -euxo pipefail

poetry run isort mondaydotcom_utils/ tests/
poetry run black mondaydotcom_utils/ tests/
