from __future__ import division


class Result(object):
    total = None
    false_positives = None
    false_negatives = None
    num_spam = None
    num_valid = None

    def __init__(self):
        self.total = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.num_spam = 0
        self.num_valid = 0

    def add(self, prediction, actual):
        self.total += 1

        if actual:
            self.num_spam += 1
            if not prediction:
                self.false_negatives += 1
        else:
            self.num_valid += 1
            if prediction:
                self.false_positives += 1

    def false_positive_ratio(self):
        if self.num_valid > 0:
            return (self.false_positives / self.num_valid)
        else:
            return 0

    def false_positive_percentage(self):
        return str((self.false_positive_ratio()) * 100) + '%'

    def false_negative_ratio(self):
        if self.num_spam > 0:
            return (self.false_negatives / self.num_spam)
        else:
            return 0

    def false_negative_percentage(self):
        return str((self.false_negative_ratio()) * 100) + '%'
