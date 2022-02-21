"""mqtt daemon for webtio-hydroqc-addon for webthings gateway"""

from ..res.hydroqc2mqtt.daemon import Hydroqc2Mqtt

class hq_mqtt_deamon(Hydroqc2Mqtt):
    """mqtt daemon class"""

    def __init__(self):
        super().__init__()