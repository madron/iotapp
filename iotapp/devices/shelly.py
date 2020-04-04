from iotapp import entities
from iotapp.devices.base import Device


class Rgbw2(Device):
    def __init__(self, name, mode='white'):
        self.mode = mode
        super().__init__(name=name)

    def get_entities(self):
        entity = dict()
        config = dict(
            availability_topic='shellies/{}/online'.format(self.name),
            availability_online='true',
            availability_offline='false',
            state_topic='shellies/{}/white/0'.format(self.name),
            command_topic='shellies/{}/white/0/command'.format(self.name),
            brightness_state_topic='shellies/{}/white/0/status'.format(self.name),
            brightness_state_template='{{ value.brightness }}',
            brightness_command_topic='shellies/{}/white/0/set'.format(self.name),
            brightness_command_template='{"brightness": {{ value }}}',

        )
        entity[self.name] = {'class': entities.Light, 'config': config}
        return entity
