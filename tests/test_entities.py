import unittest
from iotapp import entities
from iotapp.events import Event
from iotapp.test import TestClient, TestLogger


class EntityTest(unittest.TestCase):
    def test_get_subscribe_topics(self):
        entity = entities.Entity()
        self.assertEqual(entity.get_subscribe_topics(), [])

    def test_get_events(self):
        entity = entities.Entity()
        self.assertEqual(entity.get_events('topic', 'value'), [])

    def test_on_connect(self):
        entity = entities.Entity()
        self.assertEqual(entity.on_connect(), None)

    def test_availability_not_configured(self):
        entity = entities.Entity()
        self.assertEqual(entity.get_subscribe_topics(), [])
        self.assertEqual(entity.available, None)


class EntityAvailabilityTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()
        self.entity = entities.Entity(
            name='entity',
            availability_topic='status',
            client=self.client,
            logger=self.logger,
        )

    def test_availability_unknown(self):
        self.assertEqual(self.entity.get_subscribe_topics(), ['status'])
        self.assertEqual(self.entity.available, None)
        self.assertEqual(self.logger.logged, [])

    def test_availability_unknown_online(self):
        self.entity.available = None
        self.assertEqual(self.entity.get_events('status', 'online'), [Event('availability', 'online')])
        self.assertTrue(self.entity.available)
        self.assertEqual(self.logger.logged, [('info', 'Status online')])

    def test_availability_offline_online(self):
        self.entity.available = False
        self.assertEqual(self.entity.get_events('status', 'online'), [Event('availability', 'online')])
        self.assertTrue(self.entity.available)
        self.assertEqual(self.logger.logged, [('info', 'Status online')])

    def test_availability_online_online(self):
        self.entity.available = True
        self.assertEqual(self.entity.get_events('status', 'online'), [])
        self.assertTrue(self.entity.available)
        self.assertEqual(self.logger.logged, [])

    def test_availability_unknown_offline(self):
        self.entity.available = None
        self.assertEqual(self.entity.get_events('status', 'offline'), [Event('availability', 'offline')])
        self.assertFalse(self.entity.available)
        self.assertEqual(self.logger.logged, [('warning', 'Status offline')])

    def test_availability_online_offline(self):
        self.entity.available = True
        self.assertEqual(self.entity.get_events('status', 'offline'), [Event('availability', 'offline')])
        self.assertFalse(self.entity.available)
        self.assertEqual(self.logger.logged, [('warning', 'Status offline')])

    def test_availability_offline_offline(self):
        self.entity.available = False
        self.assertEqual(self.entity.get_events('status', 'offline'), [])
        self.assertFalse(self.entity.available)
        self.assertEqual(self.logger.logged, [])


class ButtonTest(unittest.TestCase):
    def test_text(self):
        topic = 'state/topic'
        button = entities.Button(
            state_topic = topic,
            state_type = 'text',
            state_value_click = 'pressed',
            state_value_template = '',
        )
        self.assertEqual(button.get_events(topic, 'pressed'), [Event('click')])
        self.assertEqual(button.get_events(topic, ''), [])

    def test_aqara_lumi_sensor_switch_aq2(self):
        topic = 'state/topic'
        button = entities.Button(
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
        button = entities.Button(state_topic = 'state/topic')
        self.assertEqual(button.get_subscribe_topics(), ['state/topic'])


class LightShellyRgbw2Test(unittest.TestCase):
    def setUp(self):
        self.client = TestClient()
        self.logger = TestLogger()
        self.state_topic = 'shellies/shelly_rgbw2/white/0'
        self.command_topic = 'shellies/shelly_rgbw2/white/0/command'
        self.light = entities.Light(
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
