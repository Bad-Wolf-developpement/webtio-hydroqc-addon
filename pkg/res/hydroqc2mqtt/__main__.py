"""Module defining entrypoint."""
import asyncio
import argparse

from hydroqc2mqtt.daemon import Hydroqc2Mqtt


def _parse_cmd():
    parser = argparse.ArgumentParser(
            prog="hydroqc2mqtt",
            description='hydroqc2mqtt daemon')
    parser.add_argument('--mqtt-host',
                        required=False,
                        default=None,
                        help='Mqtt host address. Default: 127.0.0.1')
    parser.add_argument('--mqtt-port',
                        required=False,
                        default=None,
                        type=int,
                        help='Mqtt host port. Default: 1883')
    parser.add_argument('--mqtt-username',
                        required=False,
                        default=None,
                        help='Mqtt username')
    parser.add_argument('--mqtt-password',
                        required=False,
                        default=None,
                        help='Mqtt password')
    parser.add_argument('--mqtt-discovery-root-topic',
                        required=False,
                        default='homeassistant',
                        help='Mqtt root topic for Home Assistant discovery. Default: homeassistant')
    parser.add_argument('--mqtt-data-root-topic',
                        required=False,
                        default='hydroqc',
                        help='Mqtt root topic for sensors data. Default: homeassistant')
    parser.add_argument('--log-level',
                        required=False,
                        default='info',
                        help='Log level')
    parser.add_argument('--config',
                        required=False,
                        default=None,
                        help='Config file path. Default: config.yaml')
    parser.add_argument('--hq-username',
                        required=False,
                        default=None,
                        help='HydroQuebec username')
    parser.add_argument('--hq-password',
                        required=False,
                        default=None,
                        help='HydroQuebec password')
    parser.add_argument('--hq-name',
                        required=False,
                        default=None,
                        help='Name of your account. Used for prefixing data. Default: myhouse')
    parser.add_argument('--hq-customer-id',
                        required=False,
                        default=None,
                        help='HydroQuebec customer ID')
    parser.add_argument('--hq-account-id',
                        required=False,
                        default=None,
                        help='HydroQuebec account ID')
    parser.add_argument('--hq-contract-id',
                        required=False,
                        default=None,
                        help='HydroQuebec contract ID')
    parser.add_argument('--run-once',
                        required=False,
                        default=False,
                        action='store_true',
                        help='Run once and exit. Useful to run as cronjob.')

    cmd_args = parser.parse_args()
    return cmd_args


def main():
    """Entrypoint function."""
    cmd_args = _parse_cmd()
    #import ipdb;ipdb.set_trace()

    dev = Hydroqc2Mqtt(
        mqtt_host=cmd_args.mqtt_host,
        mqtt_port=cmd_args.mqtt_port,
        mqtt_username=cmd_args.mqtt_username,
        mqtt_password=cmd_args.mqtt_password,
        mqtt_discovery_root_topic=cmd_args.mqtt_discovery_root_topic,
        mqtt_data_root_topic=cmd_args.mqtt_data_root_topic,
        config_file=cmd_args.config,
        run_once=cmd_args.run_once,
        log_level=cmd_args.log_level,
        hq_username=cmd_args.hq_username,
        hq_password=cmd_args.hq_password,
        hq_name=cmd_args.hq_name,
        hq_customer_id=cmd_args.hq_customer_id,
        hq_account_id=cmd_args.hq_account_id,
        hq_contract_id=cmd_args.hq_contract_id,
        )
    asyncio.run(dev.async_run())


if __name__ == "__main__":
    main()
