# pylint: disable="missing-module-docstring"
from mondaydotcom_utils import __version__


# pylint: disable="missing-function-docstring"
def test_version():
    assert __version__ == "0.2"
