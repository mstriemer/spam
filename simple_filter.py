import re

from filter import Filter
from settings import PLAIN, RE_NL, MIME, FORMATTING, CON_TYPE, TAG


class SimpleFilter(Filter):
    sections = None
    model = None
    threshold = None
    weight = None
    format = None

    def __init__(self, sections, threshhold, weight, format):
        super(SimpleFilter, self).__init__()
        self.sections = sections
        self.threshold = threshhold
        self.weight = weight
        self.format = format

        self.init_model()

    def init_model(self):
        self.model = {}

    def calculate_confidence(self, value):
        if value > self.threshold:
            range = 1 - self.threshold
            return value / range
        elif value < threshold:
            return value / self.threshold
        else:  # value exactly at threshhold
            return 0

    def words(self, message, format=None):
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
            else:  # should never be else
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
