"""mqtt daemon for webtio-hydroqc-addon for webthings gateway"""

import asyncio
from hydroqc2mqtt.daemon import MAIN_LOOP_WAIT_TIME

from hydroqc2mqtt.daemon import Hydroqc2Mqtt
from hydroqc2mqtt.contract_device import HydroqcContractDevice

class hq_mqtt_deamon(Hydroqc2Mqtt):
    """mqtt daemon class"""
    #TODO: load config from db instead of yaml

    def __init__(self, configs, mqtt_host = 'localhost', mqtt_port = 1883, mqtt_username = '', mqtt_password = '', run_once = False, log_level = 'INFO'):
        """Initialize the class
        
         configs -- configs dictionnary: {'sync_frequency': int, 'unregister_on_stop': bool, 'contracts': [{'name': str, 'username': str , 'password': str, 'customer': str, 'account': str, 'contract': str}]}
         mqtt_host -- mqtt broker, default localhost
         mqtt_port -- mqtt broker port, default 1883
         mqtt_username -- mqtt broker username if needed, empty if none, Default Empty
         mqtt_password -- mqtt roker passwor if needed, empty if none, Default Empty
         run_once -- set to True if you only want to run process once Default False
         log_level -- log_level, Default INFO
         """
        mqtt_discovery_root_topic = 'webtio-hydroqc-addon'
        mqtt_data_root_topic = 'webtio-hydroqc-addon'
        self.config = configs
        self.sync_frequency = configs['sync_frequency']
        self.unregister_on_stop = configs['unregister_on_stop']
        super().__init__(mqtt_host, mqtt_port, mqtt_username, mqtt_password, mqtt_discovery_root_topic, mqtt_data_root_topic, None, run_once, log_level, None, None, None, None, None, None)

    def read_config(self):
        """Read env vars."""        
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
    name = ''
    username = ''
    password = ''
    customerid = ''
    accountid = ''
    contractid = ''
    config = {'sync_frequency': 600, 'unregister_on_stop': False, 'contracts': [{'name': name, 'username': username , 'password': password, 'customer': customerid, 'account': accountid, 'contract': contractid}]}
    dev = hq_mqtt_deamon(config)
    asyncio.run(dev.async_run())