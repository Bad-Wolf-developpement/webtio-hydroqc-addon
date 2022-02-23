"""Hydroqc Consts."""
from dateutil import tz


# Always get the time using HydroQuebec Local Time
HQ_TIMEZONE = tz.gettz("America/Montreal")

LOGGING_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
