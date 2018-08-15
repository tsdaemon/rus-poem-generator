import os
import pickle

from word_forms import Phonetic, WordForms, get_csv_reader


if __name__ == '__main__':
    """
    This script is intented to serialize WordForms instance because loading it from scratch tooks
    too much time.
    
    
    """

    DATASETS_PATH = os.environ.get('DATASETS_PATH')
    LOCAL_DATA_PATH = './data'

    # Change this to load other corpora
    # Словарь слов-кандидатов по фонетическим формам: строится из набора данных SDSJ 2017
    # TODO: SDSJ 2017 – це просто корпус, ми можемо взяти будь який інший, який нам краще підійде
    # Наприклад, корпус вікіпедії
    filename = os.path.join(DATASETS_PATH, 'sdsj2017_sberquad.csv')
    column = 'paragraph'
    reader = get_csv_reader(filename, column)

    # Dictionary of stresses
    phonetic = Phonetic(os.path.join(LOCAL_DATA_PATH, 'words_accent.json.bz2'))

    # Instance
    word_forms = WordForms(phonetic, reader)
    filename = os.path.join(LOCAL_DATA_PATH, 'words_forms.bin')
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, 'wb') as f:
        pickle.dump(word_forms, f)
