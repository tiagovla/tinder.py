__title__ = "tinder"
__author__ = "tiagovla"
__version__ = "0.1.0"
__license__ = "MIT"

import logging

from .client import Client

try:
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logging.getLogger(__name__).addHandler(NullHandler())
