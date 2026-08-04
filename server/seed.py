#!/usr/bin/env python3
from datetime import date

from faker import Faker

from app import app
from models import db, User, Expense

fake = Faker()

with app.app_context():
    print("Clearing existing data...")
    Expense.query.delete()
    User.query.delete()
    db.session.commit()

    print("Seeding users...")
    alice = User(username="alice")
    alice.password_hash = "password123"

    bob = User(username="bob")
    bob.password_hash = "password123"

    db.session.add_all([alice, bob])
    db.session.commit()

    print("Seeding expenses...")
    categories = ["food", "transport", "housing", "utilities", "entertainment", "other"]

    expenses = []
    for user in [alice, bob]:
        for _ in range(5):
            expenses.append(
                Expense(
                    title=fake.bs().capitalize(),
                    amount=round(fake.pyfloat(min_value=5, max_value=500, positive=True), 2),
                    category=fake.random_element(categories),
                    date=fake.date_between(start_date="-60d", end_date="today"),
                    user=user,
                )
            )

    db.session.add_all(expenses)
    db.session.commit()

    print(f"Seeding complete! Created {User.query.count()} users and {Expense.query.count()} expenses.")