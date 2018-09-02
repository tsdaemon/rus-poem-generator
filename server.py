import sys
from collections import defaultdict
from timeit import default_timer as timer

from flask import Flask, request, jsonify, abort, render_template, send_from_directory

import poet

app = Flask(__name__, static_url_path='')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:path>')
def send_css(path):
    return send_from_directory('static', path)


@app.route('/ready')
def ready():
    return 'OK'


@app.route('/generate/<poet_id>', methods=['POST'])
def generate(poet_id):
    request_data = request.get_json()
    seed = request_data['seed']
    random = request_data.get('random', None)
    try:
        # fake it till you make it
        start = timer()
        generated_poem, original_poem, timers = poet.get_poem(seed, poet_id, random)
        t = timer()-start
        sys.stderr.write('Generation time: ' + str(t) + ' ')
        timers = [(k, v) for k, v in timers.items()]
        # print(timers)
        return jsonify({
            'poem': generated_poem,
            'originalPoem': original_poem,
            'timers': timers
        })
    except KeyError:
        abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
