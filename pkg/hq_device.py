"""Device for hqWinterCreditAdapter"""
import functools
from gateway_addon import Device

#from pkg.hq_Property import hq_bool_ro_property, hq_datetime_ro_property
#from pkg.hq_DataClass import hq_config_data
#from pkg.hq_webuser import hq_webuser

#from datetime import datetime, time

#_POLL_INTERVAL = 5 #interval to check if data changed
print = functools.partial(print, flush=True)#allow direct print to log of gateway

class hq_Device(Device):
    """HQ winter Credit Device"""

    def __init__(self, adapter, _id, config):
        """
        Initialize the object
        
        adapter -- Adapter managing this device
        _id -- ID of this device
        config -- contract settings
        """

        Device.__init__(self, adapter, _id,)

        self._type.append('BinarySensor')
        #self.description = 'Hydro Quebec Winter Credit Event 1'#not sure where it'S used
        self.title = _id#This appear in the text bar when adding the device and is the default name of the device
        #self.name = 'Hydro Quebec Winter Credit Event 3'#not sure where it's used
        

       