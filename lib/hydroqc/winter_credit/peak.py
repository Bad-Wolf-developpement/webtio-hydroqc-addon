"""Class describing a period."""
import datetime

from hydroqc.error import HydroQcWinterCreditError
from hydroqc.winter_credit.timerange import TimeRange
from hydroqc.winter_credit.consts import (
    EST_TIMEZONE,
    MORNING_EVENING,
    DEFAULT_MORNING_PEAK_START,
    DEFAULT_MORNING_PEAK_END,
    DEFAULT_EVENING_PEAK_START,
    DEFAULT_EVENING_PEAK_END,
    DEFAULT_ANCHOR_START_OFFSET,
    DEFAULT_ANCHOR_DURATION,
    DEFAULT_PRE_HEAT_START_OFFSET,
    DEFAULT_PRE_HEAT_END_OFFSET,
)


class Anchor(TimeRange):
    """This class describe a period object."""

    def __init__(self, start_date, end_date, is_critical=False):
        """Period constructor."""
        super().__init__(start_date, end_date, is_critical)


class PreHeat(TimeRange):
    """This class describe a period object."""

    def __init__(self, start_date, end_date, is_critical=False):
        """Period constructor."""
        super().__init__(start_date, end_date, is_critical)


class Peak(TimeRange):
    """This class describe a period object."""

    def __init__(self, date, morning_evening):
        """Period constructor."""
        if morning_evening not in MORNING_EVENING:
            msg = f"Peak type {morning_evening} needs be one of {MORNING_EVENING}"
            raise HydroQcWinterCreditError(msg)
        self._morning_evening = morning_evening
        self._date = date.astimezone(EST_TIMEZONE)
        super().__init__(self.start_date, self.end_date, is_critical=False)
        self._raw_stats = {}

    @property
    def is_morning(self):
        """Return True if it's a morning peak."""
        return self._morning_evening == "morning"

    @property
    def is_evening(self):
        """Return True if it's a evening peak."""
        return self.morning_evening == "evening"

    @property
    def morning_evening(self):
        """Return evening or morning peak value."""
        return self._morning_evening

    @property
    def is_critical(self):
        """Return True peak is critical."""
        return self._is_critical

    def set_critical(self, stats):
        """Save critical stats in the peak and set it as critical."""
        self._is_critical = True
        self._raw_stats = stats

    @property
    def day(self):
        """Get the day, without time, of the peak."""
        return self._date.date()

    @property
    def anchor(self):
        """Get the anchor period of the peak."""
        anchor_start_date = self.start_date - datetime.timedelta(
            hours=DEFAULT_ANCHOR_START_OFFSET
        )
        anchor_end_date = anchor_start_date + datetime.timedelta(
            hours=DEFAULT_ANCHOR_DURATION
        )
        return Anchor(anchor_start_date, anchor_end_date, self.is_critical)

    @property
    def preheat(self):
        """Get the preheat period of the peak."""
        preheat_start_date = self.start_date - datetime.timedelta(
            hours=DEFAULT_PRE_HEAT_START_OFFSET
        )
        preheat_end_date = preheat_start_date + datetime.timedelta(
            hours=DEFAULT_PRE_HEAT_END_OFFSET
        )
        return PreHeat(preheat_start_date, preheat_end_date, self.is_critical)

    @property
    def start_date(self):
        """Get the start date of the peak."""
        if self._morning_evening == "morning":
            start_date = self._date.replace(
                hour=DEFAULT_MORNING_PEAK_START.hour,
                minute=DEFAULT_MORNING_PEAK_START.minute,
                second=DEFAULT_MORNING_PEAK_START.second,
            )
        elif self._morning_evening == "evening":
            start_date = self._date.replace(
                hour=DEFAULT_EVENING_PEAK_START.hour,
                minute=DEFAULT_EVENING_PEAK_START.minute,
                second=DEFAULT_EVENING_PEAK_START.second,
            )
        return start_date

    @property
    def end_date(self):
        """Get the end date of the peak."""
        if self._morning_evening == "morning":
            end_date = self._date.replace(
                hour=DEFAULT_MORNING_PEAK_END.hour,
                minute=DEFAULT_MORNING_PEAK_END.minute,
                second=DEFAULT_MORNING_PEAK_END.second,
            )
        elif self._morning_evening == "evening":
            end_date = self._date.replace(
                hour=DEFAULT_EVENING_PEAK_END.hour,
                minute=DEFAULT_EVENING_PEAK_END.minute,
                second=DEFAULT_EVENING_PEAK_END.second,
            )
        return end_date

    @property
    def credit(self):
        """Get credit save during this peak.

        Return None if the peak is not critical.
        """
        return self._raw_stats.get("montantEffacee")

    @property
    def ref_consumption(self):
        """Get reference consumption during this peak.

        Return None if the peak is not critical.
        """
        return self._raw_stats.get("consoReference")

    @property
    def actual_consumption(self):
        """Get actual consumption during this peak.

        Return None if the peak is not critical.
        """
        return self._raw_stats.get("consoReelle")

    @property
    def saved_consumption(self):
        """Get saved consumption during this peak.

        Return None if the peak is not critical.
        """
        return self._raw_stats.get("consoEffacee")

    @property
    def consumption_code(self):
        """Get code consumption during this peak.

        Return None if the peak is not critical.
        """
        return self._raw_stats.get("codeConso")

    @property
    def is_billed(self):
        """Return True if the winter credit was billed.

        Return None if the peak is not critical.
        """
        return self._raw_stats.get("indFacture")
