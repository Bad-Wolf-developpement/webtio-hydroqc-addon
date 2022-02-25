"""Device for hqWinterCreditAdapter"""
from distutils.debug import DEBUG
import functools
from tempfile import TemporaryFile
from gateway_addon import Device
from hydroqc.webuser import WebUser
import hydroqc.error as HQerror
import asyncio

#from pkg.hq_Property import hq_bool_ro_property, hq_datetime_ro_property
#from pkg.hq_DataClass import hq_config_data
#from pkg.hq_webuser import hq_webuser

#from datetime import datetime, time

#TODO: work with loop asyncio

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
        #TODO:
        #-fix error: 2022-02-24 18:47:22.972 ERROR  : Error getting thing description for thing with id hydroqc-garage: Error: Unable to find thing with id: hydroqc-garage
        #at /home/node/webthings/gateway/build/webpack:/src/models/things.js:268:1 when we delete the device
        
        #setting the log level
        if self.adapter.verbose:
            log_level = "DEBUG"
        else:
            log_level = None

        self._type.append('BinarySensor')
        self.description = 'Hydro Quebec Winter Credit Event 1'#not sure where it'S used
        self.title = _id#This appear in the text bar when adding the device and is the default name of the device
        self._webuser = WebUser(config['username'], config['password'],False, log_level=log_level,  http_log_level=log_level)
        #self.name = 'Hydro Quebec Winter Credit Event 3'#not sure where it's used

        #asyncio.run(self.async_run([self.init_session]))#initialising web session
        asyncio.run(self.async_run([self._webuser.get_info]))#get user info
        
        #asyncio.run(self.async_run([self.close]))#close session

    async def async_run(self, functions):
        await self.init_session()
        for function in functions:
            await function()
        await self.close()

    async def init_session(self):
        """
        initialize hq websession
        """
        if self._webuser.session_expired:
            print("Login")
            await self._webuser.login()
        else:
            try:
                self._webuser.refresh_session()
                print("Refreshing session")
            except HQerror.HydroQcHTTPError:
                #if refresh didn'T work, try to login
                print("Refreshing session failed, try to login")
                self._webuser.login()
        
    async def get_user_info(self):
        await self._webuser.get_info()

    async def get_data(self):
        await self._webuser.get_info()
        customer = self._webuser.get_customer(self.config['customer'])
        account = customer.get_account(self.config['account'])
        contract = account.get_contract(self.config['contract'])
        print(customer.names)
        print(await account.get_info())
        print(await contract.get_info())



    async def close(self):
        await self._webuser.close_session()
    


        
        

       