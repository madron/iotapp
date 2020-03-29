from iotapp.base import IotApp


class Toggle(IotApp):
    def __init__(self, button=None, light=None, **kwargs):
        super().__init__(**kwargs)
        self.button = self.entity_library[button]


    def on_button_click(self):
        state = self.light.toggle()
        self.logger.info('on_button_click -> light: {}'.format(state))

