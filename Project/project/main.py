from flask import Flask, jsonify, request, Response
from json import dump, dumps
import db.dbcontext as dbcontext
from db.models import User
from project.external_models import UserData, UserToCreate
from hasher import HashPassword


def get_decorator(errors=(Exception, ), default_value=''):

    def decorator(func):

        def new_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                print("Got error! ", repr(e))
                return default_value

        return new_func

    return decorator

def create_app():
    app = Flask(__name__)

    Hasher256 = HashPassword()

    @app.route("/api/v1/hello-world-11", methods=['GET'])
    def hello():
        return '<h1 style="color:maroon;">Hello world 11</h1>'

    @app.route("/user/<int:user_id>", methods=['GET'])
    def get_user_by_id(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        if user:
            return jsonify(UserData(user, user.courses).toJSON()), 200
        return Response("User not found.", status=404)

    @app.route("/user", methods=['POST'])
    def create_user():
        user_data = UserToCreate().load(request.json)
        if user_data:
            user_data['password'] = Hasher256.Hash(user_data['password'])
            user = dbcontext.create_entry(User, **user_data)
            return jsonify(UserData(user).toJSON()), 200
        return Response("Invalid data provided.", status=400)

    @app.route("/user", methods=['GET'])
    def login():
        email = request.args.get('email')
        password = Hasher256.Hash(request.args.get('password'))
        user = dbcontext.get_user_by_email(email)
        if user:
            if password == user.password:
                return Response("JWT Token", status=200)
            return Response("Invalid auth credentials.", status=400)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['PUT'])
    def update_user(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        if user:
            user_data = UserToCreate().load(request.json)
            if user_data:
                updated_user = dbcontext.update_user(user_data, user_id)
                return jsonify(UserData(updated_user, updated_user.courses).toJSON()), 200
            return Response("Invalid data provided.", status=400)
        return Response("User not found.", status=404)

    @app.route("/user/<int:user_id>", methods=['DELETE'])
    def delete_user(user_id):
        user = dbcontext.get_entry_by_uid(User, user_id)
        if user:
            if dbcontext.delete_entry_by_uid(User, user_id):
                return Response("User has been successfully deleted.", status=200)
            return Response("Unexpected error occurred.", status=500)
        return Response("User not found.", status=404)















    return app
