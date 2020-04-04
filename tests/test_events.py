import unittest
from iotapp import events
from iotapp.events import Event


class EventTest(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(Event('status', 'online'), Event('status', 'online'))

    def test_not_equal(self):
        self.assertNotEqual(Event('status', 'online'), Event('status', 'offline'))

    def test_repr(self):
        self.assertEqual(str(Event('status', 'online')), "status ('online',) {}")
