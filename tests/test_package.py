import importlib


def test_package_is_importable():
    module = importlib.import_module("csvscope")
    assert module.__name__ == "csvscope"
