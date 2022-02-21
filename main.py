"""Hydro-Quebec winter power saving event"""

from os import path
import signal
import sys
import time

from pkg import hq_adapter

sys.path.append(path.join(path.dirname(path.abspath(__file__)), 'lib'))

_DEBUG = False
_ADAPTER = None

#print = functools.partial(print, flush=True)#TODO: figure out this


def cleanup(signum, frame):
    """Clean up any resources before exiting."""
    if _ADAPTER is not None:
        _ADAPTER.close_proxy()

    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    _ADAPTER = hq_adapter.hq_Adapter(_DEBUG)

    # Wait until the proxy stops running, indicating that the gateway shut us
    # down.
    while _ADAPTER.proxy_running():
        time.sleep(2)