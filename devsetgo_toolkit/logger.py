# -*- coding: utf-8 -*-
"""
This module sets up a logger named "Devsetgo Toolkit" with a level of DEBUG.
It also sets up a StreamHandler that outputs to the console, with a level of DEBUG.
The StreamHandler uses a Formatter to format the log messages.

use:
from devsetgo_toolkit.logger import logger

logger.info("This is an info message")
logger.debug("This is a debug message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
logger.exception("This is an exception message")

"""

import logging

# TODO: Need to use app that is import libray to set the logger
# Get a logger named "Devsetgo Toolkit"
logger = logging.getLogger("Devsetgo Toolkit")
# Set the log level of the logger to DEBUG
logger.setLevel(logging.DEBUG)

# Create a StreamHandler that outputs to the console
ch = logging.StreamHandler()
# Set the log level of the StreamHandler to DEBUG
ch.setLevel(logging.DEBUG)

# Create a Formatter that formats the log messages as "time - name - level - message"
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Set the Formatter of the StreamHandler to the created Formatter
ch.setFormatter(formatter)

# Add the StreamHandler to the logger
logger.addHandler(ch)
