from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy()
bcrypt = Bcrypt()

VALID_CATEGORIES = ["food", "transport", "housing", "utilities", "entertainment", "other"]


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False)

    expenses = db.relationship(
        "Expense", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def password_hash(self):
        raise AttributeError("password_hash is not a readable attribute")

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = password_hash.decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("USername must not be empty.")
        return value.strip()


class Expense(db.Model):
    __tablename__ = "expenses"

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_expense_amount_positive"),
        CheckConstraint(
            f"category IN ({', '.join(repr(c) for c in VALID_CATEGORIES)})",
            name="ck_expense_category_valid",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    amount = db.Column(db.Float, nullable=False)                    
    category = db.Column(db.String, nullable=False)                 
    date = db.Column(db.Date, nullable=False)                       
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="expenses")

    @validates("title")                                              
    def validate_title(self, key, value):                            
        if not value or not value.strip():                           
            raise ValueError("Expense title must not be empty.")  
        return value.strip()                                         

    @validates("amount")                                             
    def validate_amount(self, key, value):                           
        if value is None or value <= 0:                              
            raise ValueError("Expense amount must be a positive number.")  
        return value                                               

    @validates("category")                                           
    def validate_category(self, key, value):                         
        if value not in VALID_CATEGORIES:                            
            raise ValueError(f"category must be one of: {', '.join(VALID_CATEGORIES)}")  
        return value
