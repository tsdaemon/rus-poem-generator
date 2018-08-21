from abc import ABC

from pymorphy2 import MorphAnalyzer as MorphyPos


class PosAnalyzerBase(ABC):
    def get_post_form(self, word):
        pass


class PosAnalyzerMorphy(PosAnalyzerBase):
    def __init__(self):
        self.pos = MorphyPos()

    def get_word_forms(self, word):
        parses = self.pos.parse(word)
        forms_n_lemmas = []
        for parse in parses:
            word_pos = str(parse.tag.POS)
            word_gender = str(parse.tag.gender)
            word_number = str(parse.tag.number)
            word_tense = str(parse.tag.tense)
            word_case = str(parse.tag.case)

            lemma = str(parse.normal_form)
            form = (word_pos, word_gender, word_number, word_tense, word_case)

            forms_n_lemmas.append((form, lemma))

        return forms_n_lemmas

