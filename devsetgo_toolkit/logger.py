# -*- coding: utf-8 -*-
import logging
import sys

# Get a logger named after the module where this is called
logger = logging.getLogger(__name__)


def setup_logger(level=logging.INFO):
    """
    Sets up the logger with the given log level.

    Parameters:
    level (int): The log level to set for the logger.
    """
    # Set the log level of the logger
    logger.setLevel(level)

    # Check if the logger already has handlers, and if not, add a StreamHandler
    if not logger.handlers:
        # Create a StreamHandler that outputs to the console
        ch = logging.StreamHandler(sys.stdout)  # Explicitly set to stdout
        # Set the log level of the StreamHandler
        ch.setLevel(level)

        # Create a Formatter that formats the log messages
        formatter = logging.Formatter(
            "toolkit | %(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        # Set the Formatter of the StreamHandler to the created Formatter
        ch.setFormatter(formatter)

        # Add the StreamHandler to the logger
        logger.addHandler(ch)

    # Prevent messages from being passed to the root logger's handlers
    logger.propagate = False


# Set up the logger with the default log level
setup_logger()
