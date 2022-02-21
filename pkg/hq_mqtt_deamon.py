"""mqtt daemon for webtio-hydroqc-addon for webthings gateway"""

from ..res.hydroqc2mqtt.daemon import Hydroqc2Mqtt

class hq_mqtt_deamon(Hydroqc2Mqtt):
    """mqtt daemon class"""
    #TODO: load config from db instead of yaml

    def __init__(self, adapter):
        """Initialize the class
        
        adapter -- webthings.io adapter who own the daemon
        """
        super().__init__()