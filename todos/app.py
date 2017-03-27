from flask import Flask, g, jsonify, render_template

import config
import models
import requests

from resources.todos import todos_api

app = Flask(__name__)
app.register_blueprint(todos_api, url_prefix='/api/v1')


@app.route('/', methods=['GET', 'POST'])
def my_todos():
    # r = requests.get('http://127.0.0.1:8000/api/v1/todos')
    # todos = r.json()['todos']
    return render_template('index.html')

if __name__ == '__main__':
    models.initialize()
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
