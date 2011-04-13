from filter import Filter

class BiasFilter(Filter):

    biased_filter = None
    bias = None
    alt_filter = None

    def __init__(self, biased_filter, bias, alt_filter):
        self.biased_filter = biased_filter
        self.bias = bias
        self.alt_filter = alt_filter

    def train(self, message, is_spam):
        self.biased_filter.train(message, is_spam)
        self.alt_filter.train(message, is_spam)

    def predict(self, message):
        prediction, confidence = self.biased_filter.predict(message)

        if prediction == self.bias:
            prediction, confidence = self.alt_filter.predict(message)

        return prediction, confidence
