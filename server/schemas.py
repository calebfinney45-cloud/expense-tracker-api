from marshmallow import Schema, fields, validate

from models import VALID_CATEGORIES


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(min=1))


class ExpenseSchema(Schema):
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)

    title = fields.String(
        required=True,
        validate=validate.Length(min=1, error="title must not be empty"),
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, error="amount must be greater than 0"),
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf(
            VALID_CATEGORIES,
            error=f"category must be one of: {', '.join(VALID_CATEGORIES)}",
        ),
    )
    date = fields.Date(required=True)


user_schema = UserSchema()
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)