"""MQTT Light entity module."""
import json
from typing import Dict, List

from mqtt_hass_base.entity.common import MqttEntity


class MqttLight(MqttEntity):
    """MQTT Light entity class."""

    _component = "light"

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name,
        unique_id: str,
        mqtt_discovery_root_topic: str,
        mqtt_data_root_topic: str,
        logger,
        device_payload,
        subscriptions,
        optimistic: bool,
        brightness: bool = False,
        brightness_scale: int = 255,
        color_temp: bool = False,
        effect: bool = False,
        effect_list: List = None,
        flash_time_long: int = None,
        flash_time_short: int = None,
        hs_: bool = False,
        max_mireds: int = None,
        min_mireds: int = None,
        rgb: bool = False,
        white_value: bool = False,
        xy_: bool = False,
        object_id: str = None,
    ):
        """Create a new MQTT sensor entity object."""
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
        self._brightness = brightness
        self._brightness_scale = brightness_scale
        self._color_temp = color_temp
        self._effect = effect
        self._effect_list = effect_list
        self._flash_time_long = flash_time_long
        self._flash_time_short = flash_time_short
        self._hs = hs_
        self._max_mireds = max_mireds
        self._min_mireds = min_mireds
        self._optimistic = optimistic
        self._rgb = rgb
        self._white_value = white_value
        self._xy = xy_

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
            "brightness": self._brightness,
            "color_temp": self._color_temp,
            "command_topic": self.command_topic,
            "device": self.device_payload,
            "effect": self._effect,
            "hs": self._hs,
            # "json_attributes_template": "",
            "json_attributes_topic": self.json_attributes_topic,
            "name": self.name,
            # on_command_type ????
            "optimistic": self._optimistic,
            "qos": 0,
            "retain": False,
            "rgb": self._rgb,
            "schema": "json",
            "state_topic": self.state_topic,
            "white_value": self._white_value,
            "xy": self._xy,
            "unique_id": self._unique_id,
        }

        if self._brightness:
            config_payload["brightness_scale"] = self._brightness_scale
        if self._effect:
            config_payload["effect_list"] = self._effect_list
        if self._flash_time_long:
            config_payload["flash_time_long"] = self._flash_time_long
        if self._flash_time_short:
            config_payload["flash_time_short"] = self._flash_time_short
        if self._max_mireds:
            config_payload["max_mireds"] = self._max_mireds
        if self._min_mireds:
            config_payload["min_mireds"] = self._min_mireds
        if self._object_id:
            config_payload["object_id"] = self._object_id

        self.logger.debug("%s: %s", self.config_topic, json.dumps(config_payload))
        self._mqtt_client.publish(
            topic=self.config_topic, retain=True, payload=json.dumps(config_payload)
        )

    def send_state(self, state: Dict, attributes: Dict = None):
        """Send the current state of the light to Home Assistant."""
        # TODO validate the state dict
        self._mqtt_client.publish(
            topic=self.state_topic, retain=True, payload=json.dumps(state)
        )
