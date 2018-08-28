from http import client
import json as json


class TestPoemClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _connection(self):
        return client.HTTPConnection(self.host, self.port)

    def ready(self):
        conn = self._connection()
        conn.request('GET', '/ready')

        r = conn.getresponse()
        if r.status != 200:
            return False

        data = r.read()
        return data == b'OK'

    def generate(self, poet, seed, random_seed=None):
        url = '/generate/{poet}'.format(poet=poet)
        obj = {'seed':seed}
        if random_seed:
            obj['random'] = random_seed
        body = json.dumps(obj)

        conn = self._connection()
        headers = {'Content-type': 'application/json'}
        conn.request('POST', url, body, headers)
        res = conn.getresponse()
        if res.status != 200:
            raise Exception("Error when generating poem: {}".format(res.reason))

        response = json.loads(res.read())
        return response
