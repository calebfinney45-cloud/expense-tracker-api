# Expense Tracker API

## Description

A secure backend REST API for a personal expense tracking app. Users can
sign up, log in, and manage their own **Expenses** — no user can view,
edit, or delete another user's data. Authentication is handled with
**JWT** (JSON Web Tokens), so the API is fully stateless.

Built with **Flask**, **Flask-RESTful**, **Flask-SQLAlchemy**,
**Flask-Migrate**, **Flask-Bcrypt**, **Flask-JWT-Extended**, and
**Marshmallow**.

### Models

- `User` — `id`, `username` (unique), `_password_hash` (bcrypt-hashed,
  never exposed via the API)
- `Expense` — `id`, `title`, `amount`, `category`, `date`, `user_id`
  (foreign key → `users.id`)

A `User` has many `Expense`s; each `Expense` belongs to exactly one
`User`.

### Validation

- **Table constraints**: unique usernames, positive expense amounts, a
  check constraint restricting `category` to a fixed set of values.
- **Model validations** (`@validates`): non-empty username, non-empty
  expense title, positive amount, valid category.
- **Schema validations** (Marshmallow): required fields, `Length`,
  `Range`, `OneOf` validators mirroring the constraints above.

### Authentication

This API uses **JWT**, not session cookies. A successful `/signup` or
`/login` returns a token, which the frontend stores (typically in
`localStorage`) and sends back on every subsequent request as:

```
Authorization: Bearer <token>
```

There is no `/logout` endpoint — JWT is stateless, so logging out is
simply the frontend discarding its stored token. Tokens expire after 15
minutes by default (`flask-jwt-extended`'s default), after which the user
needs to log in again to get a fresh one.

## Installation

1. Clone the repo and move into it:
   ```bash
   git clone <your-repo-url>
   cd expense-tracker-api
   ```
2. Install dependencies with Pipenv:
   ```bash
   pipenv install
   pipenv shell
   ```
3. Move into the `server/` directory:
   ```bash
   cd server
   ```
4. Set the Flask app environment variable:
   ```bash
   export FLASK_APP=app.py      # Windows (cmd): set FLASK_APP=app.py
   ```
5. Create the database tables via migrations:
   ```bash
   flask db upgrade head
   ```
6. Seed the database with example users and expenses:
   ```bash
   python seed.py
   ```

## Running the App

From inside the `server/` directory:

```bash
python app.py
```

The API will be available at `http://127.0.0.1:5555`.

### Test accounts (from the seed script)

| Username | Password |
|---|---|
| `alice` | `password123` |
| `bob` | `password123` |

Each starts with 5 randomly generated expenses.

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/signup` | public | Create a new user. Body: `{"username": "...", "password": "..."}`. Returns `{"token": ..., "user": {...}}` |
| `POST` | `/login` | public | Log in an existing user. Same body/response shape as signup |
| `GET` | `/me` | protected | Return the currently authenticated user |
| `GET` | `/expenses` | protected | Paginated list of the current user's expenses. Query params: `page` (default 1), `per_page` (default 5) |
| `POST` | `/expenses` | protected | Create an expense for the current user. Body: `{"title": "...", "amount": <float>, "category": "...", "date": "YYYY-MM-DD"}` |
| `PATCH` | `/expenses/<id>` | protected | Update one of the current user's expenses. Any subset of the POST body fields. `403` if the expense belongs to another user |
| `DELETE` | `/expenses/<id>` | protected | Delete one of the current user's expenses. `403` if it belongs to another user |

Valid expense categories: `food`, `transport`, `housing`, `utilities`,
`entertainment`, `other`.

All protected routes require the `Authorization: Bearer <token>` header
and return `401` if it's missing or invalid. Validation errors return
`400` with an `errors` field. Attempting to access another user's
expense returns `403`.

## Project Structure

```
expense-tracker-api/
├── Pipfile
├── README.md
├── .gitignore
└── server/
    ├── app.py          # Flask app, JWT setup, auth + expense routes
    ├── models.py       # SQLAlchemy models, relationships, constraints, validations
    ├── schemas.py      # Marshmallow schemas + schema validations
    ├── seed.py         # Seed script
    └── migrations/     # Flask-Migrate migration history
```

## Security Note

`JWT_SECRET_KEY` in `app.py` is a plaintext placeholder for local
development and grading purposes only. In a real deployment, this should
be loaded from an environment variable and never committed to source
control.