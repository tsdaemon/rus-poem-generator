import os

from word.forms import WordForms, get_csv_reader
from word.accent import AccentRussianNlp
from word.phonetic import Phonetic
from word.morph import PosAnalyzerMorphy
from tools.picklers import PosPickler
from constants import *

if __name__ == '__main__':
    """
    This script is intented to serialize WordForms instance because loading it from scratch tooks
    too much time.
    
    """

    # Change this to load other corpora
    # Словарь слов-кандидатов по фонетическим формам: строится из набора данных SDSJ 2017
    # TODO: SDSJ 2017 – це просто корпус, ми можемо взяти будь який інший, який нам краще підійде
    # Наприклад, корпус вікіпедії
    filename = os.path.join(DATASETS_PATH, 'sdsj2017_sberquad.csv')
    column = 'paragraph'
    reader = get_csv_reader(filename, column)

    # Phonetic analyzer
    phonetic = Phonetic()

    # Accents dictionary
    accent = AccentRussianNlp(os.path.join(LOCAL_DATA_PATH, 'stress.txt'))

    # Morhology analyzer
    pos = PosAnalyzerMorphy()

    # Instance
    word_forms = WordForms(phonetic, accent, pos, reader)
    filename = os.path.join(LOCAL_DATA_PATH, 'words_forms.bin')
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, 'wb') as f:
        pickler = PosPickler(f)
        pickler.dump(word_forms)
