import json
import os
import sys
import logging

log = logging.getLogger(__name__)

""" Class for handling of configs

Currently only loading.

TODO: Saving? Overwrite?
"""


def path():
    pkgPath = os.path.dirname(sys.modules["plotter"].__file__)
    return pkgPath + "/"


def load_config(path: str):
    log.debug(f"Loading config file {path}")
    with open(path, "r") as f:
        config = json.load(f)
        return config
