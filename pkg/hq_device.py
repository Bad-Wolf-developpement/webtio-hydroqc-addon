"""Device for hqWinterCreditAdapter"""

import functools
from datetime import datetime, timedelta

import hydroqc.error as HQerror
from gateway_addon import Device
from hydroqc.webuser import WebUser

from pkg.hq_data_class import HQDatas
from pkg.hq_property import (
    HQBoolRoProperty,
    HQDatetimeRoProperty,
    HQFloatRoProperty,
)

print = functools.partial(print, flush=True)  # allow direct print to log of gateway


class HQDevice(Device):
    """HQ winter Credit Device"""

    def __init__(self, adapter, _id, config):
        """
        Initialize the object

        adapter -- Adapter managing this device
        _id -- ID of this device
        config -- contract settings
        """
        Device.__init__(
            self,
            adapter,
            _id,
        )
        # setting the log level
        if self.adapter.verbose:
            log_level = "DEBUG"
        else:
            log_level = "WARNING"
        self.config = config
        self.datas = HQDatas()
        self.new_datas = HQDatas()
        self._type.append("BinarySensor")
        self.description = (
            "Hydro Quebec Winter Credit Event 1"  # not sure where it'S used in gui
        )
        self.title = self.id
        self._webuser = WebUser(
            config["username"],
            config["password"],
            False,
            log_level=log_level,
            http_log_level=log_level,
        )
        self.name = _id
        self.db_config = self.adapter.config
        self.init_properties()  # initialize properties
        self.data_changed()

    def update_hq_datas(self):
        """
        update datas if changed
        """
        if self.adapter.verbose:
            print("updating hq datas")
            print(f"Old Datas: {self.datas.lastSync}")
            print(f"New Datas: {self.new_datas.lastSync}")
        if not self.data_changed():
            return

        self.datas = self.new_datas

        for property in self.properties:
            if property == "LastSync":
                old_value, new_value = self.datas.lastSync, self.new_datas.lastSync
            elif property == "NextEvent":
                old_value, new_value = self.datas.nextEvent, self.new_datas.nextEvent
            elif property == "creditEarned":
                old_value, new_value = self.datas.credit, self.new_datas.credit
            else:
                continue

            if old_value == new_value:
                continue

            if self.adapter.verbose:
                print(f"setting value for: {property} to {new_value}")

            self.find_property(property).set_ro_value(property, new_value)

    def update_calculated_property(self):
        """
        update property that are calculated
        """
        if self.adapter.verbose:
            print("update calculated")
        # Set end of event
        if self.datas.nextEvent is None:
            end_event = None
        elif self.datas.nextEvent.hour == 6:
            end_event = self.datas.nextEvent + timedelta(hours=3)
        elif self.datas.nextEvent.hour == 20:
            end_event = self.datas.nextEvent + timedelta(hours=4)
        else:
            raise Exception("Unknown event time???")

        # set pre-heat start time
        if self.datas.nextEvent is None:
            pre_heat_start = None
        else:
            pre_heat_start = self.datas.nextEvent - timedelta(
                minutes=self.db_config["preHeatDelay"]
            )

        # set post-heat end time
        if self.datas.nextEvent is None:
            post_heat_end = None
        else:
            post_heat_end = self.datas.nextEvent + timedelta(
                minutes=self.db_config["postHeatDelay"]
            )
        for property in self.properties:
            if property == "ActiveEvent":
                self.find_property(property).set_ro_value(
                    property,
                    self.find_property(property).is_active(
                        self.datas.nextEvent, end_event
                    ),
                )
            elif property == "PreHeatEvent":
                self.find_property(property).set_ro_value(
                    property,
                    self.find_property(property).is_active(
                        pre_heat_start, self.datas.nextEvent
                    ),
                )
            elif property == "PostHeatEvent":
                self.find_property(property).set_ro_value(
                    property,
                    self.find_property(property).is_active(end_event, post_heat_end),
                )

    def data_changed(self):
        """
        test if HQ data have changed or not

        return -- bool
        """
        if self.adapter.verbose:
            print("testing if data change")
        if self.datas.lastSync is None and not self.new_datas.lastSync is None:
            # If we don'T have old data but we have new
            return True
        elif (
            not self.datas.lastSync is None or not self.new_datas.lastSync is None
        ) and (self.datas.lastSync < self.new_datas.lastSync):
            # if have a previous last sync and new sync and new sync is newer
            return True
        else:
            return False

    def init_properties(self):
        """
        intialize device properties
        """
        active_event_property_id = "ActiveEvent"
        active_event = HQBoolRoProperty(self, active_event_property_id, "Active Event")
        self.properties[active_event_property_id] = active_event

        pre_heat_property_id = "PreHeatEvent"
        pre_heat_event = HQBoolRoProperty(self, pre_heat_property_id, "Pre-Heat Event")
        self.properties[pre_heat_property_id] = pre_heat_event

        post_heat_property_id = "PostHeatEvent"
        post_heat_event = HQBoolRoProperty(self, post_heat_property_id, "Post-Heat Event")
        self.properties[post_heat_property_id] = post_heat_event

        next_event_property_id = "NextEvent"
        next_event = HQDatetimeRoProperty(self, next_event_property_id, "Next Event")
        self.properties[next_event_property_id] = next_event

        last_sync_property_id = "LastSync"
        last_sync = HQDatetimeRoProperty(self, last_sync_property_id, "Last Sync")
        self.properties[last_sync_property_id] = last_sync

        credit_total_property_id = "creditEarned"
        credit = HQFloatRoProperty(self, credit_total_property_id, "Credit Earned")
        self.properties[credit_total_property_id] = credit

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
                # if refresh didn't work, try to login
                print("Refreshing session failed, try to login")
                self._webuser.login()

    async def get_data(self):
        temp_datas = HQDatas
        if self._webuser._hydro_client._session:
            temp_datas.lastSync = datetime.now()
        else:
            temp_datas.lastSync = None
        await self._webuser.get_info()
        customer = self._webuser.get_customer(self.config["customer"])
        account = customer.get_account(self.config["account"])
        contract = account.get_contract(self.config["contract"])
        winter_credit = contract.winter_credit
        await winter_credit.refresh_data()
        temp_datas.credit = float(winter_credit.raw_data["montantEffaceProjete"])
        temp_datas.nextEvent = winter_credit.next_critical_peak
        self.new_datas = temp_datas

    async def close(self):
        await self._webuser.close_session()
