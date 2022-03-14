"""Property for device Hydro Quebec event for Webthings"""

from datetime import datetime

from gateway_addon import Property


class HQProperty(Property):
    """Property type for HQdata"""
    def __init__(self, device, id, description=None):
        """
        Initialize the object

        device -- the device this property belongs to
        """

        # Force to provide description in child class
        if description is None:
            raise NotImplementedError("Subclasses must define description")

        super().__init__(device, id, description)

    def set_ro_value(self, prop_name, value):
        """
        Set a read-only value

        device -- device who own the property
        prop_name -- property to update
        value -- value of the property
        """
        prop = self.device.find_property(prop_name)
        prop.set_cached_value_and_notify(value)


class HQBoolRoProperty(HQProperty):
    """Boolean Property Read Only"""

    def __init__(self, device, id, name):
        """
        Initialize the objects

        name -- name of the property
        """
        super().__init__(device, id, {
            "@type": "BooleanProperty",
            "title": name,
            "type": "boolean",
            "readOnly": True,
        })

    def set_ro_value(self, prop_name, value: bool):
        super().set_ro_value(prop_name, value)

    def is_active(self, start_date, end_date):
        """
        test if the event is currently active

        start_date -- start date and time of the event
        end_date -- end date and time of the event

        return -- bool
        """
        now = datetime.now()

        if None in (now, start_date, end_date):
            return False

        if start_date < now < end_date:
            return True

        return False


class HQFloatRoProperty(HQProperty):
    """int property, read only"""

    def __init__(self, device, id, name):

        super().__init__(device, id, {
            "title": name,
            "type": "number",
            "unit": "$",
            "readOnly": True,
        })

    def set_ro_value(self, prop_name, value: float):
        super().set_ro_value(prop_name, value)


class HQDatetimeRoProperty(HQProperty):
    """datetime Property Read Only"""

    def __init__(self, device, id, name):
        """
        Initialize the object

        name -- name of the property
        """
        super().__init__(device, id, {
            "title": name,
            "type": "string",
            "readOnly": True,
        })

    def set_ro_value(self, prop_name, value: datetime):
        """
        modifying the set_ro_value for datetime object

        value -- value of the property, must be datetime
        """
        # if datetime is none enter an empty date and time
        if value is None:
            datetime_representation = "0000-00-00\n00:00:00"
        else:
            datetime_representation = value.isoformat(sep="\n", timespec="seconds")
        super().set_ro_value(prop_name, value)
