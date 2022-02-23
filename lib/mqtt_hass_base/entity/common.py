"""MQTT base entity module."""
import json
from typing import Dict

import paho.mqtt.client
from mqtt_hass_base.error import MQTTHassBaseError


class MqttEntity:
    """MQTT base entity class."""

    _component = None

    def __init__(
        self,
        name,
        unique_id: str,
        mqtt_discovery_root_topic,
        mqtt_data_root_topic,
        logger,
        device_payload: Dict = None,
        subscriptions: Dict[str, str] = None,
        object_id: str = None,
    ):
        """Create a new MQTT entity."""
        self._name = name
        self._mqtt_discovery_root_topic = mqtt_discovery_root_topic
        self._mqtt_data_root_topic = mqtt_data_root_topic
        self._logger = logger.getChild(name)
        self._object_id = object_id
        self._unique_id = unique_id
        self._device_payload = device_payload
        self._subscriptions = subscriptions
        if self._device_payload is None:
            self._device_payload = {}
        if self._subscriptions is None:
            self._subscriptions = {}
        if self._component is None:
            raise MQTTHassBaseError(
                "Missing `_component` attributes in the class {}".format(
                    self.__class__.name
                )
            )

    def set_mqtt_client(self, mqtt_client: paho.mqtt.client.Client):
        """Set MQTT client to the current entity."""
        self._mqtt_client = mqtt_client

    @property
    def component_type(self):
        """Get Entity type."""
        return self._component

    @property
    def mqtt_discovery_root_topic(self):
        """Get MQTT root topic of the entity."""
        return self._mqtt_discovery_root_topic.lower()

    @property
    def mqtt_data_root_topic(self):
        """Get MQTT root topic of data of the entity."""
        return self._mqtt_data_root_topic.lower()

    @property
    def logger(self):
        """Get the logger of the entity."""
        return self._logger

    @property
    def name(self):
        """Get the name of the entity."""
        return self._name

    @property
    def object_id(self):
        """Get the object_id of the entity."""
        return self._object_id

    @property
    def unique_id(self):
        """Get the unique_id of the entity."""
        return self._unique_id

    @property
    def device_payload(self):
        """Get the device payload of the entity."""
        return self._device_payload

    @property
    def command_topic(self):
        """MQTT Command topic to receive commands from Home Assistant."""
        return "/".join(
            (self._mqtt_data_root_topic, self._component, self.name, "command")
        ).lower()

    @property
    def state_topic(self):
        """MQTT State topic to send state to Home Assistant."""
        return "/".join(
            (self._mqtt_data_root_topic, self._component, self.name, "state")
        ).lower()

    @property
    def availability_topic(self):
        """MQTT availability topic to send entity availability to Home Assistant."""
        return "/".join(
            (self._mqtt_data_root_topic, self._component, self.name, "availability")
        ).lower()

    @property
    def json_attributes_topic(self):
        """MQTT attributes topic to send attribute dict to Home Assistant."""
        return "/".join(
            (self._mqtt_data_root_topic, self._component, self.name, "attributes")
        ).lower()

    @property
    def config_topic(self):
        """Return MQTT config topic."""
        return "/".join(
            (
                self.mqtt_discovery_root_topic,
                self._component,
                self.unique_id.lower().replace(" ", "_"),
                "config",
            )
        ).lower()

    def send_available(self):
        """Set the availability to ON."""
        self._mqtt_client.publish(
            topic=self.availability_topic, retain=True, payload="online"
        )

    def send_not_available(self):
        """Set the availability to OFF."""
        self._mqtt_client.publish(
            topic=self.availability_topic, retain=True, payload="offline"
        )

    def register(self):
        """Register the current entity to Hass.

        Using the MQTT discovery feature of Home Assistant.
        """
        raise NotImplementedError

    def subscribe(self):
        """Subscribe to the MQTT topics."""
        for topic_name, callback in self._subscriptions.items():
            self.logger.info("Subscribing to %s", topic_name)
            if not hasattr(self, topic_name):
                msg = "This entity doesn't have this mqtt input topic {}".format(
                    topic_name
                )
                self.logger.error(msg)
                raise MQTTHassBaseError(msg)
            topic = getattr(self, topic_name)
            self._mqtt_client.subscribe(topic)
            self._mqtt_client.message_callback_add(topic, callback)

    def unregister(self):
        """Unregister the current entity to Hass.

        Using the MQTT discovery feature of Home Assistant.
        """
        self.logger.info("Deleting %s: %s", self.config_topic, json.dumps({}))
        self._mqtt_client.publish(
            topic=self.config_topic, retain=False, payload=json.dumps({})
        )

    def send_state(self, state: Dict, attributes: Dict = None):
        """Send current state to MQTT."""
        raise NotImplementedError

    def send_attributes(self, attributes: Dict):
        """Send current attribute dict to MQTT."""
        if not isinstance(attributes, dict):
            raise MQTTHassBaseError("'attributes' argument should be a dict.")
        self._mqtt_client.publish(
            topic=self.json_attributes_topic,
            retain=True,
            payload=json.dumps(attributes),
        )
