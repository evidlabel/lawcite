import pytest
import lawcite

def test_package_import():
    assert lawcite.__version__ == "0.1.0"

def test_cli_module_importable():
    from lawcite.cli.main import main
    assert callable(main)
