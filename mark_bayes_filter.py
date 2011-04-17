from __future__ import division

sections_to_use = ['body', 'received', 'delivered-to', 'from', 'return-path',
                   'to']

def optimization_parameters():
    # threshold, strength, prob_spam, num_words_to_use
    thresholds = (0.999, 0.9999, 0.99999)
    strengths = (0.10, 0.15, 0.25)
    prob_spams = (0.4, 0.5, 0.6)
    num_words_to_uses = (15, 25, 35)
    for threshold in thresholds:
        for strength in strengths:
            for prob_spam in prob_spams:
                for num_words_to_use in num_words_to_uses:
                    yield (threshold, strength, prob_spam, num_words_to_use)


class BayesFilter(object):
    def __init__(self, threshold, strength, prob_spam, num_words_to_use):
        self.threshold = threshold
        self.strength = strength
        self.prob_spam = prob_spam
        self.num_words_to_use = num_words_to_use
        self.init_model()

    def init_model(self):
        self.model = FilterModel(self.strength, self.prob_spam,
                                                        self.num_words_to_use)

    def train(self, message, is_spam):
        found_words = {}
        for section, words in message.items():
            if section in sections_to_use:
                for word in words.split():
                    if word not in found_words:
                        self.model.found_word(word, is_spam)
                        found_words[word] = True

    def predict(self, message):
        classification = self.model.classify(message)
        return classification > self.threshold, classification


class FilterModel(object):
    s = 0.5
    prob_spam = 0.5

    def __init__(self, strength, prob_spam, num_words_to_use):
        self.words = {}
        self.spam = 0
        self.ham = 0
        self.s = strength
        self.prob_spam = prob_spam
        self.num_words_to_use = num_words_to_use

    def found_word(self, word, is_spam):
        if word in self.words:
            self.words[word].found(is_spam)
        else:
            self.words[word] = BayesWord(word, is_spam)
        if is_spam:
            self.spam += 1
        else:
            self.ham += 1

    @property
    def total(self):
        return self.spam + self.ham * 2

    def classify(self, message):
        probabilities = self._interesting_probabilities_for_message(message)
        if len(probabilities) > 0:
            spam_probability = reduce(lambda memo, prob: memo * prob,
                                                            probabilities, 1)
            inverse_spam_probability = reduce(lambda memo, prob: memo *
                                                (1 - prob), probabilities, 1)
            divisor = spam_probability + inverse_spam_probability
            if divisor == 0:
                return 0
            else:
                return spam_probability / divisor
        else:
            return 0

    def _interesting_probabilities_for_message(self, message):
        probabilities = self._probabilities_for_message(message)
        return self._find_interesting_probabilities(probabilities)

    def _find_interesting_probabilities(self, probabilities):
        probabilities.sort(key=lambda p: abs(0.5 - p))
        # print probabilities
        return probabilities[-self.num_words_to_use:]

    def _probabilities_for_message(self, message):
        probabilities = []
        for section, words in message.items():
            if section in sections_to_use:
                for word in words.split():
                    if word in self.words and self.words[word].total > 3:
                        bayes_word = self.words[word]
                        prob_spam_for_word = bayes_word.spamicity(self.spam,
                                                                    self.ham)
                        probabilities.append(self._weight_probability(
                                        prob_spam_for_word, self.words[word]))
        return probabilities

    def _weight_probability(self, prob_spam_for_word, word):
        return (self.s * self.prob_spam + (word.ham + word.spam) *
                        prob_spam_for_word) / (self.s + word.ham + word.spam)


class BayesWord(object):
    def __init__(self, word, is_spam):
        self.word = word
        self.spam = 1 if is_spam else 0
        self.ham = 1 if not is_spam else 0

    def found(self, is_spam):
        if is_spam:
            self.spam += 1
        else:
            self.ham += 1

    def spamicity(self, spam, ham):
        prob_word_in_spam = self.spam / spam
        prob_word_in_ham = self.ham / ham
        return prob_word_in_spam / (prob_word_in_spam + prob_word_in_ham)

    @property
    def total(self):
        return self.spam + self.ham * 2
