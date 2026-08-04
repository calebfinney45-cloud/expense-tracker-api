from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
    verify_jwt_in_request,
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


@app.before_request
def check_if_logged_in():
    open_access_list = ["signup", "login"]

    if request.endpoint not in open_access_list and not verify_jwt_in_request():
        return {"error": "401 Unauthorized"}, 401


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"errors": ["username and password are required"]}, 400

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


class Expenses(Resource):                                            
    @jwt_required()                                                  
    def get(self):                                                   
        user_id = get_jwt_identity()                                 
        expenses = Expense.query.filter_by(user_id=int(user_id)).all()  
        return [                                                      
            {                                                          
                "id": e.id,                                            
                "title": e.title,                                      
                "amount": e.amount,                                     
                "category": e.category,                                
                "date": str(e.date),                                   
            }                                                          
            for e in expenses                                          
        ], 200                                                         

    @jwt_required()                                                   
    def post(self):                                                   
        user_id = get_jwt_identity()                                  
        data = request.get_json() or {}                                

        try:                                                           
            expense = Expense(                                        
                title=data.get("title"),                               
                amount=data.get("amount"),                              
                category=data.get("category"),                          
                date=data.get("date"),                                  
                user_id=int(user_id),                                   
            )                                                           
            db.session.add(expense)                                     
            db.session.commit()                                         
        except Exception as err:                                        
            db.session.rollback()                                       
            return {"errors": [str(err)]}, 400                          

        return {"id": expense.id, "title": expense.title}, 201          


class ExpenseByID(Resource):
    @jwt_required()
    def patch(self, id):
        user_id = get_jwt_identity()
        expense = db.session.get(Expense, id)

        if not expense:
            return {"error": "Expense not found"}, 404
        if expense.user_id != int(user_id):
            return {"error": "Forbidden"}, 403

        data = request.get_json() or {}
        try:
            if "title" in data:
                expense.title = data["title"]
            if "amount" in data:
                expense.amount = data["amount"]
            if "category" in data:
                expense.category = data["category"]
            if "date" in data:
                expense.date = data["date"]
            db.session.commit()
        except Exception as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 400

        return {"id": expense.id, "title": expense.title}, 200

    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        expense = db.session.get(Expense, id)

        if not expense:
            return {"error": "Expense not found"}, 404
        if expense.user_id != int(user_id):
            return {"error": "Forbidden"}, 403

        db.session.delete(expense)
        db.session.commit()
        return {}, 204

    
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(Me, "/me")
api.add_resource(Expenses, "/expenses")
api.add_resource(ExpenseByID, "/expenses/<int:id>")


if __name__ == '__main__':
    app.run(port=5555, debug=True)