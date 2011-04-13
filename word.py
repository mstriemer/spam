from __future__ import division

class Word(object):
    valid = None
    spam = None
    total = None
    
    def __init__(self):
        self.valid = 0
        self.spam = 0
        self.total = 0
    
    def iterate(self, amount, is_spam):
        if is_spam:
            self.spam += amount
        else:
            self.valid += amount
        
        self.total += amount

    def spam_ratio(self):
        return self.spam/self.total