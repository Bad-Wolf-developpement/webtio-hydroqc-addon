"""MQTT Hass Base."""
import logging
from typing import List

from mqtt_hass_base import entity as mqtt_entity
from mqtt_hass_base.error import MQTTHassBaseError

ENTITY_TYPES = (
    "switch",
    "lock",
    "light",
    "binarysensor",
    "sensor",
    "vacuum",
)


class MqttDevice:
    """Mqtt device base class."""

    def __init__(
        self,
        name: str,
        logger: logging.Logger,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
    ):
        """Create a new device."""
        # Get logger
        self.logger = logger.getChild(name)
        self._name = name
        self.mqtt_discovery_root_topic = mqtt_discovery_root_topic
        self.mqtt_data_root_topic = mqtt_data_root_topic
        self._entities = []
        self._model = None
        self._manufacturer = None
        self._sw_version = None
        self._via_device = None
        self._identifiers = []
        self._connections = []
        self._mac = None

    def __repr__(self):
        """Get repr of the current device."""
        return "<{} '{}'>".format(self.__class__.__name__, self.name)

    @property
    def entities(self):
        """Get the list of the entities of the devices."""
        return self._entities

    def add_entity(
        self,
        entity_type,
        name,
        unique_id,
        entity_settings,
        subscriptions=None,
        sub_mqtt_topic=None,
    ):
        """Add a new entity in the device."""
        if entity_type.lower() not in ENTITY_TYPES:
            msg = (
                "Entity type '{}' is not supported. " "Supported types are: {}"
            ).format(entity_type, ENTITY_TYPES)
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)

        if sub_mqtt_topic:
            mqtt_data_root_topic = "/".join(
                (self.mqtt_data_root_topic, sub_mqtt_topic.strip("/"))
            )
        else:
            mqtt_data_root_topic = self.mqtt_data_root_topic

        self.logger.info("Adding entity %s - %s", entity_type, name)
        ent = getattr(mqtt_entity, "Mqtt" + entity_type.capitalize())(
            name=name,
            unique_id=unique_id,
            mqtt_discovery_root_topic=self.mqtt_discovery_root_topic,
            mqtt_data_root_topic=mqtt_data_root_topic,
            logger=self.logger,
            device_payload=self.config_device_payload,
            subscriptions=subscriptions,
            **entity_settings,
        )
        self._entities.append(ent)
        return ent

    def set_mqtt_client(self, mqtt_client):
        """Set the mqtt client to each entity."""
        for entity in self.entities:
            entity.set_mqtt_client(mqtt_client)

    def register(self):
        """Register all entities in MQTT."""
        self.logger.info("Registering entities for device %s", self.name)
        for entity in self.entities:
            entity.register()

    def subscribe(self):
        """Subscribe to the MQTT topic needed for each entity."""
        self.logger.info("Subscribing to input mqtt topics")
        for entity in self.entities:
            entity.subscribe()

    def unregister(self):
        """Unregister all entities from MQTT."""
        self.logger.info("Unregistering entities for device %s", self.name)
        for entity in self.entities:
            entity.unregister()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @name.setter
    def name(self, name: str):
        if name != self._name:
            self.logger = self.logger.getChild("device").getChild(name)
        self._name = name

    @property
    def model(self):
        """Return the module of the device."""
        return self._model

    @model.setter
    def model(self, model: str):
        self._model = model

    @property
    def manufacturer(self):
        """Return the manufacturer of the device."""
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, manufacturer: str):
        self._manufacturer = manufacturer

    @property
    def sw_version(self):
        """Return the software version of the device."""
        return self._sw_version

    @sw_version.setter
    def sw_version(self, sw_version: str):
        self._sw_version = sw_version

    @property
    def via_device(self):
        """Return the intermediate device name of the current device."""
        return self._via_device

    @via_device.setter
    def via_device(self, via_device: str):
        self._via_device = via_device

    @property
    def identifiers(self):
        """Return the identifiers of the device."""
        return self._identifiers

    @identifiers.setter
    def identifiers(self, id_: str):
        if id_ not in self._identifiers:
            self._identifiers.append(id_)

    @property
    def mac(self):
        """Return the mac address of the device."""
        return self._mac

    @mac.setter
    def mac(self, value):
        self._mac = value
        self.connections = ("mac", value)

    @property
    def connections(self):
        """Return the connection list of the device."""
        return self._connections

    @connections.setter
    def connections(self, raw_item: List[str]):
        try:
            item = list(raw_item)
        except TypeError:
            raise MQTTHassBaseError("Bad connection value: {}".format(raw_item))
        if len(item) != 2:
            raise MQTTHassBaseError(
                "A connection need 2 elements but it's: {}".format(raw_item)
            )
        if item not in self._connections:
            self._connections.append(item)

    @property
    def config_device_payload(self):
        """Return the configuration device payload.

        This is the payload needed to register an entity of the current
        device in Home Assistant (using MQTT discovery).
        """
        payload = {"name": self.name}
        if self.connections:
            payload["connections"] = self.connections
        if self.identifiers:
            payload["identifiers"] = self.identifiers
        if self.manufacturer:
            payload["manufacturer"] = self.manufacturer
        if self.model:
            payload["model"] = self.model
        if self.sw_version:
            payload["sw_version"] = self.sw_version
        if self.via_device:
            payload["via_device"] = self.via_device
        if "connections" not in payload and "identifiers" not in payload:
            msg = "You need to define identifiers or connections in the device attributes."
            self.logger.error(msg)
            raise MQTTHassBaseError(msg)
        return payload
