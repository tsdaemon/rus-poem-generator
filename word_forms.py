import bz2
import csv
import itertools

import json


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

    def get_form(self, word):
        word_syllables = self.syllables_count(word)
        word_accent = self.accent_syllable(word)
        return (word_syllables, word_accent)

    def sound_distance(self, word1, word2):
        """Фонетическое растояние на основе расстояния Левенштейна по окончаниям
        (число несовпадающих символов на соответствующих позициях)"""
        suffix_len = 3
        suffix1 = (' ' * suffix_len + word1)[-suffix_len:]
        suffix2 = (' ' * suffix_len + word2)[-suffix_len:]

        distance = sum((ch1 != ch2) for ch1, ch2 in zip(suffix1, suffix2))
        return distance


class WordForms(object):
    def __init__(self, phonetic, pos):
        self.phonetic = phonetic
        self.pos = pos

    def form_dictionary_from_csv(self, corpora_file, column='paragraph', max_docs=30000):
        """Загрузить словарь слов из CSV файла с текстами, индексированный по формам слова.
        Возвращает словарь вида:
            {форма: {множество, слов, кандидатов, ...}}
            форма — (<число_слогов>, <номер_ударного>)
        """

        corpora_tokens = []
        with open(corpora_file) as fin:
            reader = csv.DictReader(fin)
            for row in itertools.islice(reader, max_docs):
                paragraph = row[column]
                paragraph_tokens = word_tokenize(paragraph.lower())
                corpora_tokens += paragraph_tokens

        word_by_form = collections.defaultdict(set)
        for token in corpora_tokens:
            if token.isalpha():
                word_syllables = self.syllables_count(token)
                word_accent = self.accent_syllable(token)
                form = (word_syllables, word_accent)
                word_by_form[form].add(token)

        return word_by_form