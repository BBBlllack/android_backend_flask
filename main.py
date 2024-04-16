from flask import Flask, Response, request
import json
from views.WordView import Word
from views.OpenaiApi import OpenApi
from views.Database import db
from views.RecomView import Recommend

app = Flask(__name__)
app.register_blueprint(OpenApi)
app.register_blueprint(db)
app.register_blueprint(Word)
app.register_blueprint(Recommend)


@app.route("/")
@app.route("/index")
def index():
    text = "Hello, World!"
    response = Response(text, status=200, content_type='text/plain;charset=utf-8')
    return response


if __name__ == '__main__':
    host = "0.0.0.0"
    port = 80
    app.run(host, port, debug=True)
