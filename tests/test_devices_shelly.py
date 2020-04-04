import unittest
from iotapp import entities
from iotapp.devices import shelly


class Rgbw2Test(unittest.TestCase):
    def test_white(self):
        device = shelly.Rgbw2('kitchen', mode='white')
        self.assertEqual(len(device.get_entities()), 1)
        entity = device.get_entities()['kitchen']
        self.assertEqual(entity['class'], entities.Light)
        config = entity['config']
        self.assertEqual(config['availability_topic'], 'shellies/kitchen/online')
        self.assertEqual(config['availability_online'], 'true')
        self.assertEqual(config['availability_offline'], 'false')
        self.assertEqual(config['state_topic'], 'shellies/kitchen/white/0')
        self.assertEqual(config['command_topic'], 'shellies/kitchen/white/0/command')
        self.assertEqual(config['brightness_state_topic'], 'shellies/kitchen/white/0/status')
        self.assertEqual(config['brightness_state_template'], '{{ value.brightness }}')
        self.assertEqual(config['brightness_command_topic'], 'shellies/kitchen/white/0/set')
        self.assertEqual(config['brightness_command_template'], '{"brightness": {{ value }}}')
