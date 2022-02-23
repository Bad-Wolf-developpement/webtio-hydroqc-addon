"""MQTT Daemon Base."""
import asyncio
import logging
import os
import signal
import uuid

import paho.mqtt.client as mqtt


class MqttClientDaemon:
    """Mqtt device base class."""

    def __init__(
        self,
        name=None,
        host=None,
        port=None,
        username=None,
        password=None,
        mqtt_discovery_root_topic=None,
        mqtt_data_root_topic=None,
        log_level=None,
        first_connection_timeout=10,
    ):
        """Create new MQTT daemon."""
        if name:
            self.name = name
        else:
            self.name = os.environ.get("MQTT_NAME", "mqtt-device-" + str(uuid.uuid1()))
        self.must_run = False
        self.mqtt_client = None
        self.mqtt_connected = False
        # mqtt
        self.mqtt_host = host
        self.mqtt_port = port
        self.mqtt_username = username
        self.mqtt_password = password
        self.mqtt_discovery_root_topic = mqtt_discovery_root_topic
        self.mqtt_data_root_topic = mqtt_data_root_topic
        self.log_level = log_level
        self._first_connection_timeout = first_connection_timeout
        # Get logger
        self.logger = self._get_logger()
        self.logger.info("Initializing...")
        self.read_base_config()
        self.read_config()

    def _get_logger(self):
        """Build logger."""
        logging_level = logging.DEBUG
        logger = logging.getLogger(name=self.name)
        logger.setLevel(logging_level)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def read_config(self):
        """Read configuration."""
        raise NotImplementedError

    def read_base_config(self):
        """Read base configuration from env vars."""
        if self.mqtt_username is None:
            self.mqtt_username = os.environ.get("MQTT_USERNAME", None)
        if self.mqtt_password is None:
            self.mqtt_password = os.environ.get("MQTT_PASSWORD", None)
        if self.mqtt_host is None:
            self.mqtt_host = os.environ.get("MQTT_HOST", "127.0.0.1")
        if self.mqtt_port is None:
            try:
                self.mqtt_port = int(os.environ.get("MQTT_PORT", 1883))
            except ValueError:
                raise Exception("Bad MQTT port")
        if self.mqtt_discovery_root_topic is None:
            self.mqtt_discovery_root_topic = os.environ.get(
                "MQTT_DISCOVERY_ROOT_TOPIC",
                os.environ.get("ROOT_TOPIC", "homeassistant"),
            )
        if self.mqtt_data_root_topic is None:
            self.mqtt_data_root_topic = os.environ.get(
                "MQTT_DATA_ROOT_TOPIC", "homeassistant"
            )
        if self.log_level is None:
            self.log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.logger.setLevel(getattr(logging, self.log_level.upper()))

    async def _mqtt_connect(self):
        """Connecto to the MQTT server."""
        self.logger.info("Connecting to MQTT server")
        client = mqtt.Client(client_id=self.name)
        if None not in (self.mqtt_username, self.mqtt_password):
            client.username_pw_set(self.mqtt_username, self.mqtt_password)

        client.on_message = self._base_on_message
        client.on_connect = self._base_on_connect
        client.on_publish = self._base_on_publish

        client.connect_async(self.mqtt_host, self.mqtt_port, keepalive=60)
        self.logger.info("Reaching MQTT server")
        client.loop_start()
        return client

    def _base_on_connect(
        self, client, userdata, flags, rc
    ):  # pylint: disable=W0613,C0103
        """MQTT on_connect callback."""
        self.logger.debug("Connected to MQTT server with result code %s", str(rc))
        self.mqtt_connected = True

        self._on_connect(client, userdata, flags, rc)
        self._mqtt_subscribe(client, userdata, flags, rc)
        self.logger.debug("Subscribing done")

    def _on_connect(self, client, userdata, flags, rc):  # pylint: disable=C0103
        """On connect callback method."""
        raise NotImplementedError

    def _mqtt_subscribe(self, client, userdata, flags, rc):  # pylint: disable=C0103
        """Define which topic to subscribes.

        Called after on_connect callback.
        """
        raise NotImplementedError

    def _base_on_message(self, client, userdata, msg):
        """MQTT on_message callback."""
        self.logger.info("Message received: %s %s", msg.topic, str(msg.payload))
        self._on_message(client, userdata, msg)

    def _on_message(self, client, userdata, msg):
        """On Message callback."""
        raise NotImplementedError

    def _base_on_publish(self, client, userdata, mid):
        """On publish base callback."""
        self.logger.debug("PUBLISH")
        self._on_publish(client, userdata, mid)

    def _on_publish(self, client, userdata, mid):
        """On publish callback."""
        raise NotImplementedError

    def _base_signal_handler(self, signal_, frame):
        """Signal handler."""
        self.logger.info("SIGINT received")
        self.logger.debug("Signal %s in frame %s received", signal_, frame)
        self.must_run = False
        self._signal_handler(signal_, frame)
        self.logger.info("Exiting...")

    async def async_run(self):
        """Run main base loop."""
        self.logger.info("Start main process")
        self.must_run = True
        # Add signal handler
        signal.signal(signal.SIGINT, self._base_signal_handler)
        # Mqtt client
        self.mqtt_client = await self._mqtt_connect()

        # Ensure we are connected at the first run of the main loop
        timeout = self._first_connection_timeout
        if timeout is not None:
            while not self.mqtt_client.is_connected():
                self.logger.info("Waiting for the connection to the mqtt server.")
                await asyncio.sleep(1)
                if timeout == 0:
                    msg = "Mqtt connection timed out. Exiting..."
                    self.logger.error(msg)
                    raise Exception(msg)
                timeout -= 1

        await self._init_main_loop()

        while self.must_run:
            self.logger.debug("We are in the main loop")
            await self._main_loop()
            if not self.mqtt_connected or not self.mqtt_client.is_connected():
                self.logger.error("Mqtt not connected, please check you configuration.")

        self.logger.info("Main loop stopped")
        await self._loop_stopped()
        self.logger.info("Closing MQTT client")
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()

    def _signal_handler(self, signal_, frame):
        """System signal callback to handle KILLSIG."""
        raise NotImplementedError

    async def _init_main_loop(self):
        """Init method called just before the start of the main loop."""
        raise NotImplementedError

    async def _main_loop(self):
        """Run main loop.

        This method is recalled at each iteration.
        """
        raise NotImplementedError

    async def _loop_stopped(self):
        """Run after main loop is stopped."""
        raise NotImplementedError
