"""MQTT Binary sensor entity module."""
import json

from mqtt_hass_base.const import BINARY_SENSOR_DEVICE_CLASSES
from mqtt_hass_base.entity.common import MqttEntity
from mqtt_hass_base.error import MQTTHassBaseError


class MqttBinarysensor(MqttEntity):
    """MQTT Binary sensor entity class."""

    _component = "binary_sensor"

    def __init__(
        self,
        name,
        unique_id: str,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
        logger,
        device_payload,
        subscriptions,
        device_class=None,
        expire_after=0,
        force_update=False,
        off_delay=None,
        icon="",
        state_class=None,
        object_id: str = None,
    ):
        """Create a new MQTT binary sensor entity object."""
        # MqttEntity.__init__(self, name, mqtt_discovery_root_topic, logger, device_payload)
        MqttEntity.__init__(
            self,
            name,
            unique_id,
            mqtt_discovery_root_topic,
            mqtt_data_root_topic,
            logger,
            device_payload,
            object_id=object_id,
        )
        self._device_class = device_class
        if device_class not in BINARY_SENSOR_DEVICE_CLASSES:
            msg = "Bad device class {}. Should be in {}".format(
                device_class, BINARY_SENSOR_DEVICE_CLASSES
            )
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)
        self._expire_after = expire_after
        self._force_update = force_update
        self._off_delay = off_delay
        self._state_class = state_class
        self._icon = icon

    def register(self):
        """Register the current entity to Hass.

        Using the MQTT discovery feature of Home Assistant.
        """
        config_payload = {
            "availability": {
                "payload_available": "online",
                "payload_not_available": "offline",
                "topic": self.availability_topic,
            },
            "device": self.device_payload,
            "expire_after": self._expire_after,
            "force_update": self._force_update,
            "json_attributes_template": "",
            "json_attributes_topic": self.json_attributes_topic,
            "name": self.name,
            "payload_available": "online",
            "payload_not_available": "offline",
            "payload_off": "OFF",
            "payload_on": "ON",
            "qos": 0,
            "state_topic": self.state_topic,
            "unique_id": self.unique_id,
        }
        if self._device_class:
            config_payload["device_class"] = self._device_class
        if self._off_delay:
            config_payload["off_delay"] = self._off_delay
        if self._icon:
            config_payload["icon"] = self._icon
        if self._object_id:
            config_payload["object_id"] = self._object_id

        self.logger.debug("%s: %s", self.config_topic, json.dumps(config_payload))
        self._mqtt_client.publish(
            topic=self.config_topic, retain=True, payload=json.dumps(config_payload)
        )

    def send_state(self, state, attributes=None):
        """Send the current state of the sensor to Home Assistant."""
        if isinstance(state, (bytes, str)):
            state = state[:255]
        self._mqtt_client.publish(topic=self.state_topic, retain=True, payload=state)
        if attributes is not None:
            self.send_attributes(attributes)

    def send_on(self, attributes=None):
        """Send the ON state of the sensor to Home Assistant."""
        self.send_state("ON", attributes=attributes)

    def send_off(self, attributes=None):
        """Send the OFF state of the sensor to Home Assistant."""
        self.send_state("OFF", attributes=attributes)
