from iotapp import entities
from iotapp.devices.base import Device

class Rgbw2(Device):
    def __init__(self, name, mode='white'):
        self.mode = mode
        super().__init__(name=name)

    def get_entities(self):
        entity = dict()
        config = dict(
            state_topic='shellies/{}/white/0'.format(self.name),
            command_topic='shellies/{}/white/0/command'.format(self.name),
        )
        entity[self.name] = {'class': entities.Light, 'config': config}
        return entity
