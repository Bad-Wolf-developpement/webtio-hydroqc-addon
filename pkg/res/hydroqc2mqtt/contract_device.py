import logging
import datetime
from typing import Dict

from mqtt_hass_base.device import MqttDevice
from hydroqc.webuser import WebUser
import hydroqc

from hydroqc2mqtt.__version__ import VERSION
from hydroqc2mqtt.sensors import SENSORS, BINARY_SENSORS


class HydroqcContractDevice(MqttDevice):
    def __init__(self, name: str, logger: logging.Logger, config: Dict,
                 mqtt_discovery_root_topic=None, mqtt_data_root_topic=None):
        """Create a new MQTT Sensor Facebook object."""
        MqttDevice.__init__(self, name, logger, mqtt_discovery_root_topic, mqtt_data_root_topic)
        self._config = config
        self._webuser = WebUser(
            config["username"],
            config["password"],
            config.get("verify_ssl", True),
            log_level=config.get("log_level", "WARNING"),
            http_log_level=config.get("http_log_level", "WARNING"),
        )
        self.sw_version = VERSION
        self.manufacturer = "hydroqc"
        self._customer_id = str(self._config["customer"])
        self._account_id = str(config["account"])
        self._contract_id = str(config["contract"])

        # By default we load all sensors
        self._sensor_list = SENSORS
        if "sensors" in self._config:
            self._sensor_list = {}
            # If sensors key is in the config file, we load only the ones listed there
            # Check if sensor exists
            for sensor_key in self._config["sensors"]:
                if sensor_key not in SENSORS:
                    raise Exception(f"Sensor {sensor_key} doesn't exist. Fix your config.")
                self._sensor_list[sensor_key] = SENSORS[sensor_key]

        # By default we load all binary sensors
        self._binary_sensor_list = BINARY_SENSORS
        if "binary_sensors" in self._config:
            self._binary_sensor_list = {}
            # If binary_sensors key is in the config file, we load only the ones listed there
            # Check if sensor exists
            for sensor_key in self._config["binary_sensors"]:
                if sensor_key not in BINARY_SENSORS:
                    raise Exception(f"Binary sensor {sensor_key} doesn't exist. Fix your config.")
                self._binary_sensor_list[sensor_key] = BINARY_SENSORS[sensor_key]

        connections = [
            ["customer", self._customer_id],
            ["account", self._account_id],
            ["contract", self._contract_id],
        ]
        for conn in connections:
            self.connections = conn
        self.identifiers = config["contract"]
        self._base_name = name
        self.name = f"hydroqc_{self._base_name}"

    def add_entities(self):
        """Add Home Assistant entities."""
        for sensor_key in self._sensor_list:
            entity_settings = SENSORS[sensor_key].copy()
            sensor_name = entity_settings["name"].capitalize()
            sub_mqtt_topic = entity_settings["sub_mqtt_topic"].lower().strip("/")
            del entity_settings["data_source"]
            del entity_settings["name"]
            del entity_settings["sub_mqtt_topic"]
            entity_settings["object_id"] = f"{self.name}_{sensor_name}"

            setattr(
                self,
                sensor_key,
                self.add_entity(
                    "sensor",
                    sensor_name,
                    f"{self._contract_id}-{sensor_name}",
                    entity_settings,
                    sub_mqtt_topic=f"{self._base_name}/{sub_mqtt_topic}",
                ),
            )

        for sensor_key in self._binary_sensor_list:
            entity_settings = BINARY_SENSORS[sensor_key].copy()
            sensor_name = entity_settings["name"].capitalize()
            sub_mqtt_topic = entity_settings["sub_mqtt_topic"].lower().strip("/")
            del entity_settings["data_source"]
            del entity_settings["name"]
            del entity_settings["sub_mqtt_topic"]
            entity_settings["object_id"] = f"{self.name}_{sensor_name}"

            setattr(
                self,
                sensor_key,
                self.add_entity(
                    "binarysensor",
                    sensor_name,
                    f"{self._contract_id}-{sensor_name}",
                    entity_settings,
                    sub_mqtt_topic=f"{self._base_name}/{sub_mqtt_topic}",
                ),
            )
        self.logger.info("added %s ...", self.name)

    async def init_session(self):
        if self._webuser.session_expired:
            self.logger.info("Login")
            await self._webuser.login()
        else:
            try:
                await self._webuser.refresh_session()
                self.logger.info("Refreshing session")
            except hydroqc.error.HydroQcHTTPError:
                # Try to login if the refresh session didn't work
                self.logger.info("Refreshing session failed, try to login")
                await self._webuser.login()


    def _update_sensors(self, sensor_list, customer, account, contract, sensor_type):
        if sensor_type == "SENSORS":
            self.logger.debug("Updating sensors")
            sensor_config = SENSORS
        elif sensor_type == "BINARY_SENSORS":
            self.logger.debug("Updating binary sensors")
            sensor_config = BINARY_SENSORS
        else:
            raise Exception(f"Sensor type {sensor_type} not supported")

        for sensor_key in sensor_list:
            # Get current entity
            entity = getattr(self, sensor_key)
            # Get object path to get the value of the current entity
            datasource = sensor_config[sensor_key]["data_source"].split(".")
            # Example: datasource = "contract.winter_credit.value_state_evening_event_today"
            # datasource = ["contract", "winter_credit", "value_state_evening_event_today"]
            # Here we try get the value of the attribut "value_state_evening_event_today"
            # of the object "winter_credit" which is an attribute of the object "contract"
            data_obj = locals()[datasource[0]]
            value = None
            for index, el in enumerate(datasource[1:]):
                if not hasattr(data_obj, el):
                    entity.send_not_available()
                    self.logger.warning("%s - The object %s doesn't have the attribute %s. Maybe your contract doesn't have this data ?", sensor_key, data_obj, el)
                    break
                data_obj = getattr(data_obj, el)
                # If it's the last element of the datasource that means, it's the value
                if index + 1 == len(datasource[1:]):
                    if sensor_type == "BINARY_SENSORS":
                        value = "ON" if data_obj else "OFF"
                    elif isinstance(data_obj, datetime.datetime):
                        value = data_obj.isoformat()
                    elif (isinstance(data_obj, float) or isinstance(data_obj, int)) and sensor_list[sensor_key]["device_class"] == "monetary":
                        value = round(data_obj, 2)
                    else:
                        value = data_obj

            if value is None:
                entity.send_not_available()
                self.logger.warning("Can not find value for: %s", sensor_key)
            else:
                entity.send_state(value, {})
                entity.send_available()

    async def update(self):
        """Update Home Assistant entities."""
        self.logger.info("Updating ...")
        # TODO if any api calls failed, we should NOT crash and set sensors to not_available
        # Fetch latest data
        self.logger.info("Fetching data...")
        await self._webuser.get_info()
        customer = self._webuser.get_customer(self._customer_id)
        account = customer.get_account(self._account_id)
        contract = account.get_contract(self._contract_id)
        # fetch consumption and wintercredits
        await contract.get_periods_info()
        await contract.winter_credit.refresh_data()
        self.logger.info("Data fetched")

        self._update_sensors(self._sensor_list, customer, account, contract, "SENSORS")
        self._update_sensors(self._binary_sensor_list, customer, account, contract, "BINARY_SENSORS")

        self.logger.info("Updated %s ...", self.name)

    async def close(self):
        await self._webuser.close_session()
