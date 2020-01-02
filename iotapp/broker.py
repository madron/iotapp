class Broker():
    def __init__(
        self,
        host='localhost',
        port=1883,
        username='',
        password='',
        client_id='',
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
