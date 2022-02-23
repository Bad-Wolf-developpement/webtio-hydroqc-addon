"""HydroQc Error Module."""


class HydroQcError(Exception):
    """Base HydroQc Error."""


class HydroQcHTTPError(HydroQcError):
    """HTTP HydroQc Error."""


class HydroQcAnnualError(HydroQcError):
    """Annual HydroQc Error."""


class HydroQcWinterCreditError(HydroQcError):
    """Winter Credit HydroQc Error."""
