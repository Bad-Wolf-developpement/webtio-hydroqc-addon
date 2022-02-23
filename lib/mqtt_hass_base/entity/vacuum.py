"""MQTT Vacuum entity module."""
import json

from mqtt_hass_base.entity.common import MqttEntity
from mqtt_hass_base.error import MQTTHassBaseError

# TODO get it from hass
VACUUM_STATES = (
    "cleaning",
    "docked",
    "paused",
    "idle",
    "returning",
    "error",
)


class MqttVacuum(MqttEntity):
    """MQTT Vacuum entity class."""

    _component = "vacuum"
    _features = (
        "start",
        "stop",
        "pause",
        "return_home",
        "battery",
        "status",
        "locate",
        "clean_spot",
        "fan_speed",
        "send_command",
    )

    def __init__(
        self,
        name,
        mqtt_discovery_root_topic,
        mqtt_data_root_topic,
        logger,
        device_payload,
        subscriptions,
        supported_features,
        fan_speed_list,
        object_id: str = None,
        unique_id: str = None,
    ):
        """Create a new Vacuum entity."""
        MqttEntity.__init__(
            self,
            name,
            unique_id,
            mqtt_discovery_root_topic,
            mqtt_data_root_topic,
            logger,
            device_payload,
            subscriptions,
            object_id=object_id,
        )
        self._supported_features = supported_features
        self._fan_speed_list = fan_speed_list
        self._state = None

    @property
    def state(self):
        """Get the current state of the vacuum."""
        return self._state

    @property
    def send_command_topic(self):
        """Get the MQTT topic where command should be send to."""
        return "/".join(
            (self.mqtt_data_root_topic, self._component, self.name, "send_command")
        ).lower()

    @property
    def set_fan_speed_topic(self):
        """Return the current fan/suction speed."""
        return "/".join(
            (self.mqtt_data_root_topic, self._component, self.name, "set_fan_speed")
        ).lower()

    def register(self):
        """Register the current entity to Hass.

        Using the MQTT discovery feature of Home Assistant.
        """
        config_payload = {
            "availability": {
                "payload_available": "online",
                "payload_not_available": "offline",
                "topic": self.availability_topic,  # required
            },
            "command_topic": self.command_topic,
            "device": self.device_payload,
            "fan_speed_list": self._fan_speed_list,
            # "json_attributes_template": "",
            "json_attributes_topic": self.json_attributes_topic,
            "name": self.name,
            "payload_clean_spot": "clean_spot",
            "payload_locate": "locate",
            "payload_pause": "pause",
            "payload_return_to_base": "return_to_base",
            "payload_start": "start",
            "payload_stop": "stop",
            "qos": 0,
            "retain": False,
            "schema": "state",  # static
            "send_command_topic": self.send_command_topic,
            "set_fan_speed_topic": self.set_fan_speed_topic,
            "state_topic": self.state_topic,
            "supported_features": self._supported_features,
            "unique_id": self._unique_id,
        }

        if self._object_id:
            config_payload["config_object_id"] = self._object_id

        self.logger.debug("%s: %s", self.config_topic, json.dumps(config_payload))
        self._mqtt_client.publish(
            topic=self.config_topic, retain=True, payload=json.dumps(config_payload)
        )

    def send_state(
        self, state, battery_level=None, fan_speed=None
    ):  # pylint: disable=arguments-differ
        """Send the current state of the vacuum to Hass."""
        if state not in VACUUM_STATES:
            raise MQTTHassBaseError(
                "Bad state {} not in {}".format(state, VACUUM_STATES)
            )
        payload = {"state": state}
        self._state = state
        if battery_level:
            payload["battery_level"] = battery_level
        if fan_speed:
            payload["fan_speed"] = fan_speed
        self._mqtt_client.publish(
            topic=self.state_topic, retain=True, payload=json.dumps(payload)
        )
