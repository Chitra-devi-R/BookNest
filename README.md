# 📚 BookNest: Campus Library Reservation System

A web app where students browse, search and reserve library books.
Built as the final project for **23IT723 DevOps Laboratory**, combining Git, Jenkins, Docker, Pytest and Ansible.

## Pipeline

```
Git/GitHub → Jenkins → Docker build → Pytest → Ansible → Docker container (Flask + SQLite volume)
```

## Run locally

```bash
pip install -r requirements.txt
python app.py          # http://localhost:5000
python -m pytest test_app.py
```

## Endpoints

| Route | Purpose |
|-------|---------|
| `/` | Book catalogue, search, reserve |
| `/reservations` | All reservations (admin view) |
| `/api/books` | Books with live availability (JSON) |
| `/api/reserve` | POST: reserve a book |
| `/health` | Health check |

## Project files

`app.py`, `templates/`, `test_app.py`, `requirements.txt`, `Dockerfile`, `Jenkinsfile`, `ansible/deploy.yml`, `ansible/inventory.ini`, `.gitignore`
