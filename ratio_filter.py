from __future__ import division

from simple_filter import SimpleFilter
from word import Word


class RatioFilter(SimpleFilter):
    def init_model(self):
        self.model = {}

    def train(self, message, is_spam):
        weight = 1

        if not is_spam:
            weight = self.weight

        words = self.words(message)

        for word in words:
            if len(word) > 0:
                if not word in self.model:
                    self.model[word] = Word()

                self.model[word].iterate(weight, is_spam)

    def predict(self, message):
        words = self.words(message)

        score = 0
        for word in words:
            if len(word) > 0:
                if word in self.model:
                    score += self.model[word].spam_ratio()
                else:
                    score += self.threshold

        prediction = ((len(words) * self.threshold < score))
        confidence = score / len(words)
        
        #confidence = self.calculate_confidence(confidence)
        #prediction = confidence <= 0.5

        return prediction, confidence
