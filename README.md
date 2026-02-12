# FEM Trucking API

Backend REST API for managing **drivers** and **trucks** for FEM Trucking.

Built with FastAPI + SQLAlchemy + MySQL, with database migrations managed by Alembic.

---

## Tech Stack

- FastAPI (REST API + Swagger UI)
- SQLAlchemy ORM
- MySQL (via PyMySQL)
- Alembic (migrations)
- Pydantic (schemas/validation)
- Uvicorn (local dev server)

---

## Features

- CRUD endpoints for Drivers and Trucks
- Soft-delete pattern (deactivate via `is_active = false`)
- Validation:
  - Prevent assigning a truck to a non-existent driver
  - Enforce unique `unit_number`
  - Optional unique `vin` (when provided)
- Swagger docs available at `/docs`

---

## Project Structure

- `main.py` — FastAPI routes (drivers + trucks)
- `db.py` — SQLAlchemy engine + session dependency
- `models.py` — SQLAlchemy models
- `schemas.py` — Pydantic request/response models
- `alembic/` — migration scripts
- `alembic.ini` — Alembic config
- `requirements.txt` — dependencies

---

## Setup

### 1) Create MySQL database + user

Example:
- Database: `fem_trucking`
- User: `fem_app`

You can do this in MySQL Workbench.

---

### 2) Create virtual environment + install deps

From project root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt