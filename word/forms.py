import csv
import itertools
import collections

from nltk.tokenize import word_tokenize
from tqdm import tqdm

Word = collections.namedtuple("Word", ["word", "phonetic_form", "morph_form", "lemma"])


class WordForms(object):
    def __init__(self, phonetic, accent, pos, corpus_reader):
        self.phonetic = phonetic
        self.accent = accent
        self.pos = pos
        self.corpus = corpus_reader()
        print('Corpus length: {}'.format(len(self.corpus)))
        self.word_by_form = self._parse_word_forms()

    def _parse_word_forms(self):
        word_by_form = collections.defaultdict(set)
        for token in tqdm(self.corpus, desc='Parsing word forms'):
            if token.isalpha():
                words = list(self.parse(token))
                for word in words:
                    word_by_form[(word.phonetic_form, word.morph_form)].add(word)

        return word_by_form

    def parse_text(self, text, phonetic=True):
        """
        Parse using contextual information

        :param phonetic: Extract phonetic information
        :param text:
        :return:
        """
        if phonetic:
            tokens_accents = self.accent.multy_accent(text)
        else:
            tokens = word_tokenize(text)
            tokens_accents = zip(tokens, [0]*len(tokens))

        for token, accent in tokens_accents:
            if accent == -1:  # special case for puctuation
                yield Word(token, None, None, token)
            if phonetic:
                syllables = self.phonetic.syllables_count(token)
            else:
                syllables = 0
            phonetic_form = (syllables, accent)
            # Use only first POS option and hope it is right
            morph_form, lemma = self.pos.get_word_forms(token)[0]
            yield Word(token, phonetic_form, morph_form, lemma)

    def parse(self, word, word_accents=None):
        """
        Can be multiple forms because each word can have multiple POS interpretations
        :param word:
        :return:
        """

        word_syllables = self.phonetic.syllables_count(word)

        if word_accents is None:
            word_accents = self.accent.accent_syllable(word)
        if word_accents is None:
            return []

        word_forms_and_lemmas = self.pos.get_word_forms(word)

        for accent, form_n_lemma in itertools.product(word_accents, word_forms_and_lemmas):
            morph_form, lemma = form_n_lemma
            phonetic_form = (word_syllables, accent)
            yield Word(word, phonetic_form, morph_form, lemma)


def get_csv_reader(corpora_file, column):
    def read():
        corpora_tokens = []
        with open(corpora_file) as fin:
            reader = csv.DictReader(fin)
            for row in tqdm(reader,
                            desc='Reading corpora',
                            total=51000):  # ~
                paragraph = row[column]
                paragraph_tokens = word_tokenize(paragraph.lower())
                corpora_tokens += paragraph_tokens
        return set(corpora_tokens)

    return read
