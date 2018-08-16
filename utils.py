import json
import random
import collections

from nltk.tokenize import word_tokenize


class PoemTemplateLoader(object):
    """
    Хранит шаблоны стихотворений, полученные из собрания сочинений.
    Шаблон — обработанное и обрезанное стихотворение в виде набора отдельных токенов (слов).
    """

    def __init__(self, poems_file, min_lines=3, max_lines=8):
        self.poet_templates = collections.defaultdict(list)
        self.min_lines = min_lines
        self.max_lines = max_lines

        self.load_poems(poems_file)

    def load_poems(self, poems_file):
        with open(poems_file) as fin:
            poems = json.load(fin)

        for poem in poems:
            template = self.poem_to_template(poem['content'])
            if len(template) >= self.min_lines:
                self.poet_templates[poem['poet_id']].append(template)

    def poem_to_template(self, poem_text):
        poem_lines = poem_text.split('\n')[:self.max_lines]
        poem_template = []
        for line in poem_lines:
            line_tokens = [token.lower() for token in word_tokenize(line) if token.isalpha()]
            poem_template.append(line_tokens)
        return poem_template

    def get_random_template(self, poet_id, random_seed):
        """Возвращает случайный шаблон выбранного поэта"""
        if not self.poet_templates[poet_id]:
            raise KeyError('Unknown poet "%s"' % poet_id)
        random.seed(random_seed)
        return random.choice(self.poet_templates[poet_id])

    def __repr__(self):
        return '\n'.join(['{}: {}'.format(k, len(v)) for k,v in self.poet_templates.items()])


