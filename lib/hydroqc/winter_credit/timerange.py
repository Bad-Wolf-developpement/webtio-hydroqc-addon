"""Class describing an interval of time."""


class TimeRange:
    """This class describe an interval of time."""

    def __init__(self, start, end, is_critical):
        """Period constructor."""
        self._start_date = start
        self._end_date = end
        self._is_critical = is_critical

    @property
    def start_date(self):
        """Get start date of the time range."""
        return self._start_date

    @property
    def end_date(self):
        """Get end date of the time range."""
        return self._end_date

    @property
    def is_critical(self):
        """Get critical status of the time range."""
        return self._is_critical

    def __repr__(self):
        """Make object repr more readable."""
        if self.is_critical:
            repr_str = f"<{self.__class__.__name__} - {self.start_date} - critical>"
        else:
            repr_str = f"<{self.__class__.__name__} - {self.start_date}>"
        return repr_str
