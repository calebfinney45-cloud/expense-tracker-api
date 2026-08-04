from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    )

from models import db, User, Expense

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'change-this-in-a-real-app'

migrate = Migrate(app, db)
db.init_app(app)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)
api = Api(app)


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"errors": ["username and assword are required"]}, 400

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 400

        token = create_access_token(identity=str(user.id))
        return make_response(
            jsonify(token=token, user={"id": user.id, "username": user.username}),
            201
        )


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            token = create_access_token(identity=str(user.id))
            return make_response(
                jsonify(token=token, user={"id": user.id, "username":user.username}),
                200
            )

        return {"errors": ["Invalid username or password"]}, 401


class Me(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, int(user_id))
        return {"id": user.id, "username": user.username}, 200


api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Me, "/me")


if __name__ == '__main__':
    app.run(port=5555, debug=True)