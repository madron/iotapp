class Device:
    def __init__(self, name):
        self.name = name
        self.entities = self.get_entities()

    def get_entities(self):
        return dict()
