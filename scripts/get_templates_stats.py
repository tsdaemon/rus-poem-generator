import os

import numpy as np

from word.templates import PoemTemplateLoader

DATASETS_PATH = os.environ.get('DATASETS_PATH')

if __name__ == '__main__':
    path = os.path.join(DATASETS_PATH, 'classic_poems.json')
    loader = PoemTemplateLoader(path, debug_folder='./debug')

    for poet, poems in loader.original_poems.items():
        length = [len(t) for t in poems]
        lines = [len(t.split('\n')) for t in poems]
        templates = len(loader.poet_templates[poet])

        max_poem = poems[np.argmax(length)]

        print("""
{}
Number of poems: {}
Number of templates: {}
Length: {}
Lines: {} 
        """.format(
            poet,
            len(poems),
            templates,
            np.percentile(length, [0, 25, 50, 75, 100]),
            np.percentile(lines, [0, 25, 50, 75, 100]),
            # max_poem
        ))

