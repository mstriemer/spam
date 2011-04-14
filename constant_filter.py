from filter import Filter


class ConstantFilter(Filter):
    value = None

    def __init__(self, value):
        self.value = value

    def predict(self, message):
        return self.value, 1