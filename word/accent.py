import json
import bz2
import collections
from abc import ABC
import regex as re
from word.phonetic import VOWELS
from russtress import Accent as RusAccent


def _parse_word(word, symbol='`'):
    tilda_indices = [i for i, x in enumerate(word) if x == symbol]
    vowels_indices = [i for i, x in enumerate(word) if x in VOWELS]
    accent_indices = [i for i, vi in enumerate(vowels_indices) if vi + 1 in tilda_indices]
    return ''.join(c for c in word if c != symbol), tuple(accent_indices)


class AccentBase(ABC):
    def __init__(self):
        super().__init__()
        self.accents_dict = None

    def accent_syllable(self, word):
        return self.accents_dict.get(word, None)


class Accent(AccentBase):
    def __init__(self, accent_file):
        super().__init__()
        with bz2.BZ2File(accent_file) as fin:
            accents_dict = json.load(fin)
            self.accents_dict = {w:[i] for w, i in accents_dict.items()}


class MultyAccentRuss:
    def __init__(self):
        self.stress_model = RusAccent()

    def multy_accent(self, text):
        multy_accent_text = self.stress_model.put_stress(text)
        tokens = multy_accent_text.split()
        tokens_accents = [_parse_word(t, symbol='\'') for t in tokens]
        return tokens_accents


class AccentRussianNlp(AccentBase, MultyAccentRuss):
    def __init__(self, accent_file):
        super().__init__()
        self.filter_regex = re.compile("^[а-я].*", re.UNICODE)

        with open(accent_file) as f:
            self.accents_dict = self._load(f)

    def _load(self, f):
        accents_dict = collections.defaultdict(list)
        for w in f.readlines():
            w = w.strip()
            if not self.filter_regex.match(w):
                continue
            if "&amp;" in w:
                continue

            word, accents = _parse_word(w)
            accents_dict[word].append(tuple(accents))

        return accents_dict





