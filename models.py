from bayes_filter import BayesFilter
from ratio_filter import RatioFilter
from mark_bayes_filter import BayesFilter as MarkBayesFilter
from mark_bayes_filter import optimization_parameters

from bias_filter import BiasFilter

from settings import *

filters = {}

#formattatting

#for params in optimization_parameters():
#    filters['mark_bayes_%s' % (params,)] = MarkBayesFilter(*params)

#filters['bayes_third'] = BayesFilter(SECTIONS, 0.0788497688361, (1/3), False)
#filters['bayes_half'] = BayesFilter(SECTIONS, 0.0788497688361, (1/2), False)
#filters['bayes_normal'] = BayesFilter(SECTIONS, 0.0788497688361, 1, False)
#filters['bayes_double'] = BayesFilter(SECTIONS, 0.0788497688361, 2, False)
#filters['bayes_triple'] = BayesFilter(SECTIONS, 0.0788497688361, 3, False)

#email sections
#filters['bayes_body'] = BayesFilter([BODY], 0.0788497688361, 1, False)
#filters['bayes_body_from'] = \
#    BayesFilter([BODY, FROM], 0.0788497688361, 1, False)
#filters['bayes_body_subject'] = \
#    BayesFilter([BODY, SUBJECT], 0.0788497688361, 1, False)
#filters['bayes_body_subject_from']  = \
#    BayesFilter([BODY, SUBJECT, FROM], 0.0788497688361, 1, False)

bb = BayesFilter([BODY, SUBJECT, FROM], 0.2, 2, True)
rb = RatioFilter([BODY, SUBJECT, FROM], 0.35, 2, True)
bayes = BayesFilter([BODY, SUBJECT, FROM], 0.0788497688361, 1, False)

filters['MC Bayes'] = BiasFilter(bb, False, bayes)
filters['MC Ratio'] = BiasFilter(rb, False, bayes)
filters['Bayes'] = bayes

bs = BayesFilter(SECTIONS, 0, 0.25, True)

filters['E'] = BiasFilter(bb, False, BiasFilter(bs, True, bayes))