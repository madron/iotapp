class Event(object):
    def __init__(self, type, *args, **kwargs):
        self.type = type
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, event):
        if self.type == event.type and self.args == event.args and self.kwargs == event.kwargs:
            return True
        return False

    def __repr__(self):
        return '{} {} {}'.format(self.type, self.args, self.kwargs)

    def __str__(self):
        return self.__repr__()
