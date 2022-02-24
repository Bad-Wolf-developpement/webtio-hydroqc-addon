"""hq2mqtt adapter for webthings gateway"""
from asyncio.log import logger
import functools
from gateway_addon import Adapter, Database
import os
import sys
import logging

#root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#sys.path.append(root_folder)#get access to import from parent folder
print = functools.partial(print, flush=True)

_TIMEOUT = 3   

class hq_Adapter(Adapter):
    """
    Adapter for the HQ program
    """

    def __init__(self, verbose=False):
        """Initialize the object"""
        self.name = self.__class__.__name__
        _id = 'webtio-hydroqc-addon'
        package_name = _id
        super().__init__(_id, package_name, verbose)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.config = self.load_db_config(_id)#load config from DB
        #now load thew mqtt deamon
        self.logger.info(self.config)
        
        

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