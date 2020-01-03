import argparse
import asyncio
import logging
import os
import signal
import sys
from iotapp import IotApp

MQTT_HOST = os.getenv('MQTT_HOST', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
CONFIG_DIR = os.getenv('CONFIG_DIR', 'config')
APPS_DIR = os.path.join(CONFIG_DIR, 'apps')
APPS_DIR = os.getenv('APPS_DIR', APPS_DIR)
DEFAULT_LOGLEVEL = 'INFO'
LOGLEVEL_CHOICES = [
    'DEBUG',
    'INFO',
    'WARNING',
    'ERROR',
    'CRITICAL',
]
SHUTDOWN_SIGNALS = [
    signal.SIGHUP,
    signal.SIGTERM,
    signal.SIGINT,
    signal.SIGQUIT,
]

parser = argparse.ArgumentParser(prog='iotapp', description='Iot application daemon')
parser.add_argument('--config-dir', metavar='DIR', type=str, default=CONFIG_DIR, help="Config directory. Default: '{}'".format(CONFIG_DIR))
parser.add_argument('--apps-dir', metavar='DIR', type=str, default=APPS_DIR, help="Applications directory. Default: '{}'".format(APPS_DIR))
parser.add_argument('--mqtt-host', type=str, default=MQTT_HOST, help="Default: '{}'".format(MQTT_HOST))
parser.add_argument('--mqtt-port', type=int, default=MQTT_PORT, help="Default: '{}'".format(MQTT_PORT))
parser.add_argument('--loglevel', metavar='LEVEL', type=str,
                    default=DEFAULT_LOGLEVEL, choices=LOGLEVEL_CHOICES,
                    help="Log level. Default: '{}'".format(DEFAULT_LOGLEVEL))
parser.add_argument('--debug', action='store_true')


async def signal_handler(signal, controller):
    logging.info('Terminating on user request: received {} signal'.format(signal.name))
    await controller.stop()


async def shutdown(controller):
    # Controller
    logging.info('Stopping IotApp')
    await controller.stop()
    # Tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    logging.info('Outstanding tasks: {}'.format(len(tasks)))
    [task.cancel() for task in tasks]
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        pass
    logging.info('Shutdown completed')


async def handle_exception(coro, loop):
    try:
        await coro
    except asyncio.CancelledError:
        pass


def main():
    args = parser.parse_args()
    log_level = getattr(logging, args.loglevel, DEFAULT_LOGLEVEL)
    logging.basicConfig(level=log_level, format='%(levelname)-8s %(message)s')

    logging.debug('Arguments')
    logging.debug('sys.argv: {}'.format(sys.argv))
    logging.debug('args: {}'.format(args))
    logging.debug('config_dir: {}'.format(args.config_dir))
    logging.debug('apps_dir: {}'.format(args.apps_dir))

    mqtt_config = dict(
        host=args.mqtt_host,
        port=args.mqtt_port,
    )
    iot_app = IotApp(
        config_dir=args.config_dir,
        apps_dir=args.apps_dir,
        mqtt_config=mqtt_config,
    )
    loop = asyncio.get_event_loop()
    loop.set_debug(args.debug)

    # Signal handlers
    for s in SHUTDOWN_SIGNALS:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(signal_handler(s, iot_app)))

    # Loop
    try:
        loop.run_until_complete(handle_exception(iot_app.run(), loop))
    finally:
        loop.run_until_complete(shutdown(iot_app))
        loop.stop()


if __name__ == '__main__':
    main()
