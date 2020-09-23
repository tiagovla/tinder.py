__title__ = 'tinder'
__author__ = 'tiagovla'
__version__ = '0.1.0'
__license__ = 'MIT'

from .client import Client
import logging

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
