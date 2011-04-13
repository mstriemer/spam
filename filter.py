from __future__ import division

import math
import os
import random
import re
import sys

###############
# KEYS   KEYS #
###############
SPAM = 'spam'
BODY = 'body'
FROM = 'from'

###############
#VALUES VALUES#
###############

#MODE VALUES
TEST_MODE = '-t'                #normal mode in which models are tested
OPT_MODE = '-o'                 #optimize more in which threshholds are optimized for either reducing false-postives or false negatives

#OPT_MODE VALUES
OPT_SPAM = 'spam'               #flag for optimizing threshholds based on maximizing spam detection
OPT_VALID = 'valid'             #flag for optimizing threshholds based on minimizing misclassifying valid email
OPT_TRIALS = 4                  #number of trials at each level. more trials is slower, but more accurate
MIN_IMPROVEMENT = 0.95          #new results/old results must be smaller than MIN_IMPROVEMENT for another test run to occur
OPT_RESULTS = 'results.txt'     #file results are saved to

#FILE DEFAULTS
DEFAULT_FILE = 'default.train'  #file containing training values
DEFAULT_DIR = '/mail'           #directory mail is stored in
DEFAULT_TRAIN = 0               #number of messages to use for training

#DEFAULT VALUES
FILE_FORMAT = '.eml'            #what format, the emails are in
RATIO_TO_TRAIN = 0.1            #what ratio of emails can be used for training
PLAIN_ONLY = False

#FILTER VALUES
NUM_SETTINGS = 5                #number of settings per model
RATIO = 'ratio'                 #ratio model
BAYES = 'bayes'                 #bayes model
SECTIONS = [BODY]
NO_FORMAT = 'none'              #no formatting on body text
PLAIN_FORMAT = 'plain'          #just plaintext sections of body text
USE_DEFAULT = 'DEFAULT'         #use the default value

#MODEL VALUES
MODELS = [BAYES, RATIO]
MODEL_THRESHHOLDS = {BAYES:0.24, RATIO:0.24}

###############
#   REGEXES   #
###############
PAIR = '^(.*?):(.*)'            #header pairs
CONT = '^[ \t].*'               #continuation of pair
MIME = '^This (?:(?:(?:is a multi-?part message)|(?:message is)) in MIME format)|(?: is a MIME-(?:encapsulated|formatted) message)' #mime lines in email
FORMATTING = '^--(?:-_=)*(?:(?:(?:[Nn]ext_?)?[Pp]art)|(?:[Bb]oundary)|(?:Apple-Mail)|(?:[a-fA-Z0-9]+)|(?:mimepart))' #line signifying change in mime-type
CON_TYPE = '[Cc]ontent-?[Tt]ype'#formatting for line containing mime-type
PLAIN = 'text/plain'            #mime-type for plaintext
RE_NL = '^[> ]*(.*)(?:=[0-9]*)*$'#reply formatting and newline formatting
TAG = '^(.*?)</?(.*?)>(.*?)$'   #html/xml tag

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
        return (self.false_positives/self.num_valid)

    def false_positive_percentage(self):
        return str((self.false_positive_ratio())*100) + '%'

    def false_negative_ratio(self):
        return (self.false_negatives/self.num_spam)

    def false_negative_percentage(self):
        return str((self.false_negative_ratio())*100) + '%'

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

class Filter(object):
    name = None
    sections = None
    model = None
    threshhold = None
    weight = None
    format = None

    def __init__(self, name, sections, threshhold, weight, format):
        self.name = name
        self.sections = sections
        self.threshhold = threshhold
        self.weight = weight
        self.format  = format
        
        self.init_model()
    
    def init_model(self):
        self.model = {}

    def words(self, message, format = None):
        if format == None:
            format = self.format
    
        re_renl = re.compile(RE_NL)
        re_skip = re.compile(MIME)
        re_formatting = re.compile(FORMATTING)
        re_type = re.compile(CON_TYPE)
        re_tag = re.compile(TAG)
        
        text = ''
        for section in self.sections:
            if section in message:
                text += message[section]
                
        lines = text.split('\n')
        formed_lines = []

        for line in lines:
            m = re_renl.search(line)
        
            if m:
                formed_lines.append(m.group(1) + ' ')
            else: #should never be else
                formed_lines.append(line + ' ')

        words = ''
        if format:
            skipping = False
            checking = False
            wait_til_blank = False
            for line in formed_lines:
                if len(line.strip()) == 0:
                    wait_til_blank = False
                if not re_skip.search(line):
                    if re_formatting.search(line):
                        checking = True
                    elif checking:
                        if re_type.search(line):
                            skipping = not (PLAIN in line)
                            checking = False
                            wait_til_blank = True
                    elif not skipping and not wait_til_blank:
                        m = re_tag.search(line)
                        while m:
                            words += m.group(1) + ' '
                            line = m.group(3)

                            m = re_tag.search(line)
                        words += line
            if len(words.strip()) == 0:
                return self.words(message, False)
        else:
            for line in formed_lines:
                m = re_tag.search(line)
                
                while m:
                    words += m.group(1) + ' ' + m.group(2)
                    line = m.group(3)

                    m = re_tag.search(line)
                
                words += line

        return words.split(' ')
    
    def train(self, message, is_spam):
        pass
    
    def predict(self, message):
        return False, 0

class BayesFilter(Filter):
    equal_ratio = None
    num_spam = None
    num_valid = None

    def __init__(self, name, sections, threshhold, weight, format, equal_ratio=True):
        super(BayesFilter, self).__init__(name, sections, threshhold, weight, format)
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
            prob_spam = self.num_spam/(self.num_spam + self.num_valid)
        
        prob_valid = 1 - prob_spam
        
        probabilities = []
        skip = False
        
        prediction = False
        confidence = 0
        
        words = self.words(message)
        
        for word in words:
            if len(word) > 0 and word in self.model:
                prob_ws_s = (self.model[word].spam/self.num_spam)*prob_spam
                prob_wv_v = (self.model[word].valid/self.num_valid)*prob_valid
                probabilities.append(prob_ws_s/(prob_ws_s+prob_wv_v))
        
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
                    if math.isinf(100000*p):
                        prediction = True
                        confidence = 1
                        skip = True
                        break
                    if math.isinf(100000*np):
                        prediction = False
                        confidence = 1
                        skip = True
                        break
                    
                    p *= 100000
                    np *= 100000

            if not skip:
                confidence = p/(p + np)
                prediction = (self.threshhold < confidence)
        
        return prediction, confidence

class RatioFilter(Filter):
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
                    score += self.threshhold

        prediction = ((len(words)*self.threshhold < score))
        confidence = score/len(words)
        
        return prediction, confidence

####################
#get_mail_list
#PURPOSE: searches a directory for mail file to load
#PARAMS:
#       root: the directory to be searched
#       (format): the file format (defaults to FILE_FORMAT)
#RETURNS: the list of email files
####################
def get_mail_list(root, format = FILE_FORMAT):
    mail = []

    for (path, directories, filenames) in os.walk(root):
        for file in filenames:
            if file.endswith(format):
                mail.append(path + '/' + file)

    return mail

####################
#load_filter
#PURPOSE: loads a filter
#PARAMS:
#       unformatted
#RETURNS: filter
####################
def load_filter(unformatted):
    values = unformatted.split(',')
    valid = True
    reason = ''
    
    filter = None
    name = None
    type = None
    threshhold = None
    weight = None
    format = None
        
    if len(values) >= 6:
        name = values[0].strip()
        type = values[1].strip()
        sections = values[2].strip()
        format = values[3].strip()
        weight = values[4].strip()
        threshhold = values[5].strip()
        
        if sections == USE_DEFAULT:
            sections = SECTIONS
        else:
            sections = sections.split(' ')

        if format == USE_DEFAULT:
            format = False
        elif format == NO_FORMAT:
            format = False
        elif format == PLAIN_FORMAT:
            format = True
        else:
            reason = 'invalid formatting'
            valid = False
        
        if valid:
            if weight == USE_DEFAULT:
                weight = 1
            else:
                try:
                    weight = float(weight)
                except ValueError:
                    reason = 'weight value must be a number'
                    valid = False
                
        if valid:
            if threshhold == USE_DEFAULT:
                threshhold = MODEL_THRESHHOLDS[type]
            else:
                try:
                    threshhold = float(threshhold)

                    if threshhold < 0 or threshhold > 1:
                        reason = 'threshhold value must be between 0 and 1'
                        valid = False
                except ValueError:
                    reason = 'threshold is not a number'
                    valid = False
    else:
        reason = str(NUM_SETTINGS) + ' settings required'
        valid = False
    
    if type == BAYES:
        if len(values) == 7:
            try:
                equal_ratio = bool(values[6])
                
                filter = BayesFilter(name, sections, threshhold, weight, format, equal_ratio)
            except ValueError:
                reason = 'equal_ratio must be True or False'
                valid = False
        else:
            filter = BayesFilter(name, sections, threshhold, weight, format)
    elif type == RATIO:
        filter = RatioFilter(name, sections, threshhold, weight, format)
    else:
        reason = 'invalid filter type: ' + str(type)
        valid = False

    if valid:
        return filter
    else:
        print 'skipping: ' + str(unformatted).strip() + '\n\t' + reason
        return None

####################
#load_filters
#PURPOSE: loads a list of filters
#PARAMS:
#       filename: the file being loaded
#RETURNS: a list of filters
####################
def load_filters(file):
    
    fin = open(file, 'r')
    line = fin.readline()
    
    filters = {}
    
    while line:
        if not line.startswith('#') and len(line.strip()) > 0:
            filter = load_filter(line)
        
            if filter:
                filters[filter.name] = filter
        
        line = fin.readline()
    fin.close()

    return filters

####################
#reset_filters
#PURPOSE: resets a set of filters
#PARAMS:
#       filters: the list of filters
#RETURNS: filters
####################
def reset_filters(filters):
    for key in filters:
        filters[key].init_model()
    return filters

####################
#load_message
#PURPOSE: loads a mail file, and formats it
#PARAMS:
#       filename: the file being loaded
#RETURNS: the formatted email, whether it is spam
####################
def load_message(file):
    re_pair = re.compile(PAIR)
    re_cont = re.compile(CONT)
    re_mime = re.compile(MIME)
    
    spam = (SPAM in file)
    message = {}

    fin = open(file, 'r')
    line = fin.readline()
    field = None
    in_header = True

    while line and in_header:
        if len(line.strip()) == 0 or re_mime.search(line):
            in_header = False
        else:
            if re_cont.search(line): #continuation of previous value
                if field:
                    message[field] += ' ' + line.strip()
                    line = fin.readline()
                else:
                    in_header = False
            else:
                m = re_pair.search(line)
                
                if m:
                    field = m.group(1).lower()
                    message[field] = m.group(2)
                    line = fin.readline()
                else:
                    in_header = False

    body = ''
    while line:
        body += line
        line = fin.readline()
    message[BODY] = body
    
    return message, spam

####################
#train
#PURPOSE: trains models
#PARAMS:
#       mail: the training mail
#       filters: the list of filters to be trained
#RETURNS: the updated filters
####################
def train(mail, filters):
    for file in mail:
        message, is_spam = load_message(file)

        for key in filters:
            filters[key].train(message, is_spam)

    return filters

####################
#test
#PURPOSE: test models
#PARAMS:
#       mail: the testing mail
#       filters: the list of filters to be tested
#RETURNS: filters
####################
def test(mail, filters):
    results = {}
    for key in filters:
        results[key] = Result()

    for file in mail:
        message, is_spam = load_message(file)

        for key in filters:
            prediction, confidence = filters[key].predict(message)
            results[key].add(prediction, is_spam)
    return filters, results

####################
#train_test
#PURPOSE: trains and tests some models
#PARAMS:
#       mail: the testing mail
#       filters: the list of filters to be tested
#RETURNS: filters
####################
def train_test(filters, mail, num_train):
    train_mail = mail[0:num_train]
    test_mail = mail[num_train:]

    print 'training on ' + str(len(train_mail)) + ' files'
    filters = train(train_mail,filters)

    print 'testing on ' + str(len(test_mail)) + ' files'
    (filters, results) = test(test_mail,filters)

    return filters, results

def init(args):
    train_file = DEFAULT_FILE
    root = DEFAULT_DIR
    num_train = DEFAULT_TRAIN

    if len(args) > 0:
        train_file = args[0]

        if len(args) > 1:
            root = args[1]
            
            if len(args) > 2:
                num_train = int(args[2])

    filters = load_filters(train_file)

    #load mail
    mail = get_mail_list(root)
    random.shuffle(mail)

    #calculate the number of training files
    max = RATIO_TO_TRAIN*len(mail)
    if max < num_train:
        num_train = int(max)
    
    return (filters, mail, num_train)

def test_models(filters, mail, num_train):
    if len(filters) > 0:        
        (filters, results) = train_test(filters, mail, num_train)

        for key in filters:
            print str(key) + ':'
            print '\tFalse Positives: ' + results[key].false_positive_percentage()
            print '\t\t' + str(results[key].false_positives) + ' of ' + str(results[key].num_valid)
            print '\tFalse Negatives: ' + results[key].false_negative_percentage()
            print '\t\t' + str(results[key].false_negatives) + ' of ' + str(results[key].num_spam)

"""def optimize_models(opt_mode, restriction, filters, mail, num_train, mins, maxes, prev = None):
    again = (prev == None)

    sections = {}
    for key in mins:
        thirds = (maxes[key]-mins[key])/3
        sections[key] = [mins[key], mins[key]+thirds, maxes[key]-thirds, maxes[key]]
    
    scores = {}
    for key in filters:
        scores[key] = {}
        
        for section in sections[key]:
            scores[key][section] = {FALSE_NEG:[],FALSE_POS:[]}

    for num_trials in xrange(OPT_TRIALS):
        random.shuffle(mail)
        for section_num in xrange(4):
            #set threshhold value
            for key in filters:
                filters[key][FTHRESHHOLD] = sections[key][section_num]
        
            filters = train_test(filters, mail, num_train)
        
            for key in filters:
                scores[key][sections[key][section_num]][FALSE_POS].append(filters[key][FTESTING][FALSE_POS]/filters[key][FTESTING][FNUM_VALID])
                scores[key][sections[key][section_num]][FALSE_NEG].append(filters[key][FTESTING][FALSE_NEG]/filters[key][FTESTING][FNUM_SPAM])

            
            filters = reset_filters(filters)
    new_mins = {}
    new_maxes = {}
    new_prev = {}
    for key in filters:
        new_prev[key] = {}
    
        best_section = None
        best_fp = None
        best_fn = None
        
        for section in sections[key]:
            fp = 0
            fn = 0

            for i in xrange(OPT_TRIALS):
                fp += scores[key][section][FALSE_POS][i]
                fn += scores[key][section][FALSE_NEG][i]
            
            fp /= OPT_TRIALS
            fn /= OPT_TRIALS
            
            scores[key][section][FALSE_POS] = fp
            scores[key][section][FALSE_NEG] = fn
            
            better = False
            
            if not best_section:
                better = True
            else:
                if OPT_SPAM == opt_mode:
                    if best_fp < restriction:
                        if fp < restriction and  ((best_fn > fn) or (best_fn == fn and best_fp > fp)):
                            better = True
                    elif best_fp > fp:
                        better = True
                else:
                    if best_fn < restriction:
                        if fn < restriction and  ((best_fp > fp) or (best_fp == fp and best_fn > fn)):
                            better = True
                    elif best_fn > fn:
                        better = True

            if better:
                best_section = section
                best_fp = fp
                best_fn = fn
        
        if not best_section:
            new_mins[key] = mins[key]
            new_maxes[key] = maxes[key]
        else:
            
            if sections[key].index(best_section) < 2:
                new_mins[key] = sections[key][0]
                new_maxes[key] = sections[key][2]
            else:
                new_mins[key] = sections[key][1]
                new_maxes[key] = sections[key][3]
        
        new_prev[key][FALSE_POS] = fp
        new_prev[key][FALSE_NEG] = fn
        new_prev[key][FTHRESHHOLD] = best_section
        
        print filters[key][FNAME] + ':'
        print '\tFalse Positives: ' + str(100*(fp)) + '%'
        print '\tFalse Negatives: ' + str(100*(fn)) + '%'
        print '\tThreshhold: ' + str(best_section)
        print '\tOld Range: ' + str(mins[key]) + ' to ' + str(maxes[key])
        print '\tNew Range: ' + str(new_mins[key]) + ' to ' + str(new_maxes[key])

        if not again:
            again = ((prev[key][FALSE_POS] != 0 and (fp/prev[key][FALSE_POS]) <= MIN_IMPROVEMENT) or (prev[key][FALSE_NEG] != 0 and (fn/prev[key][FALSE_NEG]) <= MIN_IMPROVEMENT))

    if again:
        optimize_models(opt_mode, restriction, filters, mail, num_train, new_mins, new_maxes, new_prev)
    else:
        print 'TRAINING COMPLETE'
        fout = open('results.txt', 'w')
        for key in new_prev:
            fout.write(str(key) + ': ' + str(new_prev[key][FTHRESHHOLD]) + '\n')
        fout.close()"""

if __name__ == '__main__':    
    #find which mode the program is running in
    mode = sys.argv[1]
    
    if mode.startswith('-'):
        if mode == TEST_MODE:
            args = sys.argv[2:]
            (filters, mail, num_train) = init(args)

            test_models(filters, mail, num_train)
        elif mode == OPT_MODE:
            pass
            opt_mode = sys.argv[2]
            restriction = float(sys.argv[3])

            args = sys.argv[4:]
            (filters, mail, num_train) = init(args)
            
            mins = {}
            maxes = {}
            for key in filters:
                mins[key] = 0
                maxes[key] = 1
            print 'I need to update this'
            #optimize_models(opt_mode, restriction, filters, mail, num_train, mins, maxes)
        else:
            print 'unrecognized mode'
    else: #mode not given, run in test mode
        args = sys.argv[1:]
        (filters, mail, num_train) = init(args)
        test_models(filters, mail, num_train)