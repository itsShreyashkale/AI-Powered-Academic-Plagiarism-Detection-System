# Developer Guide – AI-Powered Academic Plagiarism Detection

This document explains setup, folder purpose, and how to extend the project.

---

## ⚙️ Environment Setup

```bash
python -m venv env
source env/bin/activate   # or env\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 📂 Apps Overview

- **users/**  
  - Custom User model (with `role`: student/professor).  
  - JWT Authentication endpoints.  
  - Permissions: `IsStudent`, `IsProfessor`, `IsAdmin`.

- **documents/**  
  - Models: `Assignment`, `Submission`, `AssignmentReview`.  
  - Endpoints: create/list assignments, submit files, professor views.  
  - HTML pages: student.html, professor.html.  

- **plagiarism/**  
  - `utils.py`: text extraction, preprocessing, TF-IDF, BERT similarity.  
  - Endpoints: plagiarism check (`/api/plagiarism/check/<submission_id>/`).  

- **plagiarism_project/**  
  - Django settings (configured for REST + JWT + Swagger).  
  - Root `urls.py` connects all apps.  

- **templates/**  
  - Frontend HTML pages (`login.html`, `register.html`, `student.html`, `professor.html`).  

- **media/**  
  - Uploaded assignment & submission files.  

- **static/**  
  - For future CSS/JS/images.  

---

## 🧪 Testing

We use `pytest` + `pytest-django`.

Run:

```bash
pytest -v
pytest --cov=. --cov-report=term-missing
```

Tests include:

- User registration + login
- Assignment creation
- Submission upload
- Plagiarism check API

---

## 🛠️ How to Extend

- Add new AI methods in `plagiarism/utils.py`.  
- Improve frontend UI (replace plain HTML with React/Vue if desired).  
- Replace SQLite with PostgreSQL for production.  
- Add Celery tasks for async plagiarism checking.  

---

## 🧑‍💻 VS Code Tips

- Install extensions: Python, Django, Pylance.  
- Use `.env` file for secrets:

  ```text
  DJANGO_SECRET_KEY=your_secret
  DEBUG=True
  ```
  
- Debug via `launch.json` in VS Code.  

---

## 🔮 Future Updates (planned in `FUTURE_UPDATES.md`)

- UI polish with Tailwind.
- Extra AI methods: BERT + LLMs.
- Optimization: caching, async plagiarism checks.
