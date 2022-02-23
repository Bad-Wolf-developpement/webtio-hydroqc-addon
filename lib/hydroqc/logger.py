"""Logging module."""
import logging

from hydroqc.error import HydroQcError
from hydroqc.consts import LOGGING_LEVELS


def get_logger(name, log_level="INFO", parent=None):
    """Build logger."""
    if log_level is None:
        log_level = "INFO"
    if log_level.upper() not in LOGGING_LEVELS:
        raise HydroQcError(
            f"""Bad logging level. " "Should be in {", ".join(LOGGING_LEVELS)}"""
        )
    logging_level = getattr(logging, log_level.upper())
    root_logger = logging.getLogger(name="hydroqc")
    if parent:
        root_logger = root_logger.getChild(parent)
    logger = root_logger.getChild(name)
    logger.setLevel(logging_level)
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    if len(logger.handlers) == 0 and parent is None:
        logger.addHandler(console_handler)
    return logger
