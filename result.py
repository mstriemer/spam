from __future__ import division


class Result(object):
    total = None
    false_positives = None
    false_negatives = None
    num_spam = None
    num_valid = None

    def __init__(self, *args):
        self.total = 0
        self.false_positives = 0
        self.false_negatives = 0
        self.num_spam = 0
        self.num_valid = 0
        for result in args:
            self.total += result.total
            self.false_positives += result.false_positives
            self.false_negatives += result.false_negatives
            self.num_spam += result.num_spam
            self.num_valid += result.num_valid
        if len(args) > 0:
            self.total = self.total / len(args)
            self.false_positives = self.false_positives / len(args)
            self.false_negatives = self.false_negatives / len(args)
            self.num_spam = self.num_spam / len(args)
            self.num_valid = self.num_valid / len(args)

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
        return self.false_positive_ratio() * 100

    def false_negative_ratio(self):
        if self.num_spam > 0:
            return (self.false_negatives / self.num_spam)
        else:
            return 0

    def false_negative_percentage(self):
        return self.false_negative_ratio() * 100
