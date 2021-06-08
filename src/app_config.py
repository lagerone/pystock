import os

_base_dir_path = os.path.abspath(os.path.curdir)
_DEFAULT_DATA_PATH = os.path.join(_base_dir_path, ".ticker_data")

TICKER_DATA_PATH = os.getenv("TICKER_DATA_PATH", _DEFAULT_DATA_PATH)
