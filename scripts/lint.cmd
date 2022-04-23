poetry run mypy --ignore-missing-imports mondaydotcom_utils/
poetry run isort --check --diff mondaydotcom_utils/ tests/
poetry run black --check mondaydotcom_utils/ tests/
poetry run pylint mondaydotcom_utils/ tests/
poetry run safety check 
poetry run bandit -r mondaydotcom_utils/
