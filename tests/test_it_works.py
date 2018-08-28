import pytest
import random as rnd

from constants import POETS, TEST_SEEDS
from tests.client import TestPoemClient

rnd.seed(42)


@pytest.mark.parametrize("poet", POETS)
def test_generate(local_client: TestPoemClient, poet):
    random_index = rnd.randint(0, len(TEST_SEEDS)-1)

    response = local_client.generate(poet, TEST_SEEDS[random_index])
    assert response['poem']
    assert len(response['poem']) > 10
