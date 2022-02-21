import asyncio
import os
import re

import yaml

from mqtt_hass_base.daemon import MqttClientDaemon
from hydroqc2mqtt.contract_device import HydroqcContractDevice


MAIN_LOOP_WAIT_TIME = 300
OVERRIDE_REGEX = re.compile("HQ2M_CONTRACTS_(\d*)_(USERNAME|PASSWORD|CUSTOMER|ACCOUNT|CONTRACT|NAME)")


class Hydroqc2Mqtt(MqttClientDaemon):
    """MQTT Sensor Feed."""

    def __init__(self):
        """Create a new MQTT Hydroqc Sensor object."""
        self.contracts = []
        MqttClientDaemon.__init__(self, "hydroqc2mqtt")

    def read_config(self):
        """Read env vars."""
        self.config_file = os.environ["CONFIG_YAML"]

        with open(self.config_file, "rb") as fhc:
            self.config = yaml.safe_load(fhc)

        # Override hydroquebec username and password from env var if exists
        self.config.setdefault("contracts", [])
        if self.config["contracts"] is None:
            self.config["contracts"] = []

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

    async def _init_main_loop(self):
        """Init before starting main loop."""
        for contract in self.contracts:
            contract.set_mqtt_client(self.mqtt_client)

    async def _main_loop(self):
        """Run main loop."""
        # TODO refreshing session using a setting in the config yaml file
        for contract in self.contracts:
            await contract.init_session()

        for contract in self.contracts:
            await contract.update()

        i = 0
        while i < self.sync_frequency and self.must_run:
            await asyncio.sleep(1)
            i += 1

    def _on_connect(self, client, userdata, flags, rc):
        """MQTT on connect callback."""
        for contract in self.contracts:
            contract.register()

    def _on_publish(self, client, userdata, mid):
        """MQTT on publish callback."""

    def _mqtt_subscribe(self, client, userdata, flags, rc):
        """Subscribe to all needed MQTT topic."""

    def _signal_handler(self, signal_, frame):
        """Handle SIGKILL."""
        if self.unregister_on_stop:
            for contract in self.contracts:
                contract.unregister()

    def _on_message(self, client, userdata, msg):
        """Do nothing."""

    async def _loop_stopped(self):
        """Run after the end of the main loop."""
        for contract in self.contracts:
            await contract.close()
