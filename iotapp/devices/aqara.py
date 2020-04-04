from iotapp import entities
from .base import Device


class Button(Device):
    def __init__(self, name):
        super().__init__(name=name)


    def get_entities(self):
        entity = dict()
        config = dict(
            state_topic='zigbee/{}'.format(self.name),
            state_value_click = 'single',
            state_template = '{{ value.click }}',
        )
        entity[self.name] = {'class': entities.Button, 'config': config}
        return entity
