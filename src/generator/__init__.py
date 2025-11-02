"""Generator subpackage."""

import logging
import sys


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the gallery generator.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("exposure")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove any existing handlers
    logger.handlers.clear()

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    # Formatter that matches current output style (no timestamp by default)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Create module-level logger instance
logger = logging.getLogger("exposure")
