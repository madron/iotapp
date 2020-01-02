import unittest
from iotapp.broker import Broker


class BrokerInitTest(unittest.TestCase):
    def test_empty(self):
        broker = Broker()
        self.assertEqual(broker.host, 'localhost')
        self.assertEqual(broker.port, 1883)

    def test_host(self):
        broker = Broker(host='example.com')
        self.assertEqual(broker.host, 'example.com')
        self.assertEqual(broker.port, 1883)

    def test_port(self):
        broker = Broker(port=8883)
        self.assertEqual(broker.host, 'localhost')
        self.assertEqual(broker.port, 8883)

    def test_host_port(self):
        broker = Broker(host='example.com', port=8883)
        self.assertEqual(broker.host, 'example.com')
        self.assertEqual(broker.port, 8883)
