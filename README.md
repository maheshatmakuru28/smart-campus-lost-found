# CampusFind — Smart Campus Lost & Found Management System

A responsive Flask website for a college/campus to report lost and found items, search reports, contact the reporter, and update item status.

## Features
- Responsive home page and item cards
- Report lost or found items
- Search by keyword, filter by type/category/status
- Item detail page and email contact button
- Open, Claimed, and Returned statuses
- SQLite for local development; PostgreSQL supported through `DATABASE_URL`
- Render deployment configuration included

## Run locally (Windows)
1. Install Python 3.11 or newer.
2. Open Command Prompt in this project folder.
3. Create and activate a virtual environment:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```
4. Install packages:
   ```bat
   pip install -r requirements.txt
   ```
5. Start the site:
   ```bat
   python app.py
   ```
6. Open `http://127.0.0.1:5000` in your browser.

## Push to GitHub
Create a new empty repository on GitHub, then run these commands from this folder:
```bash
git init
git add .
git commit -m "Build CampusFind lost and found website"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```
Replace the example repository address with your own repository URL.

## Deploy on Render
1. Push the project to GitHub.
2. In Render, create a **PostgreSQL** database and copy its **Internal Database URL** (use the external URL if the web service cannot access the internal network).
3. Create a **New Web Service** and connect your GitHub repository.
4. Render settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
5. Add environment variables:
   - `DATABASE_URL` = the PostgreSQL URL from your Render database
   - `SECRET_KEY` = a long random secret value
6. Deploy. If using the included `render.yaml`, it asks you to supply `DATABASE_URL` during setup.

## Important production notes
- Use PostgreSQL on Render for persistent data. The default local SQLite database is convenient for development, but files on a typical Render web service filesystem may be ephemeral.
- This starter intentionally has no login system. Anyone who can access a report detail page can see the reporter's contact email, and the status update form is public. Before real campus use, add student/staff authentication, authorization, CSRF protection, rate limiting, and privacy controls.
- This starter does not upload item photos. Photo uploads should use durable object storage and file validation.
