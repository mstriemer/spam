from filter import Filter


class ConfidenceFilter(Filter):

    confidence_filter = None
    higher_filter = None
    lower_filter = None
    value = None

    def __init__(self, confidence_filter, value, higher_filter, lower_filter):
        self.confidence_filter = confidence_filter
        self.value = value
        self.higher_filter = higher_filter
        self.lower_filter = lower_filter

    def train(self, message, is_spam):
        self.confidence_filter.train(message, is_spam)
        self.higher_filter.train(message, is_spam)
        self.lower_filter.train(message, is_spam)

    def predict(self, message):
        prediction, confidence = self.confidence_filter.predict(message)

        if confidence >= self.value:
            prediction, confidence = self.higher_filter.predict(message)
        else:
            prediction, confidence = self.lower_filter.predict(message)

        return prediction, confidence
