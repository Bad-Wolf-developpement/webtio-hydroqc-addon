"""adapter for webthings gateway"""

import functools
from gateway_addon import Adapter, Database
import time
import asyncio
from threading import Thread

from pkg.hq_device import hq_Device

print = functools.partial(print, flush=True)#allow direct print to log of gateway

_TIMEOUT = 3 
_POLL = 30  

class hq_Adapter(Adapter):
    """
    Adapter for the HQ program
    """
    
    def __init__(self):
        """Initialize the object"""
        self.name = self.__class__.__name__
        
        _id = 'webtio-hydroqc-addon'
        package_name = _id        

        self.config = self.load_db_config(_id)#load config from DB
        self.verbose = self.config["debug_mode"]
        super().__init__(_id, package_name, self.verbose)

        if not self.config:
            print("Can't load config from Database")
            return        

        self.pairing=False
        self.start_pairing(_TIMEOUT)
        self.async_main()

    def start_pairing(self, timeout):
        """Start pairing process"""
        if self.pairing:
            return

        self.pairing = True
        #create a device for each contract in config
        for contract in self.config['contracts']:
            device = hq_Device(self, "hydroqc-{0}".format(contract['name']), contract)
            self.handle_device_added(device)
        if self.verbose:
            print("Start Pairing")

        time.sleep(timeout)

        self.pairing = False

    def cancel_pairing(self):
        """Cancel the pairing process"""
        self.pairing = False           

    def load_db_config(self, package_name):
        """
        Load configuration from DB
        package_name -- name of the package as shown in the manifest.json
        Return the config object as dict
        """
        database = Database(package_name)
        if not database.open():
            print("Can't open database for package: {0}".format(package_name))
            return
        configs = database.load_config()
        database.close()

        return configs

    def async_main(self):
        """main async loop"""
        if self.verbose:
            print("Starting Loops")
        
        t = Thread(target=self.small_loop)
        t.start()

        big_loop = asyncio.new_event_loop()
        t = Thread(target=self.start_loop, args=(big_loop,))
        t.start()

        asyncio.run_coroutine_threadsafe(self.big_loop(), big_loop)
        
        """
        self.config['sync_frequency'] = 10
        asyncio.run(self.big_loop())"""
    def small_loop(self):
        """
        Looping to update data needed frequently
        """
        while True:
            if self.verbose:
                print("Small Loop")
            if not self.get_devices():
                pass
            for device in self.get_devices():
                updatedDevice = self.get_device(device)
                updatedDevice.update_calculated_property()
            time.sleep(_POLL)

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
            if self.verbose:
                print("Big Loop")
            if not self.get_devices():
                pass
            for device in self.get_devices():
                device = self.get_device(device)
                await device.init_session()
                await device.get_data()
                device.update_hq_datas()
            time.sleep(self.config['sync_frequency'])
            