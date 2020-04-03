import unittest
from iotapp.devices import base


class DeviceTest(unittest.TestCase):
    def test_init(self):
        device = base.Device('kitchen')
        self.assertEqual(device.name, 'kitchen')
        self.assertEqual(device.entities, dict())
