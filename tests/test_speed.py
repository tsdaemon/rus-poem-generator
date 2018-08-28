import random as rnd
from timeit import default_timer as timer
import pytest

import numpy as np

from constants import POETS, TEST_SEEDS
from tests.client import TestPoemClient

EXPERIMENTS = 100
rnd.seed(42)


@pytest.mark.parametrize("poet", POETS)
def test_generation_time(local_client: TestPoemClient, poet):
    req_times = []
    for _ in range(EXPERIMENTS):
        seed = TEST_SEEDS[rnd.randint(0, len(TEST_SEEDS)-1)]

        start = timer()
        response = local_client.generate(poet, seed)
        stop = timer()

        req_time = stop - start
        assert req_time < 5, "Generation is too long, poet {}, poem length {}".format(
            poet, len(response['poem'])
        )
        req_times.append(req_time)

    print('\nMean generation time: {}\nMedian generation time: {}\nSTD: {}\nQuantiles: {}'.format(
        np.mean(req_times),
        np.median(req_times),
        np.std(req_times),
        np.percentile(req_times, [25, 75])
    ))
