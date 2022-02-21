"""Module defining entrypoint."""
import asyncio

from hydroqc2mqtt.daemon import Hydroqc2Mqtt


def main():
    """Entrypoint function."""
    dev = Hydroqc2Mqtt()
    asyncio.run(dev.async_run())


if __name__ == "__main__":
    main()
