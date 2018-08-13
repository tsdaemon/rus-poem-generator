import json
import random
import collections

import numpy as np
from scipy.spatial.distance import cosine

from nltk.tokenize import word_tokenize
from gensim.models import KeyedVectors
from pymystem3 import Mystem


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

    def get_random_template(self, poet_id):
        """Возвращает случайный шаблон выбранного поэта"""
        if not self.poet_templates[poet_id]:
            raise KeyError('Unknown poet "%s"' % poet_id)
        return random.choice(self.poet_templates[poet_id])


class Word2vecProcessor(object):
    """Объект для работы с моделью word2vec сходства слов"""

    def __init__(self, w2v_model_file):
        self.mystem = Mystem()
        self.word2vec = KeyedVectors.load_word2vec_format(w2v_model_file, binary=True)
        self.lemma2word = {word.split('_')[0]: word for word in self.word2vec.index2word}

    def word_vector(self, word):
        lemma = self.mystem.lemmatize(word)[0]
        word = self.lemma2word.get(lemma)
        return self.word2vec[word] if word in self.word2vec else None

    def text_vector(self, text):
        """Вектор текста, получается путем усреднения векторов всех слов в тексте"""
        word_vectors = [
            self.word_vector(token)
            for token in word_tokenize(text.lower())
            if token.isalpha()
            ]
        word_vectors = [vec for vec in word_vectors if vec is not None]
        return np.mean(word_vectors, axis=0)

    def distance(self, vec1, vec2):
        if vec1 is None or vec2 is None:
            return 2
        return cosine(vec1, vec2)