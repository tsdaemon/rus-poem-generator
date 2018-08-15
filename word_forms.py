import bz2
import csv
import itertools
import collections

import json
from nltk.tokenize import word_tokenize
from pymorphy2 import MorphAnalyzer
from tqdm import tqdm


class Phonetic(object):
    """Объект для работы с фонетическими формами слова"""

    def __init__(self, accent_file, vowels='уеыаоэёяию'):
        self.vowels = vowels
        with bz2.BZ2File(accent_file) as fin:
            self.accents_dict = json.load(fin)

    def syllables_count(self, word):
        """Количество гласных букв (слогов) в слове"""
        return sum((ch in self.vowels) for ch in word)

    def accent_syllable(self, word):
        """Номер ударного слога в слове"""
        default_accent = (self.syllables_count(word) + 1) // 2
        return self.accents_dict.get(word, default_accent)

    def sound_distance(self, word1, word2):
        """Фонетическое растояние на основе расстояния Левенштейна по окончаниям
        (число несовпадающих символов на соответствующих позициях)"""
        suffix_len = 3
        suffix1 = (' ' * suffix_len + word1)[-suffix_len:]
        suffix2 = (' ' * suffix_len + word2)[-suffix_len:]

        distance = sum((ch1 != ch2) for ch1, ch2 in zip(suffix1, suffix2))
        return distance


DO_NOT_WANT_TO_REPLACE = ['эх', 'и', 'еще', 'уже', 'когда', 'ли']


class WordForms(object):

    def __init__(self, phonetic, corpus_reader):
        self.phonetic = phonetic
        self.pos = MorphAnalyzer()
        self.corpus = corpus_reader()
        print('Corpus length: {}'.format(len(self.corpus)))
        self.word_by_form = self.parse_word_forms()

    def parse_word_forms(self):
        word_by_form = collections.defaultdict(set)
        for token in tqdm(self.corpus, desc='Parsing word forms'):
            if token.isalpha():
                forms_n_lemmas = self.get_forms(token)
                for form, lemma in forms_n_lemmas:
                    word_by_form[form].add((token, lemma))

        return word_by_form

    def get_forms(self, word):
        """
        Can be multiple forms because each word can have multiple POS interpretations
        :param word:
        :return:
        """

        # Деякі виключення — слова які не варто заміняти
        if word in DO_NOT_WANT_TO_REPLACE:
            return [(None, None)]

        word_syllables = self.phonetic.syllables_count(word)
        word_accent = self.phonetic.accent_syllable(word)
        forms = []
        for parse in self.pos.parse(word):
            word_pos = str(parse.tag.POS)
            word_gender = str(parse.tag.gender)
            word_number = str(parse.tag.number)
            word_tense = str(parse.tag.tense)
            word_case = str(parse.tag.case)
            lemma = str(parse.normal_form)

            form = (word_syllables, word_accent, word_pos, word_gender, word_number,
                    word_tense, word_case)
            forms.append((form, lemma))
        return list(set(forms))


def get_csv_reader(corpora_file, column, max_docs=50000):
    def read():
        corpora_tokens = []
        with open(corpora_file) as fin:
            reader = csv.DictReader(fin)
            total = max_docs
            for row in tqdm(itertools.islice(reader, max_docs),
                            desc='Reading corpora',
                            total=total):
                paragraph = row[column]
                paragraph_tokens = word_tokenize(paragraph.lower())
                corpora_tokens += paragraph_tokens
        return set(corpora_tokens)

    return read
