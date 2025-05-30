---

# Mini Blogging API

A minimal but production-ready blogging platform built with Flask. Users can register, log in, write blog posts, and comment on others' posts. Authentication is handled using JWT tokens.

---

## Features

- User registration and login with JWT
- Secure password hashing with `bcrypt`
- CRUD APIs for Posts and Comments
- Users can only edit/delete their own content
- Pagination for blog posts and comments
- Full unit testing with `pytest`
- Configurable via `.env`
- SQLite by default (easy to replace with PostgreSQL/MySQL)

---

## Tech Stack

- **Flask** & Flask Extensions (`Flask-JWT-Extended`, `Flask-SQLAlchemy`, `Flask-Migrate`, `Flask-Marshmallow`)
- **SQLite** for development (can switch via `DATABASE_URL`)
- **JWT** for stateless authentication
- **pytest** for testing
- **PowerShell** script for local automation
- **Python Version** 3.11

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/mini-blogging-api.git
cd mini-blogging-api
```

### 2. Create `.env` file

```env
# .env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///blog.db
```

### 3. Install dependencies (in virtual env)

```bash
py -3.11 -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
```

### 4. Run migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 5. Run the API

```bash
flask run
```

> Or use the provided PowerShell script (RECOMMENDED):

```bash
.\run.ps1
```

---

## API Endpoints

### Auth

| Method | Endpoint             | Description              |
| ------ | -------------------- | ------------------------ |
| POST   | `/api/auth/register` | Register a new user      |
| POST   | `/api/auth/login`    | Log in and get tokens    |
| POST   | `/api/auth/refresh`  | Refresh access token     |
| GET    | `/api/auth/me`       | Get current user profile |

---

### Posts

| Method | Endpoint                  | Description                |
| ------ | ------------------------- | -------------------------- |
| GET    | `/api/posts`              | List all published posts   |
| GET    | `/api/posts/<id>`         | View a single post         |
| POST   | `/api/posts`              | Create a new post _(auth)_ |
| PUT    | `/api/posts/<id>`         | Update your post _(auth)_  |
| DELETE | `/api/posts/<id>`         | Delete your post _(auth)_  |

---

### Comments

| Method | Endpoint                  | Description             |
| ------ | ------------------------- | ----------------------- |
| GET    | `/api/comments/post/<id>` | Get comments for a post |
| GET    | `/api/comments/<id>`      | Get single comment      |
| POST   | `/api/comments`           | Add a comment _(auth)_  |
| PUT    | `/api/comments/<id>`      | Update comment _(auth)_ |
| DELETE | `/api/comments/<id>`      | Delete comment _(auth)_ |

---

## Running Tests

```bash
pytest
```

All test files are located under the `tests/` directory.

---

## Folder Structure

```
mini-blogging-api/
├── app/
│   ├── api/           # Post & comment routes
│   ├── auth/          # Authentication routes
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Marshmallow schemas
│   ├── utils/         # Reusable decorators & helpers
│   ├── templates/     # For future UI
├── tests/             # Unit test files
├── .env.example       # Sample env config
├── config.py          # App configs for dev/test/prod
├── run.py             # Entrypoint
├── run.ps1            # PowerShell script to run app
```
