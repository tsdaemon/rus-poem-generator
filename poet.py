import os
import copy
import pickle
from timeit import default_timer as timer

from word_forms import Phonetic, WordForms
from utils import PoemTemplateLoader, Word2vecProcessor

# Загальні набори даних присутні на тестувальному сервері
DATASETS_PATH = os.environ.get('DATASETS_PATH', '/data/')
# Наші набори даних присутні локально
LOCAL_DATA_PATH = './data'
timers = {}

# Гіперпараметри
MAX_PHONETIC_DISTANCE_TO_CHANGE = 1
MAX_COSINE_DISTANCE_TO_CHANGE = 0.7
POS_TO_REPLACE = ['NOUN', 'AVJ', 'ADJF', 'ADJM', 'VERB', 'ADVB']  # TODO: це можна розширити

def measure_time(func, name):
    start = timer()
    result = func()
    timers[name] = timer()-start
    return result


# Шаблоны стихов: строим их на основе собраний сочинений от организаторов
template_loader = measure_time(
    lambda: PoemTemplateLoader(os.path.join(DATASETS_PATH, 'classic_poems.json')),
    'Templates'
)

# Word2vec модель для оценки схожести слов и темы: берем из каталога RusVectores.org
word2vec = measure_time(
    lambda: Word2vecProcessor(os.path.join(DATASETS_PATH, 'web_upos_cbow_300_20_2017.bin.gz')),
    'Word2vec'
)


phonetic = measure_time(
    lambda: Phonetic(os.path.join(LOCAL_DATA_PATH, 'words_accent.json.bz2')),
    'Phonetic'
)

with open(os.path.join(LOCAL_DATA_PATH, 'words_forms.bin'), 'rb') as f:
    word_forms = measure_time(
        lambda: pickle.load(f),
        'Word forms'
    )

timers['Total'] = sum(v for k,v in timers.items())

print('Load finished, elapsed time: {}'.format(timers))


def _filter_words_by_phonetic_distance(replacement_candidates, word):
    candidate_phonetic_distances = [
        (replacement_word, phonetic.sound_distance(replacement_word, word))
        for replacement_word in replacement_candidates
    ]

    if not candidate_phonetic_distances:
        return []
    min_phonetic_distance = min(d for w, d in candidate_phonetic_distances)
    if min_phonetic_distance > MAX_PHONETIC_DISTANCE_TO_CHANGE:
        return []

    return [w for w, d in candidate_phonetic_distances if d == min_phonetic_distance]


def _get_word_by_vector(replacement_candidates, seed_vec):
    # из кандидатов берем максимально близкое теме слово
    # TODO: оце можна пришвидчити якщо перемножувати тензори одразу пачкою і на GPU
    word2vec_distances = [
        (replacement_word, word2vec.distance(seed_vec, word2vec.word_vector(replacement_word)))
        for replacement_word in replacement_candidates
    ]
    word2vec_distances.sort(key=lambda pair: pair[1])
    new_word, distance = word2vec_distances[0]
    if distance > MAX_COSINE_DISTANCE_TO_CHANGE:
        return None
    return new_word


def generate_poem(seed, poet_id):
    """
    Алгоритм генерации стихотворения на основе фонетических шаблонов
    """

    # выбираем шаблон на основе случайного стихотворения из корпуса
    template = template_loader.get_random_template(poet_id)
    poem = copy.deepcopy(template)

    # оцениваем word2vec-вектор темы
    seed_vec = word2vec.text_vector(seed)

    # не використовуємо слова більше ніж два рази
    used_words = []

    # заменяем слова в шаблоне на более релевантные теме
    for li, line in enumerate(poem):
        for ti, word in enumerate(line):
            if not word.isalpha():
                continue

            # Рахуємо форму слова — наголос, кількість голосних, частина мови
            # TODO: якщо використати тут інший (не словниковий) алгоритм визначення частини мови,
            # можна визначити частину мови однозначно.
            forms = word_forms.get_forms(word)
            if not forms:
                continue

            # Заміняємо тільки іменники, дієслова та прикметники
            if forms[0][2] not in POS_TO_REPLACE:
                continue

            # Обираємо можливі замінники. Знаходимо слова, які мають таку саму форму
            words_by_forms = [word_forms.word_by_form[f] for f in forms]
            replacement_candidates = [
                item
                for sublist in words_by_forms
                for item in sublist
                if item not in used_words
            ]
            if not replacement_candidates:
                continue

            # Якщо це останнє слово в рядку, фільтруємо кандидатів за фонетичною відстаню
            if ti == len(line)-1:
                replacement_candidates = _filter_words_by_phonetic_distance(
                    replacement_candidates,
                    word
                )
                if not replacement_candidates:
                    continue

            # Додаємо оригінальне слово, можливо воно вже непогано підходить
            replacement_candidates.append(word)

            # Фільтруємо повтори
            replacement_candidates = set(replacement_candidates)
            if len(replacement_candidates) < 2:
                continue

            new_word = _get_word_by_vector(replacement_candidates, seed_vec)
            if not new_word:
                continue

            poem[li][ti] = new_word
            used_words.append(new_word)

    assert template != poem, 'Should change something'

    # собираем получившееся стихотворение из слов
    generated_poem = '\n'.join([' '.join([token for token in line]) for line in poem])

    # оригінальний темплейт
    original_poem = '\n'.join([' '.join([token for token in line]) for line in template])

    return generated_poem, original_poem
