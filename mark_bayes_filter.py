from __future__ import division

sections_to_use = ['body', 'received', 'delivered-to', 'from', 'return-path',
                   'to']

def optimization_parameters():
    # threshold, strength, prob_spam, num_words_to_use
    thresholds = (0.999, 0.9999,)
    strengths = (0.1, 0.2, 0.3)
    prob_spams = (0.4, 0.5, 0.6)
    num_words_to_uses = (15, 25, 35)
    test_thresholds = (-1,)
    for threshold in thresholds:
        for strength in strengths:
            for prob_spam in prob_spams:
                for num_words_to_use in num_words_to_uses:
                    for test_threshold in test_thresholds:
                        yield (threshold, strength, prob_spam,
                                            num_words_to_use, test_threshold)


class BayesFilter(object):
    def __init__(self, threshold, strength, prob_spam, num_words_to_use,
                                                            test_threshold):
        self.threshold = threshold
        self.strength = strength
        self.prob_spam = prob_spam
        self.num_words_to_use = num_words_to_use
        self.test_threshold = test_threshold
        self.init_model()

    def init_model(self):
        self.model = FilterModel(self.strength, self.prob_spam,
                                    self.num_words_to_use, self.test_threshold)

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
        prediction = classification > self.threshold
        self.train(message, prediction)
        return prediction, classification


class FilterModel(object):
    s = 0.5
    prob_spam = 0.5

    def __init__(self, strength, prob_spam, num_words_to_use, test_threshold):
        self.words = {}
        self.spam = 0
        self.ham = 0
        self.s = strength
        self.prob_spam = prob_spam
        self.num_words_to_use = num_words_to_use
        self.test_threshold = test_threshold

    def found_word(self, word, is_spam):
        if word in self.words:
            self.words[word].found(is_spam)
        else:
            self.words[word] = BayesWord(word, is_spam)
        if is_spam:
            self.spam += 1
        else:
            self.ham += 2

    @property
    def total(self):
        return self.spam + self.ham

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
        if self.test_threshold > 0:
            return self._find_interesting_probabilities_threshold(
                                                                probabilities)
        else:
            return self._find_interesting_probabilities_number(probabilities)

    def _find_interesting_probabilities_number(self, probabilities):
        probabilities.sort(key=lambda p: abs(0.5 - p))
        return probabilities[-self.num_words_to_use:]

    def _find_interesting_probabilities_threshold(self, probabilities):
        return [p for p in probabilities if abs(0.5 - p) < self.test_threshold]

    def _probabilities_for_message(self, message):
        probabilities = []
        for section, words in message.items():
            if section in sections_to_use:
                for word in words.split():
                    word = word.strip('.,!?@:;()[]{}\\/"\'')
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
        self.spam = 0
        self.ham = 0
        self.found(is_spam)

    def found(self, is_spam):
        if is_spam:
            self.spam += 1
        else:
            self.ham += 2

    def spamicity(self, spam, ham):
        prob_word_in_spam = self.spam / spam
        prob_word_in_ham = self.ham / ham
        return prob_word_in_spam / (prob_word_in_spam + prob_word_in_ham)

    @property
    def total(self):
        return self.spam + self.ham
