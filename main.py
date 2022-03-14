"""Hydro-Quebec winter power saving event"""

import functools
import signal
import sys
import time
from pathlib import Path

from pkg import hq_adapter

_DEBUG = False
_ADAPTER = None

LIB_PATH = Path(__file__).absolute().parent / "lib"

# adding lib folder to path
sys.path.append(f"{LIB_PATH}")


def cleanup(signum, frame):
    """Clean up any resources before exiting."""
    if _ADAPTER is not None:
        _ADAPTER.close_proxy()

    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    _ADAPTER = hq_adapter.hq_Adapter(verbose=_DEBUG)

    # Wait until the proxy stops running, indicating that the gateway shut us
    # down.
    while _ADAPTER.proxy_running():
        time.sleep(2)
