"""Device for hqWinterCreditAdapter"""
from distutils.debug import DEBUG
import functools
from tempfile import TemporaryFile
from gateway_addon import Device
from hydroqc.webuser import WebUser
import hydroqc.error as HQerror
from pkg.hq_data_class import hq_Datas
import asyncio
from datetime import datetime
from pkg.hq_property import *

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
        self.config = config
        self.datas = hq_Datas
        self.new_datas = hq_Datas
        self._type.append('BinarySensor')
        self.description = 'Hydro Quebec Winter Credit Event 1'#not sure where it'S used
        self.title = _id#This appear in the text bar when adding the device and is the default name of the device
        self._webuser = WebUser(config['username'], config['password'],False, log_level=None,  http_log_level=None)
        #self.name = 'Hydro Quebec Winter Credit Event 3'#not sure where it's used

        self.init_data()#get initial data
        self.init_propertys()#initialize property
        
    def init_data(self):
        asyncio.run(self.async_run([self._webuser.get_info, self.get_data]))
        self.new_datas = self.datas

    def init_propertys(self):
        """intialize device property"""
        #active event property
        activeEvent = hq_bool_ro_property(self, 'Active Event')
        self.properties['ActiveEvent'] = activeEvent
        activeEvent.set_RO_Value('ActiveEvent', False)

        #pre-heat property
        preHeatEvent = hq_bool_ro_property(self, 'Pre-Heat Event')
        self.properties['PreHeatEvent'] = preHeatEvent
        #preHeatEvent.set_RO_Value(self, 'PreHeatEvent', False)

        #post-heat property
        postHeatEvent = hq_bool_ro_property(self, 'Post-Heat Event')
        self.properties['PostHeatEvent'] = postHeatEvent
        #postHeatEvent.set_RO_Value(self, 'PostHeatEvent', False)

        #next event property
        nextEvent = hq_datetime_ro_property(self, 'Next Event')
        self.properties['NextEvent'] = nextEvent
        #nextEvent.set_RO_Value(self, 'NextEvent', datetime.now())

        #last sync property
        lastSync = hq_datetime_ro_property(self, 'Last Sync')
        self.properties['LastSync'] = lastSync
        lastSync.set_RO_Value('LastSync', self.datas.lastSync)

        #credit total property
        credit = hq_float_ro_property(self, 'Credit Earned')
        self.properties['creditEarned'] = credit
        credit.set_RO_Value('creditEarned', self.datas.credit)

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
                await self._webuser.refresh_session()
                print("Refreshing session")
            except HQerror.HydroQcHTTPError:
                #if refresh didn'T work, try to login
                print("Refreshing session failed, try to login")
                self._webuser.login()
        
    async def get_user_info(self):
        await self._webuser.get_info()

    async def get_data(self):
        datas = hq_Datas
        if self._webuser._hydro_client._session:
            datas.lastSync = datetime.now()
        await self._webuser.get_info()
        customer = self._webuser.get_customer(self.config['customer'])
        account = customer.get_account(self.config['account'])
        contract = account.get_contract(self.config['contract'])
        wc = contract.winter_credit
        await wc.refresh_data()
        datas.credit = float(wc.raw_data['montantEffaceProjete'])
        datas.nextEvent = wc.next_critical_peak
        self.new_datas = datas
        
    async def close(self):
        await self._webuser.close_session()
    


        
        

       