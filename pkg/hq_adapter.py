"""adapter for webthings gateway"""

from cgitb import small
import functools
from gateway_addon import Adapter, Database
import time
import asyncio
from threading import Thread

from pkg.hq_device import hq_Device

#root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(root_folder)#get access to import from parent folder
print = functools.partial(print, flush=True)#allow direct print to log of gateway

_TIMEOUT = 3   

class hq_Adapter(Adapter):
    """
    Adapter for the HQ program
    """

    def __init__(self, verbose=False):
        """Initialize the object"""
        self.name = self.__class__.__name__
        self.verbose = verbose
        _id = 'webtio-hydroqc-addon'
        package_name = _id
        super().__init__(_id, package_name, verbose)

        self.config = self.load_db_config(_id)#load config from DB

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
        print("Start Pairing")#DEBUG

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

        small_loop = asyncio.new_event_loop()
        t = Thread(target=self.start_loop, args=(small_loop,))
        t.start()

        big_loop = asyncio.new_event_loop()
        t = Thread(target=self.start_loop, args=(big_loop,))
        t.start()

        asyncio.run_coroutine_threadsafe(self.small_loop(), small_loop)
        asyncio.run_coroutine_threadsafe(self.big_loop(), big_loop)

    async def small_loop(self):
        """
        """
        while True:
            print("Small Loop")
            if not self.get_devices():
                pass
            for device in self.get_devices():
                updatedDevice = self.get_device(device)
                updatedDevice.update_calculated_property()
            time.sleep(10)#TODO: update with var instead            

    def start_loop(self, loop):
        print("start loop")
        asyncio.set_event_loop(loop)
        loop.run_forever()
    
    async def big_loop(self):
        """
        """
        while True:
            print("Big Loop")
            if not self.get_devices():
                pass
            for device in self.get_devices():
                device = self.get_device(device)
                await device.init_session()
                await device.get_data()
                device.update_hq_datas()
                device.close()
            time.sleep(30)#TODO USE VAR instead