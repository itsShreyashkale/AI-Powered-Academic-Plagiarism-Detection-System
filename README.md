# AI-Powered Academic Plagiarism Detection System

An end-to-end **Django + DRF** project with role-based workflows (**student**, **professor**), file uploads, and plagiarism detection using **TF-IDF** and optional **Sentence-BERT**.  

This project contains a backend (Django REST API), frontend (HTML/CSS/JS pages), database models, and AI-powered utilities for plagiarism detection.

---

## 🚀 Features

- 🔐 **User Authentication** with JWT (register, login, logout).
- 🧑‍🏫 **Professor role**: create assignments (title, description, deadline, file).
- 🎓 **Student role**: view assignments, upload submissions, track plagiarism reports.
- 📑 **Plagiarism detection**:
  - TF-IDF + cosine similarity (lightweight baseline).
  - Optional semantic similarity (Sentence-BERT) for deeper checks.
- 🖥️ **Frontend**:
  - `/login/`, `/register/`
  - `/student/` → assignments + submissions
  - `/professor/` → assignments + submissions
- 📜 **API Docs** via Swagger (`/swagger/`) and ReDoc (`/redoc/`).
- 🧪 **Tests** with `pytest` + Django test integration.

---

## 📂 Folder Structure

```text
AI-Powered Academic Plagiarism Detection System/
├─ documents/          # Assignments, submissions, serializers, tests
├─ plagiarism/         # Plagiarism engine, utils, plagiarism API
├─ users/              # User model, JWT auth, permissions
├─ plagiarism_project/ # Django project (settings, urls, wsgi/asgi)
├─ templates/          # HTML frontend pages
├─ media/              # Uploaded files (assignments & submissions)
├─ static/             # Static resources
├─ env/                # Virtual environment (ignored in git)
├─ manage.py
├─ pytest.ini
├─ README.md
├─ README_DEV.md
├─ requirements.txt
└─ .gitignore
```

---

## ⚡ Quickstart

### 1. Clone repo

```bash
git clone https://github.com/itsShreyashkale/AI-Powered-Academic-Plagiarism-Detection-System.git
cd AI-Plagiarism-Detection
```

### 2. Setup environment

```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux / macOS
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations & create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/login/`

### 6. Run tests

```bash
pytest -q
```

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Auth**: JWT (SimpleJWT)
- **Database**: SQLite (default, can switch to Postgres/MySQL)
- **Plagiarism Engine**: scikit-learn (TF-IDF), NLTK, optional Sentence-BERT
- **Frontend**: HTML + CSS + Vanilla JS
- **Testing**: pytest, pytest-django
- **Docs**: drf-yasg (Swagger/ReDoc)

---

## 📌 Future Improvements

- 🎨 UI polish with Tailwind or React frontend.
- 🤖 Additional AI models (GPT-style rephrasing detection, semantic graph matching).
- ⚡ Optimizations for large datasets and faster similarity search.
- 🔐 Production security: refresh token blacklisting, rate-limiting, Docker deployment.

---
