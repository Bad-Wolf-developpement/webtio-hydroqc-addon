"""mqtt daemon for webtio-hydroqc-addon for webthings gateway"""

import asyncio
from hydroqc2mqtt.daemon import MAIN_LOOP_WAIT_TIME

from hydroqc2mqtt.daemon import Hydroqc2Mqtt
from hydroqc2mqtt.contract_device import HydroqcContractDevice

_SYNC_FREQUENCY = 600
_UNREGISTER_ON_STOP = False

class hq_mqtt_deamon(Hydroqc2Mqtt):
    """mqtt daemon class"""
    #TODO: load config from db instead of yaml

    def __init__(self, mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_discovery_root_topic, mqtt_data_root_topic, run_once, log_level, hq_username, hq_password, hq_name, hq_customer_id, hq_account_id, hq_contract_id):
        """Initialize the class
        
         adapter -- webthings.io adapter who own the daemon
         """
        self.config = self.config = {'sync_frequency': _SYNC_FREQUENCY, 'unregister_on_stop': _UNREGISTER_ON_STOP, 'contracts': []}
        #TODO use data from DB to file this
        self.sync_frequency = _SYNC_FREQUENCY
        self.unregister_on_stop = _UNREGISTER_ON_STOP
        super().__init__(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_discovery_root_topic, mqtt_data_root_topic, None, run_once, log_level, hq_username, hq_password, hq_name, hq_customer_id, hq_account_id, hq_contract_id)

    def read_config(self):
        """Read env vars."""

        self.config = {'sync_frequency': 600, 'unregister_on_stop': False, 'contracts': [{'name': self.name, 'username': self._hq_username , 'password': self._hq_password, 'customer': self._hq_customer_id, 'account': self._hq_account_id, 'contract': self._hq_contract_id}]}
        
        self.sync_frequency = int(
            self.config.get("sync_frequency", MAIN_LOOP_WAIT_TIME)
        )

        self.unregister_on_stop = bool(
            self.config.get("unregister_on_stop", False)
        )
        # Handle contracts
        for contract_config in self.config["contracts"]:
            #TODO: maybe will have to change this for a webtio Devices
            contract = HydroqcContractDevice(
                contract_config["name"],
                self.logger,
                contract_config,
                self.mqtt_discovery_root_topic,
                self.mqtt_data_root_topic,
            )
            contract.add_entities()
            self.contracts.append(contract)

if __name__ == '__main__':
    """
    this part is for test purpose or for calling it externally
    """
    username = ''
    password = ''
    customerid = ''
    accountid = ''
    contractid = ''
    dev = hq_mqtt_deamon("localhost", 1883, '', '', 'hydroqc', 'hydroqc', False, 'INFO', username, password, 'maison', customerid, accountid, contractid)
    asyncio.run(dev.async_run())