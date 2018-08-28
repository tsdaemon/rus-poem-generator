import pytest
from timeit import default_timer as timer
import time

from tests.client import TestPoemClient


@pytest.fixture(scope='module')
def local_client():
    client = TestPoemClient('localhost', 8000)
    start = timer()
    while True:
        try:
            ready = client.ready()
            if ready:
                break
        except:
            pass
        stop = timer()
        assert stop - start <= 120, "Ready time expired"
        time.sleep(2)

    return client
