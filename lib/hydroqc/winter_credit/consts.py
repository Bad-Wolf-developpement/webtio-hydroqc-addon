"""Constants module for winter credits."""
import datetime

import pytz


DEFAULT_ANCHOR_START_OFFSET = 5
DEFAULT_ANCHOR_DURATION = 3
DEFAULT_EVENT_REFRESH_SECONDS = 300
DEFAULT_PRE_HEAT_START_OFFSET = 3
DEFAULT_PRE_HEAT_END_OFFSET = 0
DEFAULT_MORNING_PEAK_START = datetime.time(6, 0, 0)
DEFAULT_MORNING_PEAK_END = datetime.time(9, 0, 0)
DEFAULT_EVENING_PEAK_START = datetime.time(16, 0, 0)
DEFAULT_EVENING_PEAK_END = datetime.time(20, 0, 0)
MORNING_EVENING = ("morning", "evening")

EST_TIMEZONE = pytz.timezone("Canada/Eastern")
