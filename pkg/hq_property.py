"""Property for device Hydro Quebec event for Webthings"""

from gateway_addon import Property
from datetime import datetime


class hqProperty(Property):
    """Property type for HQdata"""
    description = None
    
    def __init__(self, device, name):
        """
        Initialize the object
        
        device -- the device this property belongs to
        """
        
        #Force to provide description in child class
        if self.description is None:
            raise NotImplementedError('Sublcasses must define description')

        super().__init__(device, name, self.description)
        

    def set_RO_Value(self, propName, value):
        """
        Set a read-only value
        
        device -- device who own the property
        propName -- property to update
        value -- value of the property
        """

        prop = self.device.find_property(propName)
        prop.set_cached_value_and_notify(value)

class hq_bool_ro_property(hqProperty):
    """Boolean Property Read Only"""

    def __init__(self, device, name):
       """
       Initialize the objects

       name -- name of the property
       """
       self.description={'@type': 'BooleanProperty', 'title': name, 'type': 'boolean', 'readOnly' : True,}#description of the property
       super().__init__(device, name)

    def set_RO_Value(self, propName, value: bool):
        super().set_RO_Value(propName, value)

    def is_active(self, startDate, endDate):
        """
        test if the event is currently active

        startDate -- start date and time of the event
        endDate -- end date and time of the event

        return -- bool
        """
        now = datetime.now()

        if now is None or startDate is None or endDate is None:
            return False
        elif now > startDate and now < endDate:
            return True
        else:
            return False

class hq_float_ro_property(hqProperty):
    """int property, read only"""

    def __init__(self, device, name):
        
        self.description={'title': name, 'type': 'number', 'unit' : "$", 'readOnly' : True,}
        super().__init__(device, name)

    def set_RO_Value(self, propName, value: float):
        super().set_RO_Value(propName, value)

class hq_datetime_ro_property(hqProperty):
    """datetime Property Read Only"""

    def __init__(self, device, name):
        """
        Initialize the object

        name -- name of the property
        """
        self.description={'title': name, 'type': 'string', 'readOnly' : True,}#description of the property
        super().__init__(device, name)    
    
    def set_RO_Value(self, propName, value: datetime):
        """
        modifying the set_RO_Value for datetime object

        value -- value of the property, must be datetime
        """
        #if datetime is none enter an empty date and time
        if value is None:
            value = None#"00/00/0000\n00:00:00"
        else:
            value = value.strftime("%d/%m/%Y\n %H:%M:%S")#TODO:Verify if isoformat could replace strftime
        super().set_RO_Value(propName, value)
"""
#Those class will be disabled since property will only be keep in add-on settings page for now
class hq_minute_rw_property(hqProperty):
    """"""Number property, read and write""""""

    def __init__(self, device, name):
        """"""
        Initialize the object
        
        name -- name of the property
        """"""

        self.description={'@type':'LevelProperty' ,'title': name, 'type': 'number','minimum': 0,}#description of the property
        super().__init__(device)

    def set_RO_Value(self, device, propName, value: int):
        super().set_RO_Value(device, propName, value)
    
"""
