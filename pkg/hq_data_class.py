""" Data class for configuration data"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class hq_Datas:

    lastSync: datetime
    nextEvent: datetime
    credit: float
    #eventTable#TODO: create a table to store multiple next event and not just one

    @property
    def print_data(self):
        return "last sync: {0}\r\next event{1}\r\ncredit: {2}".format(self.lastSync, self.nextEvent, self.credit)