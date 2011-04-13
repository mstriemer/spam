class Filter(object):

    def train(self, message, is_spam):
        pass

    def predict(self, message):
        return False, 0
