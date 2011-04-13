from __future__ import division

import math

from simple_filter import SimpleFilter
from word import Word


class BayesFilter(SimpleFilter):
    equal_ratio = None
    num_spam = None
    num_valid = None

    def __init__(self, sections, threshold, weight, format, equal_ratio=True):
        super(BayesFilter, self).__init__(sections, threshold, weight, format)
        self.equal_ratio = equal_ratio

    def init_model(self):
        super(BayesFilter, self).init_model()
        self.num_spam = 0
        self.num_valid = 0

    def train(self, message, is_spam):
        weight = 1

        if is_spam:
            self.num_spam += 1
        else:
            self.num_valid += 1
            weight = self.weight

        words = self.words(message)
        used = {}

        for word in words:
            if len(word) > 0:
                if not word in used:
                    used[word] = 1

                    if not word in self.model:
                        self.model[word] = Word()

                    self.model[word].iterate(weight, is_spam)

    def predict(self, message):
        prob_spam = 0.5

        if not self.equal_ratio:
            prob_spam = self.num_spam / (self.num_spam + self.num_valid)

        prob_valid = 1 - prob_spam

        probabilities = []
        skip = False

        prediction = False
        confidence = 0

        words = self.words(message)

        for word in words:
            if len(word) > 0 and word in self.model:
                prob_ws_s = (self.model[word].spam / self.num_spam) * prob_spam
                prob_wv_v = (self.model[word].valid / self.num_valid) \
                                * prob_valid
                probabilities.append(prob_ws_s / (prob_ws_s + prob_wv_v))

        if len(probabilities) > 0:
            p = 1
            np = 1

            for prob in probabilities:
                if prob == 0:
                    prob = 0.0001
                if prob == 1:
                    prob = 0.9999

                p *= prob
                np *= (1 - prob)

                if p < 0.001 or np < 0.001:
                    if math.isinf(100000 * p):
                        prediction = True
                        confidence = 1
                        skip = True
                        break
                    if math.isinf(100000 * np):
                        prediction = False
                        confidence = 1
                        skip = True
                        break

                    p *= 100000
                    np *= 100000

            if not skip:
                confidence = p / (p + np)
                prediction = (self.threshold < confidence)

        return prediction, self.calculate_confidence(confidence)
