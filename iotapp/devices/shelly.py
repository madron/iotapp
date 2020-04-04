from iotapp import entities
from iotapp.devices.base import Device


class Rgbw2(Device):
    def __init__(self, name, mode='white', channel1=None, channel2=None, channel3=None, channel4=None):
        self.mode = mode
        self.channels = [channel1, channel2, channel3, channel4]
        super().__init__(name=name)

    def get_entities(self):
        entity = dict()
        for number, name in enumerate(self.channels):
            if name:
                entity[name] = {'class': entities.Light, 'config': self.get_channel_config(number, self.name)}
        return entity

    def get_channel_config(self, number, name):
        return dict(
            availability_topic='shellies/{}/online'.format(name),
            availability_online='true',
            availability_offline='false',
            state_topic='shellies/{}/white/{}'.format(name, number),
            command_topic='shellies/{}/white/{}/command'.format(name, number),
            brightness_state_topic='shellies/{}/white/{}/status'.format(name, number),
            brightness_state_template='{{ value.brightness }}',
            brightness_command_topic='shellies/{}/white/{}/set'.format(name, number),
            brightness_command_template='{"brightness": {{ value }}}',
        )