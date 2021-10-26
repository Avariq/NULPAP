from flask import Flask

def create_app():
    app = Flask(__name__)

    @app.route("/api/v1/hello-world-11", methods=['GET'])
    def hello():
        return '<h1 style="color:maroon;">Hello world 11</h1>'

    return app
