"""Device for hqWinterCreditAdapter"""

import functools
from gateway_addon import Device
from hydroqc.webuser import WebUser
import hydroqc.error as HQerror
from pkg.hq_data_class import hq_Datas
from datetime import datetime, timedelta
from pkg.hq_property import *

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
        
        #setting the log level
        if self.adapter.verbose:
            log_level = "DEBUG"
        else:
            log_level = "WARNING"
        self.config = config
        self.datas = hq_Datas
        self.datas.lastSync = None
        self.datas.nextEvent = None
        self.datas.credit = None
        self.new_datas = hq_Datas
        self._type.append('BinarySensor')
        self.description = 'Hydro Quebec Winter Credit Event 1'#not sure where it'S used in gui
        self.title = _id#This appear in the text bar when adding the device and is the default name of the device
        self._webuser = WebUser(config['username'], config['password'],False, log_level=log_level,  http_log_level=log_level)
        self.name = _id
        self.dbConfig = self.adapter.config

        self.init_properties()#initialize properties
            
    def update_hq_datas(self):
        """
        update datas if changed
        """       
         
        if self.adapter.verbose:
            print("updating hq datas")
            print("Old Datas: {0}".format(self.datas.lastSync))
            print("New Datas: {0}".format(self.new_datas.lastSync))
        if self.data_changed():
            #TODO: don't call set_RO if value is same
            #self.datas = self.new_datas
            for property in self.properties:
                if property == 'LastSync':
                    value = self.new_datas.lastSync
                    if self.adapter.verbose:
                        print("setting value for: {0} to {1}".format(property, value))
                    self.find_property(property).set_RO_Value(property, value)
                elif property == 'NextEvent':
                    value = self.new_datas.nextEvent
                    if self.adapter.verbose:
                        print("setting value for: {0} to {1}".format(property, value))
                    self.find_property(property).set_RO_Value(property, value)
                elif property == 'creditEarned':
                    value = self.new_datas.credit
                    if self.adapter.verbose:
                        print("setting value for: {0} to {1}".format(property, value))
                    self.find_property(property).set_RO_Value(property, value)

    def update_calculated_property(self):
        """
        update property that are calculated
        """
        if self.adapter.verbose:
            print("update calculated")
        #Set end of event
        if self.datas.nextEvent is None:
            endEvent = None
        elif self.datas.nextEvent.hour == 6:
            endEvent = self.datas.nextEvent + timedelta(hours=3)
        elif self.datas.nextEvent.hour == 20:
            endEvent = self.datas.nextEvent + timedelta(hours=4)

        #set pre-heat start time
        if self.datas.nextEvent is None:
            preHeatStart = None
        else:
            preHeatStart = self.datas.nextEvent - timedelta(minutes=self.dbConfig['preHeatDelay'])

        #set post-heat end time
        if self.datas.nextEvent is None:
            postHeatEnd = None
        else:
            postHeatEnd = self.datas.nextEvent + timedelta(minutes=self.dbConfig['postHeatDelay'])

        for property in self.properties:
            if property == 'ActiveEvent':
                self.find_property(property).set_RO_Value(property,self.find_property(property).is_active(self.datas.nextEvent, endEvent))
            elif property == 'PreHeatEvent':
                self.find_property(property).set_RO_Value(property, self.find_property(property).is_active(preHeatStart, self.datas.nextEvent))
            elif property == 'PostHeatEvent':
                self.find_property(property).set_RO_Value(property, self.find_property(property).is_active(endEvent, postHeatEnd))

    def data_changed(self):
        """
        test if HQ data have changed or not
        
        return -- bool
        """
        #TODO: DEBBUGING THIS SECTION, IT SHOW FALSE ALWAYS, TEMPORARY PUT BOTH ON TRUE
        #if self.adapter.verbose:
        if True:
            print("Old last Sync : {0}".format(self.datas.lastSync))
            print("New last Sync : {0}".format(self.new_datas.lastSync))
        if (not self.datas.lastSync is None or not self.new_datas.lastSync is None) and (self.datas.lastSync < self.new_datas.lastSync):
            #if have a previous last sync and new sync and new sync is newer
            print("True")
            return True

        elif self.datas.lastSync is None and not self.new_datas.lastSync is None:
            return True#If we don'T have old data but we have new     
        else:
            print("False")
            return False

    def init_properties(self):
        """
        intialize device properties
        """
        #active event property
        aeID = 'ActiveEvent'
        activeEvent = hq_bool_ro_property(self, aeID, 'Active Event')
        self.properties[aeID] = activeEvent

        #pre-heat property
        prheID = 'PreHeatEvent'
        preHeatEvent = hq_bool_ro_property(self, prheID, 'Pre-Heat Event')
        self.properties[prheID] = preHeatEvent

        #post-heat property
        poeID = 'PostHeatEvent'
        postHeatEvent = hq_bool_ro_property(self, poeID, 'Post-Heat Event')
        self.properties[poeID] = postHeatEvent

        #next event property
        neID = 'NextEvent'
        nextEvent = hq_datetime_ro_property(self, neID, 'Next Event')
        self.properties[neID] = nextEvent

        #last sync property
        lsID = 'LastSync'
        lastSync = hq_datetime_ro_property(self, lsID, 'Last Sync')
        self.properties[lsID] = lastSync

        #credit total property
        cID = 'creditEarned'
        credit = hq_float_ro_property(self, cID, 'Credit Earned')
        self.properties[cID] = credit

    async def init_session(self):
        """
        initialize hq websession
        """
        if self._webuser.session_expired:
            if self.adapter.verbose:
                print("Login")
            await self._webuser.login()
        else:
            try:
                await self._webuser.refresh_session()
                if self.adapter.verbose:
                    print("Refreshing session")
            except HQerror.HydroQcHTTPError:
                #if refresh didn'T work, try to login
                print("Refreshing session failed, try to login")
                self._webuser.login()

    async def get_data(self):
        datas = hq_Datas
        if self._webuser._hydro_client._session:
            datas.lastSync = datetime.now()
        else:
            datas.lastSync = None
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
