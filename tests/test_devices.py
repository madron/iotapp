import unittest
from iotapp import devices
from iotapp.events import Event
from iotapp.test import TestClient, TestLogger


class EntityTest(unittest.TestCase):
    def test_get_subscribe_topics(self):
        entity = devices.Entity()
        self.assertEqual(entity.get_subscribe_topics(), [])

    def test_get_events(self):
        entity = devices.Entity()
        self.assertEqual(entity.get_events('topic', 'value'), [])

    def test_on_connect(self):
        entity = devices.Entity()
        self.assertEqual(entity.on_connect(), None)


class ButtonTest(unittest.TestCase):
    def test_text(self):
        topic = 'state/topic'
        button = devices.Button(
            state_topic = topic,
            state_type = 'text',
            state_value_click = 'pressed',
            state_value_template = '',
        )
        self.assertEqual(button.get_events(topic, 'pressed'), [Event('click')])
        self.assertEqual(button.get_events(topic, ''), [])

    def test_aqara_lumi_sensor_switch_aq2(self):
        topic = 'state/topic'
        button = devices.Button(
            state_topic = topic,
            state_type = 'json',
            state_value_click = 'single',
            state_value_template = '{{ value.click }}',
        )
        payload = '{"battery":100,"voltage":3015,"linkquality":0,"click":"single"}'
        self.assertEqual(button.get_events(topic, payload), [Event('click')])
        payload = '{"battery":100,"voltage":3015,"linkquality":0,"click":""}'
        self.assertEqual(button.get_events(topic, payload), [])

    def test_get_subscribe_topics(self):
        button = devices.Button(state_topic = 'state/topic')
        self.assertEqual(button.get_subscribe_topics(), ['state/topic'])


class LightShellyRgbw2Test(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()
        self.state_topic = 'shellies/shelly_rgbw2/white/0'
        self.command_topic = 'shellies/shelly_rgbw2/white/0/command'
        self.light = devices.Light(
            client=self.client,
            logger=self.logger,
            state_topic = self.state_topic,
            command_topic = self.command_topic,
        )
        self.assertEqual(self.light.state, None)

    def test_get_subscribe_topics(self):
        self.assertEqual(self.light.get_subscribe_topics(), ['shellies/shelly_rgbw2/white/0'])

    def test_get_events_on(self):
        events = self.light.get_events(self.state_topic, 'on')
        self.assertEqual(events, [])
        self.assertEqual(self.light.state, 'on')

    def test_get_events_off(self):
        events = self.light.get_events(self.state_topic, 'off')
        self.assertEqual(events, [])
        self.assertEqual(self.light.state, 'off')

    def test_turn_on(self):
        self.light.turn_on()
        self.assertEqual(self.client.published, [('shellies/shelly_rgbw2/white/0/command', 'on')])

    def test_turn_off(self):
        self.light.turn_off()
        self.assertEqual(self.client.published, [('shellies/shelly_rgbw2/white/0/command', 'off')])

    def test_toggle_state_on(self):
        self.light.state = 'on'
        command = self.light.toggle()
        self.assertEqual(command, 'off')
        self.assertEqual(self.client.published, [('shellies/shelly_rgbw2/white/0/command', 'off')])

    def test_toggle_state_off(self):
        self.light.state = 'off'
        command = self.light.toggle()
        self.assertEqual(command, 'on')
        self.assertEqual(self.client.published, [('shellies/shelly_rgbw2/white/0/command', 'on')])

    def test_toggle_state_unavailable(self):
        self.light.state = None
        command = self.light.toggle()
        self.assertEqual(command, None)
        self.assertEqual(self.client.published, [])
        self.assertEqual(self.logger.logged, [('warning', 'toggle - state not available')])
