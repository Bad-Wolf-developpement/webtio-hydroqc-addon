"""mqtt daemon for webtio-hydroqc-addon for webthings gateway"""

import asyncio
import os
import logging
from res.hydroqc2mqtt.daemon import MAIN_LOOP_WAIT_TIME

from res.hydroqc2mqtt.daemon import Hydroqc2Mqtt
from res.hydroqc2mqtt.contract_device import HydroqcContractDevice

_SYNC_FREQUENCY = 600
_UNREGISTER_ON_STOP = False


class hq_mqtt_deamon(Hydroqc2Mqtt):
    """mqtt daemon class"""
    #TODO: load config from db instead of yaml

    def __init__(self):
        """Initialize the class
        
        adapter -- webthings.io adapter who own the daemon
        """
        self.config = self.config = {'sync_frequency': _SYNC_FREQUENCY, 'unregister_on_stop': _UNREGISTER_ON_STOP, 'contracts': []}
        #TODO use data from DB to file this
        self.sync_frequency = _SYNC_FREQUENCY
        self.unregister_on_stop = _UNREGISTER_ON_STOP
        super().__init__()

    def read_config(self):
        """Read env vars."""
        
        self.config = {'sync_frequency': 600, 'unregister_on_stop': False, 'contracts': [{'name': 'maison', 'username': 'USERNAME', 'password': 'PASSWORD', 'customer': '0xxxxxxxxx', 'account': '29xxxxxxxxx', 'contract': '0xxxxxxxxx'}]}

        # Override hydroquebec username and password from env var if exists
        self.config.setdefault("contracts", [])
        if self.config["contracts"] is None:
            self.config["contracts"] = []
        """
        for env_var, value in os.environ.items():
            match_res = OVERRIDE_REGEX.match(env_var)
            if match_res and len(match_res.groups()) == 2:
                index = int(match_res.group(1))
                kind = match_res.group(2).lower()  # "username" or "password"
                # TODO improve me
                try:
                    # Check if the contracts is set in the config file
                    self.config["contracts"][index]
                except IndexError:
                    self.config["contracts"].append({})
                self.config["contracts"][index][kind] = value
        """

        self.sync_frequency = int(
            self.config.get("sync_frequency", MAIN_LOOP_WAIT_TIME)
        )

        self.unregister_on_stop = bool(
            self.config.get("unregister_on_stop", False)
        )
        # Handle contracts
        for contract_config in self.config["contracts"]:
            contract = HydroqcContractDevice(
                contract_config["name"], self.logger, contract_config
            )
            contract.add_entities()
            self.contracts.append(contract)

    def read_base_config(self):
        self.mqtt_username = ''
        self.mqtt_password = ''
        self.mqtt_port = 1883

        self.mqtt_discovery_root_topic = 'homeassistant'
        
        self.mqtt_data_root_topic = 'homeassistant'
        
        self._loglevel = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, self._loglevel))

if __name__ == '__main__':
    dev = hq_mqtt_deamon()
    asyncio.run(dev.async_run())