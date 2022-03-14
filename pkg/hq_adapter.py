"""adapter for webthings gateway"""

import asyncio
import time
from threading import Thread
from logging import getLogger, INFO, WARNING

from gateway_addon import Adapter, Database

from pkg.hq_device import HQDevice

LOGGER = getLogger(__name__)

_TIMEOUT = 3
_POLL = 30


class HQAdapter(Adapter):
    """
    Adapter for the HQ program
    """

    def __init__(self, verbose=False):
        """Initialize the object"""
        self.name = self.__class__.__name__
        package_name = "webtio-hydroqc-addon"
        super().__init__(package_name, package_name, verbose)

        # load config from DB
        self.config = self.load_db_config()

        if self.verbose:
            LOGGER.setLevel(INFO)
        else:
            LOGGER.setLevel(WARNING)

        LOGGER.info(f"Config : {self.config}")

        if not self.config:
            LOGGER.error("Can't load config from Database")
            return

        self.pairing = False
        self.start_pairing(_TIMEOUT)
        self.async_main()

    def start_pairing(self, timeout):
        """Start pairing process"""
        if self.pairing:
            return

        self.pairing = True

        # create a device for each contract in config
        for contract in self.config["contracts"]:
            device = hq_Device(self, f"hydroqc-{contract['name']}", contract)
            self.handle_device_added(device)

        LOGGER.info("Start Pairing")

        time.sleep(timeout)

        self.pairing = False

    def load_db_config(self):
        """
        Load configuration from DB
        package_name -- name of the package as shown in the manifest.json
        Return the config object as dict
        """
        database = Database(self.package_name)

        if not database.open():
            LOGGER.error(f"Can't open database for package: {self.package_name}")
            return

        configs = database.load_config()
        # Si c'est toi qui la ferme ici... qui l'ouvre ?
        database.close()

        return configs

    def async_main(self):
        """main async loop"""
        LOGGER.info("Starting Loops")

        # Voir si tu peux pas utiliser async/await au lieu de Thread
        t = Thread(target=self.small_loop)
        t.start()

        big_loop = asyncio.new_event_loop()
        t = Thread(target=self.start_loop, args=(big_loop,))
        t.start()

        asyncio.run_coroutine_threadsafe(self.big_loop(), big_loop)

    def small_loop(self):
        """
        Looping to update data needed frequently
        """
        while True:
            LOGGER.info("Small Loop")

            self.update_device()

            time.sleep(_POLL)

    def update_device_property(self):
        if not self.get_devices():
            return

        for device in self.get_devices():
            updatedDevice = self.get_device(device)
            updatedDevice.update_calculated_property()

    def start_loop(self, loop):
        """
        start an async loop
        """
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def big_loop(self):
        """
        loop to update HQ data, 3 to 4 time a day is enough
        """
        while True:
            LOGGER.info("Big Loop")

            await self.update_device_hq_data()

            # Async Sleep?
            await asyncio.sleep(self.config["sync_frequency"])

    async def update_device_hq_data(self):
        if not self.get_devices():
            return

        for device in self.get_devices():
            device = self.get_device(device)

            await device.init_session()
            await device.get_data()

            device.update_hq_datas()
            device.close()
