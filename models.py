from bayes_filter import BayesFilter
from constant_filter import ConstantFilter
from ratio_filter import RatioFilter
from mark_bayes_filter import BayesFilter as MarkBayesFilter
from mark_bayes_filter import optimization_parameters

from bias_filter import BiasFilter
from confidence_filter import ConfidenceFilter

from settings import *

filters = {}

#formattatting
ru = RatioFilter(SECTIONS, 0.301278335656, 1, False)
filters['ratio_unformatted'] = ru
rf = RatioFilter(SECTIONS, 0.2580593353, 1, True)
filters['ratio_formatted'] = rf
#filters['bayes_unformatted'] = BayesFilter(SECTIONS, 0.0788497688361, 1, False)
#filters['bayes_formatted'] = BayesFilter(SECTIONS, 0.24, 1, True)

#for params in optimization_parameters():
#    filters['mark_bayes_%s' % (params,)] = MarkBayesFilter(*params)

#filters['bayes_third'] = BayesFilter(SECTIONS, 0.0788497688361, (1/3), False)
#filters['bayes_half'] = BayesFilter(SECTIONS, 0.0788497688361, (1/2), False)
#ruc = ConfidenceFilter(ru, 0.5, ConstantFilter(True), ConstantFilter(False))
#rfc = ConfidenceFilter(rf, 0.5, ConstantFilter(True), ConstantFilter(False))

#filters['ratio_unformatted_fixed?'] = ruc
#filters['ratio_formatted_fixed?'] = rfc

#weightings
#filters['bayes_third'] = BayesFilter(SECTIONS, 0.0788497688361, 0.33, False)
#filters['bayes_half'] = BayesFilter(SECTIONS, 0.0788497688361, 0.5, False)
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

#bias filter
#bb = BayesFilter([BODY, SUBJECT, FROM], 0.2, 2, True)
#rb = RatioFilter([BODY, SUBJECT, FROM], 0.35, 2, True)
#bayes = BayesFilter([BODY, SUBJECT, FROM], 0.0788497688361, 1, False)

#filters['MC Bayes'] = BiasFilter(bb, False, bayes)
#filters['MC Ratio'] = BiasFilter(rb, False, bayes)
#filters['Bayes'] = bayes

#bs = BayesFilter(SECTIONS, 0, 0.25, True)

#filters['E'] = BiasFilter(bb, False, BiasFilter(bs, True, bayes))