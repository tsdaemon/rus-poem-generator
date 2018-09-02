import json
import random
import collections
import html
import re
import os

from nltk.tokenize import word_tokenize
from tqdm import tqdm

from constants import PUNCTUATION

MAX_LINE_LENGTH = 100


def untokenize_template(template):
    return "\n".join([untokenize(line) for line in template])


def untokenize(tokens):
    return "".join([
            " " + i if not i.startswith("'") and i not in PUNCTUATION else i for i in tokens
        ]).strip()



class PoemTemplateLoaderBase:
    def __init__(self, poems_file, min_lines=3, max_lines=8, debug_folder=None):
        self.poet_templates = collections.defaultdict(list)
        self.original_poems = collections.defaultdict(list)
        self.min_lines = min_lines
        self.max_lines = max_lines

        poems = self._load_poems(poems_file)
        self._preprocess_poems(poems)
        assert all(
            len(template) <= max_lines
            for poet, templates in self.poet_templates.items()
            for template in templates
        )
        assert all(
            len(' '.join(words)) <= MAX_LINE_LENGTH
            for poet, templates in self.poet_templates.items()
            for template in templates
            for lines in template
            for words in lines
        )
        if debug_folder is not None:
            self._store(debug_folder)

    def _preprocess_poems(self, poems):
        for poem in poems:
            template = self._poem_to_template(poem['content'])
            if len(template) >= self.min_lines:
                self.poet_templates[poem['poet_id']].append(template)
                self.original_poems[poem['poet_id']].append(poem['content'])

    def _load_poems(self, poems_file):
        with open(poems_file) as fin:
            return json.load(fin)

    def _poem_to_template(self, poem_text):
        poem_lines = poem_text.split('\n')[:self.max_lines]
        poem_template = []
        for line in poem_lines:
            line_tokens = [token.lower() for token in word_tokenize(line)]
            poem_template.append(line_tokens)
        return poem_template

    def get_random_template(self, poet_id, random_seed):
        if not self.poet_templates[poet_id]:
            raise KeyError('Unknown poet "%s"' % poet_id)
        random.seed(random_seed)
        return random.choice(self.poet_templates[poet_id])

    def __repr__(self):
        return '\n'.join(['{}: {}'.format(k, len(v)) for k, v in self.poet_templates.items()])

    def _store(self, debug_folder):
        for poet, templates in self.poet_templates.items():
            file = os.path.join(debug_folder, poet + '.txt')
            with open(file, 'w') as f:
                for template in templates:
                    f.write(untokenize_template(template) + '\n\n')


class PoemTemplateLoader(PoemTemplateLoaderBase):
    number_first = re.compile("^\d{1,4}\..*$", re.U | re.M)
    dots = re.compile("^[\.…]*$|· · ·", re.U | re.M)
    brackets = re.compile("[\[<_]([^\[<_]*)[\]>_]", re.U)
    line_breaks = re.compile("\n{2,}", re.U)
    not_russian = re.compile("[a-z]", re.U)
    forbidden_chars = re.compile("[*`']", re.U)

    def _preprocess_poems(self, poems):
        for poem in tqdm(poems):
            poet_id = poem['poet_id']
            content = html.unescape(poem['content']).lower()
            self.original_poems[poet_id].append(content)
            content = self._preprocess_content(content)
            templates = self._split_on_templates(content)
            self.poet_templates[poem['poet_id']] += \
                [self._create_array(t) for t in templates]

    def _preprocess_content(self, content):
        # remove special symbols
        content = self.forbidden_chars.sub("", content)
        # remove strings which starts from 1111
        content = self.number_first.sub("", content)
        # remove dots lines
        content = self.dots.sub("", content)
        # replace optional strings
        content = self.brackets.sub(r"\1", self.brackets.sub(r"\1", content))
        content = self._remove_options(content)
        content = self.forbidden_chars.sub("", content)
        return content

    def _remove_options(self, content):
        lines_to_remove = []
        lines = content.split('\n')
        start = -1
        for i in range(len(lines)):
            if lines[i].startswith('а)'):
                start = i
                lines[i] = lines[i][2:].strip()
            if lines[i].startswith('б)'):
                length = i-start
                r = list(range(i, i+length))
                lines_to_remove += r

        return '\n'.join([l for i, l in enumerate(lines) if i not in lines_to_remove])

    def _split_on_templates(self, content):
        # first split by double or more line breaks
        tt = self.line_breaks.split(content)
        results = []
        for t in tt:
            results += list(self._split_on_templates2(t))

        return [r for r in results if r]

    def _split_on_templates2(self, t):
        lines = t.split('\n')
        start = 0
        for i in range(len(lines)):
            line = lines[i]
            if i - start >= self.max_lines:
                yield '\n'.join(lines[start:i])
                start = i

            # check for invalid string
            if len(line) > MAX_LINE_LENGTH or self.not_russian.match(line):
                start = i + 1

        if not len(lines) - start < self.min_lines:
            yield '\n'.join(lines[start:])

    def _create_array(self, poem):
        return [word_tokenize(line) for line in poem.split('\n')]

