from iotapp.base import IotApp


class Toggle(IotApp):
    def __init__(self, button=None, light=None, **kwargs):
        super().__init__(**kwargs)
        self.add_entity('button', button)
        self.add_entity('light', light)

    def on_button_click(self):
        state = self.light.toggle()
        self.logger.info('on_button_click -> light: {}'.format(state))
