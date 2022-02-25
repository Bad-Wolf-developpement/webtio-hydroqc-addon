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
        return "{0}\r\n{1}\r\n{2}"