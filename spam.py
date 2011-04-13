from __future__ import division

import os
import random
import re
import sys

import models

from bayes_filter import BayesFilter
from ratio_filter import RatioFilter
from result import Result
from settings import *


####################
#get_mail_list
#PURPOSE: searches a directory for mail file to load
#PARAMS:
#       root: the directory to be searched
#       (format): the file format (defaults to FILE_FORMAT)
#RETURNS: the list of email files
####################
def get_mail_list(root, format=FILE_FORMAT):
    mail = []

    for (path, directories, filenames) in os.walk(root):
        for file in filenames:
            if file.endswith(format):
                mail.append(path + '/' + file)

    return mail


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
            if re_cont.search(line):  # continuation of previous value
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
    filters = train(train_mail, filters)

    print 'testing on ' + str(len(test_mail)) + ' files'
    (filters, results) = test(test_mail, filters)

    return filters, results


def init(args):
    root = DEFAULT_DIR
    num_train = DEFAULT_TRAIN

    if len(args) > 0:
        root = args[0]

        if len(args) > 1:
            try:
                num_train = int(args[1])
            except ValueError:
                print 'invalid number for training, using default'

    filters = models.filters

    #load mail
    mail = get_mail_list(root)
    random.shuffle(mail)

    #calculate the number of training files
    max = RATIO_TO_TRAIN * len(mail)
    if max < num_train:
        num_train = int(max)

    return (filters, mail, num_train)


def test_models(filters, mail, num_train):
    if len(filters) > 0:
        (filters, results) = train_test(filters, mail, num_train)

        for key in filters:
            print str(key) + ':'
            print '\tFalse Positives: ' + \
                results[key].false_positive_percentage()
            print '\t\t' + str(results[key].false_positives) + \
                ' of ' + str(results[key].num_valid)
            print '\tFalse Negatives: ' + \
                results[key].false_negative_percentage()
            print '\t\t' + str(results[key].false_negatives) + \
                ' of ' + str(results[key].num_spam)


"""def optimize_models(opt_mode, restriction, filters, mail, num_train, \
        mins, maxes, prev = None):
    again = (prev == None)

    sections = {}
    for key in mins:
        thirds = (maxes[key]-mins[key])/3
        sections[key] = [mins[key], mins[key]+thirds, \
            maxes[key]-thirds, maxes[key]]

    scores = {}
    for key in filters:
        scores[key] = {}

        for section in sections[key]:
            scores[key][section] = {FALSE_NEG:[],FALSE_POS:[]}

    for num_trials in xrange(OPT_TRIALS):
        random.shuffle(mail)
        for section_num in xrange(4):
            #set threshold value
            for key in filters:
                filters[key][FTHRESHHOLD] = sections[key][section_num]

            filters = train_test(filters, mail, num_train)

            for key in filters:
                scores[key][sections[key][section_num]][FALSE_POS] \
                    .append(filters[key][FTESTING][FALSE_POS]/filters \
                        [key][FTESTING][FNUM_VALID])
                scores[key][sections[key][section_num]][FALSE_NEG] \
                    .append(filters[key][FTESTING][FALSE_NEG]/filters[key] \
                        [FTESTING][FNUM_SPAM])


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
                        if fp < restriction and  ((best_fn > fn) or \
                            (best_fn == fn and best_fp > fp)):
                            better = True
                    elif best_fp > fp:
                        better = True
                else:
                    if best_fn < restriction:
                        if fn < restriction and  ((best_fp > fp) or \
                            (best_fp == fp and best_fn > fn)):
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
        print '\tOld Range: ' + str(mins[key]) + \
            ' to ' + str(maxes[key])
        print '\tNew Range: ' + str(new_mins[key]) + \
            ' to ' + str(new_maxes[key])

        if not again:
            again = ((prev[key][FALSE_POS] != 0 and \
                (fp/prev[key][FALSE_POS]) <= MIN_IMPROVEMENT) or \
                (prev[key][FALSE_NEG] != 0 and (fn/prev[key][FALSE_NEG]) \
                <= MIN_IMPROVEMENT))

    if again:
        optimize_models(opt_mode, restriction, filters, mail, num_train, \
            new_mins, new_maxes, new_prev)
    else:
        print 'TRAINING COMPLETE'
        fout = open('results.txt', 'w')
        for key in new_prev:
            fout.write(str(key) + ': ' + \
                str(new_prev[key][FTHRESHHOLD]) + '\n')
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
            #optimize_models(opt_mode, restriction, filters, mail, \
            #num_train, mins, maxes)
        else:
            print 'unrecognized mode'
    else:  # mode not given, run in test mode
        args = sys.argv[1:]
        (filters, mail, num_train) = init(args)
        test_models(filters, mail, num_train)
