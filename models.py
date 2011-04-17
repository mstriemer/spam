from bayes_filter import BayesFilter
from ratio_filter import RatioFilter
from mark_bayes_filter import BayesFilter as MarkBayesFilter
from mark_bayes_filter import optimization_parameters
from settings import *

filters = {}

#formattatting
# filters['ratio_unformatted'] = RatioFilter(SECTIONS, 0.301278335656, 1, False)
# filters['ratio_formatted'] = RatioFilter(SECTIONS, 0.2580593353, 1, True)
# filters['bayes_unformatted'] = BayesFilter(SECTIONS, 0.0788497688361, 1, False)
# filters['bayes_formatted'] = BayesFilter(SECTIONS, 0.24, 1, True)
# filters['mark_bayes'] = MarkBayesFilter(0.95)

for params in optimization_parameters():
    filters['mark_bayes_%s' % (params,)] = MarkBayesFilter(*params)

#filters['bayes_third'] = BayesFilter(SECTIONS, 0.0788497688361, (1/3), False)
#filters['bayes_half'] = BayesFilter(SECTIONS, 0.0788497688361, (1/2), False)
#filters['bayes_normal'] = BayesFilter(SECTIONS, 0.0788497688361, 1, False)
#filters['bayes_double'] = BayesFilter(SECTIONS, 0.0788497688361, 2, False)
#filters['bayes_triple'] = BayesFilter(SECTIONS, 0.0788497688361, 3, False)

#filters['bayes_body'] = BayesFilter([BODY], 0.0788497688361, 1, False)
#filters['bayes_body_from'] = \
#    BayesFilter([BODY, FROM], 0.0788497688361, 1, False)
#filters['bayes_body_subject'] = \
#    BayesFilter([BODY, SUBJECT], 0.0788497688361, 1, False)
#filters['bayes_body_subject_from']  = \
#    BayesFilter([BODY, SUBJECT, FROM], 0.0788497688361, 1, False)
