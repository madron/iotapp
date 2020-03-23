class Message:
    topic = None
    payload = None


class TestClient:
    def __init__(self):
        self.on_connect = None
        self.on_message = None
        self.subscribed = []
        self.published = []

    def connect(self, *args, **kwargs):
        self.on_connect(client=None, userdata=None, flags=None, rc=None)

    def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
        self.published.append((topic, payload))

    def subscribe(self, topic, qos=0, options=None, properties=None):
        self.subscribed.append(topic)

    def receive(self, topic, payload):
        msg = Message()
        msg.topic = topic
        msg.payload = payload.encode('utf-8')
        self.on_message(client=self, userdata=None, msg=msg)


class TestLogger:
    level_order = dict(
        debug=10,
        info=20,
        warning=30,
        error=40,
        exception=50,
    )
    def __init__(self, level='info'):
        self.level = level
        self.logged = []

    def append(self, msg, type):
        if self.level_order[type] >= self.level_order[self.level]:
            self.logged.append((type, msg))

    def debug(self, msg):
        self.append(msg, 'debug')

    def info(self, msg):
        self.append(msg, 'info')

    def warning(self, msg):
        self.append(msg, 'warning')

    def error(self, msg):
        self.append(msg, 'error')

    def exception(self, msg, exc_info=False):
        self.append(msg, 'exception')