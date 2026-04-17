# Job Application Tracker

> Track your job search with a full-stack Python application built from scratch.

**Live Demo:** [your-app.streamlit.app](https://your-app.streamlit.app)  
**API Docs:** [your-api.onrender.com/docs](https://your-api.onrender.com/docs)

---

## What It Does

A complete job application management system that lets you:

- Log every application with company, role, status, salary, and notes
- Track status through the pipeline: Applied → Interview → Offer / Rejected
- Filter and search your applications
- View summary statistics at a glance
- Secure multi-user accounts — each user only sees their own data

---

## Tech Stack

| Layer      | Technology                       |
|------------|----------------------------------|   
| Frontend   | Streamlit 1.35                   |
| Backend    | FastAPI 0.111 + Python 3.11      |
| Database   | PostgreSQL (Render) / SQLite     |
| ORM        | SQLAlchemy 2.0                   |
| Validation | Pydantic 2.7                     |
| Auth       | JWT (python-jose) + argon2-cffi  |

---

## Architecture

Browser → Streamlit (Streamlit Cloud)
↕ HTTP + JWT
FastAPI (Render)
↕ SQLAlchemy ORM
PostgreSQL (Render)

---

## Running Locally

### Prerequisites
- Python 3.11+
- Git

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/job-application-tracker.git
cd job-application-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your own SECRET_KEY

# Start the API
uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs (interactive API docs)

# In a second terminal, install and start Streamlit
pip install -r requirements-streamlit.txt
streamlit run streamlit_app/app.py
# → http://localhost:8501
```

---

---

## API Endpoints

| Method | Endpoint           | Description            | Auth |
|--------|--------------------|------------------------|------|
| POST   | /auth/register     | Create account         | No   |
| POST   | /auth/login        | Get JWT token          | No   |
| GET    | /applications      | List your applications | Yes  |
| POST   | /applications      | Add an application     | Yes  |
| PATCH  | /applications/{id} | Update status/fields   | Yes  |
| DELETE | /applications/{id} | Remove application     | Yes  |
| GET    | /stats             | Summary counts         | Yes  |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## What I Learned Building This

This project was built as a structured 8-week learning journey covering:

- **Python OOP** — dataclasses, the manager pattern, custom exceptions, modules
- **Type hints & pytest** — type-safe code with automated tests
- **FastAPI** — REST API design, dependency injection, Pydantic validation
- **SQLAlchemy** — ORM, sessions, migrations
- **JWT Authentication** — bcrypt hashing, token creation/verification, ownership checks
- **Streamlit** — session state, the rerun model, calling APIs from a Python UI

---

## Licence

MIT