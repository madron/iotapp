#!/bin/env python
import argparse
import os
from iotapp.manager import AppManager


def get_default():
    return dict(
        name=os.environ.get('IOTAPP_NAME', None),
        config=os.environ.get('IOTAPP_CONFIG', None),
        apps=os.environ.get('IOTAPP_APPS', None),
        devices=os.environ.get('IOTAPP_DEVICES', None),
    )

def main():
    default = get_default()
    parser = argparse.ArgumentParser(prog='iotapp', description='Iot Applications.')
    parser.add_argument('-n', '--name', metavar='NAME', help='Application name', default=default['name'])
    parser.add_argument('-c', '--config', metavar='DIR', help='Configuration directory', default=default['config'])
    parser.add_argument('-d', '--devices', metavar='FILE', help='Devices file', default=default['devices'])
    parser.add_argument('-a', '--apps', metavar='FILE', help='Apps file', default=default['apps'])
    args = parser.parse_args()

    # Config
    config_dir = args.config or ''
    devices_file = args.devices
    apps_file = args.apps
    if not devices_file:
        devices_file = os.path.join(config_dir, 'devices.yml')
    if not apps_file:
        apps_file = os.path.join(config_dir, 'apps.yml')

    # Manager
    manager = AppManager(name=args.name, devices=devices_file, apps=apps_file, )
    manager.run()


if __name__ == '__main__':
    main()
