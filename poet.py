import copy
from timeit import default_timer as timer
from collections import defaultdict

from word.phonetic import Phonetic
from tools.picklers import PosUnpickler
from word.vectors import Word2VecTorch
from word.templates import PoemTemplateLoader, untokenize_template

from constants import *

# Загальні набори даних присутні на тестувальному сервері
DATASETS_PATH = os.environ.get('DATASETS_PATH', '/data/')
# Наші набори даних присутні локально
LOCAL_DATA_PATH = './data'
timers = defaultdict(float)

# Гіперпараметри
MAX_PHONETIC_DISTANCE_TO_CHANGE = 1
MAX_COSINE_DISTANCE_TO_CHANGE = 0.7
POS_TO_REPLACE = [
    'NOUN',
    'AVJ',
    'ADJF',
    'ADJM',
    # 'VERB', дієслова дуже погано заміняються
    'ADVB'
]  # TODO: це можна розширити


def measure_time(func, name, local_timers=None):
    global timers
    if local_timers is not None:
        timers = local_timers

    start = timer()
    result = func()
    timers[name] += timer() - start
    return result


# Шаблоны стихов: строим их на основе собраний сочинений от организаторов
template_loader = measure_time(
    lambda: PoemTemplateLoader(os.path.join(DATASETS_PATH, 'classic_poems.json')),
    'Templates'
)

# Word2vec модель для оценки схожести слов и темы: берем из каталога RusVectores.org
word2vec = measure_time(
    lambda: Word2VecTorch(os.path.join(LOCAL_DATA_PATH, 'web_upos_cbow_300_20_2017.bin')),
    'Word2vec'
)

phonetic = Phonetic()

with open(os.path.join(LOCAL_DATA_PATH, 'words_forms.bin'), 'rb') as f:
    word_forms = measure_time(
        lambda: PosUnpickler(f).load(),
        'Word forms'
    )

timers['Total'] = sum(v for k, v in timers.items())

print('Load finished, elapsed time: {}'.format(timers))


def _filter_words_by_phonetic_distance(replacement_candidates, word):
    candidate_phonetic_distances = [
        (replacement_word, phonetic.sound_distance(replacement_word.word, word.word))
        for replacement_word in replacement_candidates
    ]

    if not candidate_phonetic_distances:
        return []
    min_phonetic_distance = min(d for w, d in candidate_phonetic_distances)
    if min_phonetic_distance > MAX_PHONETIC_DISTANCE_TO_CHANGE:
        return []

    return [w for w, d in candidate_phonetic_distances if d == min_phonetic_distance]


def _get_word_by_vector(replacement_candidates, seed_vec):
    distances = word2vec.distance(replacement_candidates, seed_vec)

    # из кандидатов берем максимально близкое теме слово
    cand_distances = list(zip(replacement_candidates, distances))
    cand_distances.sort(key=lambda pair: pair[1])

    new_word, distance = cand_distances[0]
    if distance > MAX_COSINE_DISTANCE_TO_CHANGE:
        return None

    return new_word


def _get_repacement_candidates(word, used_words):
    # Обираємо можливі замінники. Знаходимо слова, які мають таку саму форму
    words_by_form = word_forms.word_by_form[(word.phonetic_form, word.morph_form)]
    return [w for w in words_by_form
            if w.lemma not in used_words and w.word not in DO_NOT_WANT_TO_REPLACE]


def last_word_in_row(ti, words):
    if ti == len(words) - 1:
        return True
    # all next words are puctuation
    words = words[ti+1:]
    return all(w.word.strip() in PUNCTUATION for w in words)


def generate_poem(seed, poet_id, random):
    """
    Алгоритм генерации стихотворения на основе фонетических шаблонов
    """

    # выбираем шаблон на основе случайного стихотворения из корпуса
    template = template_loader.get_random_template(poet_id, random)
    poem = copy.deepcopy(template)

    # Вимірюємо час
    local_timers = defaultdict(float)

    # оцениваем word2vec-вектор темы
    seed_tokens = word_forms.parse_text(seed, phonetic=False)
    seed_vec = measure_time(lambda: word2vec.text_vector(seed_tokens), 'Text vector', local_timers)

    # TODO: ще можна слова з сіда якось пробувати використовувати. Може додавати їх з більшими
    # вагами?

    # не використовуємо слова більше ніж два рази
    used_words = []

    for li, line in enumerate(poem):
        # Рахуємо форму слів — наголос, кількість голосних, частина мови etc
        words = list(word_forms.parse_text(' '.join(line)))
        assert len(words) == len(line)
        for ti, word in enumerate(words):
            # Заміняємо тільки іменники, дієслова та прикметники,
            # пропускаємо пунктуацію,
            # не заміняємо деякі фіксовані слова
            if word.word.strip() in PUNCTUATION or \
                    word.morph_form.pos not in POS_TO_REPLACE or \
                    word.word in DO_NOT_WANT_TO_REPLACE:
                continue

            replacement_candidates = _get_repacement_candidates(word, used_words)

            # Якщо це останнє слово в рядку, фільтруємо кандидатів за фонетичною відстаню
            if last_word_in_row(ti, words):
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

            new_word = measure_time(
                lambda: _get_word_by_vector(replacement_candidates, seed_vec),
                'Word similarities',
                local_timers
            )
            if not new_word:
                continue

            poem[li][ti] = new_word.word
            used_words.append(new_word.lemma)

    generated_poem = untokenize_template(poem)
    original_poem = untokenize_template(template)

    return generated_poem, original_poem, local_timers


def get_poem(seed, poet_id, random):
    generated_poem, original_poem, timers = '', '', None
    while generated_poem == original_poem:
        generated_poem, original_poem, timers = generate_poem(seed, poet_id, random)
    return generated_poem, original_poem, timers