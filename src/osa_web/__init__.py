"""OSA.Web Streamlit application package."""

import tomllib
from importlib.metadata import version
from pathlib import Path

_pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
if _pyproject.is_file():
    with _pyproject.open("rb") as file:
        __version__ = tomllib.load(file)["project"]["version"]
else:
    __version__ = version("osa-web")
