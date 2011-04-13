###############
# KEYS   KEYS #
###############
SPAM = 'spam'
BODY = 'body'
FROM = 'from'
SUBJECT = 'subject'

###############
#VALUES VALUES#
###############

#MODE VALUES
TEST_MODE = '-t'                # normal mode in which models are tested
OPT_MODE = '-o'                 # optimize more in which thresholds are optimized for either reducing false-postives or false negatives

#OPT_MODE VALUES
OPT_SPAM = 'spam'               # flag for optimizing thresholds based on maximizing spam detection
OPT_VALID = 'valid'             # flag for optimizing thresholds based on minimizing misclassifying valid email
OPT_TRIALS = 4                  # number of trials at each level. more trials is slower, but more accurate
MIN_IMPROVEMENT = 0.95          # new results/old results must be smaller than MIN_IMPROVEMENT for another test run to occur
OPT_RESULTS = 'results.txt'     # file results are saved to

#FILE DEFAULTS
DEFAULT_DIR = '/mail'           # directory mail is stored in
DEFAULT_TRAIN = 0               # number of messages to use for training

#DEFAULT VALUES
FILE_FORMAT = '.eml'            # what format, the emails are in
RATIO_TO_TRAIN = 0.1            # what ratio of emails can be used for training
PLAIN_ONLY = False

#FILTER VALUES
NUM_SETTINGS = 5                # number of settings per model
RATIO = 'ratio'                 # ratio model
BAYES = 'bayes'                 # bayes model
SECTIONS = [BODY, SUBJECT, FROM]
NO_FORMAT = 'none'              # no formatting on body text
PLAIN_FORMAT = 'plain'          # just plaintext sections of body text
USE_DEFAULT = 'DEFAULT'         # use the default value

#MODEL VALUES
MODELS = [BAYES, RATIO]
MODEL_THRESHHOLDS = {BAYES: 0.24, RATIO: 0.24}

###############
#   REGEXES   #
###############
PAIR = '^(.*?):(.*)'            # header pairs
CONT = '^[ \t].*'               # continuation of pair
MIME = '^This (?:(?:(?:is a multi-?part message)|(?:message is)) in MIME format)|(?: is a MIME-(?:encapsulated|formatted) message)'  # mime lines in email
FORMATTING = '^--(?:-_=)*(?:(?:(?:[Nn]ext_?)?[Pp]art)|(?:[Bb]oundary)|(?:Apple-Mail)|(?:[a-fA-Z0-9]+)|(?:mimepart))'  # line signifying change in mime-type
CON_TYPE = '[Cc]ontent-?[Tt]ype'  # formatting for line containing mime-type
PLAIN = 'text/plain'            # mime-type for plaintext
RE_NL = '^[> ]*(.*)(?:=[0-9]*)*$'  # reply formatting and newline formatting
TAG = '^(.*?)</?(.*?)>(.*?)$'   # html/xml tag
