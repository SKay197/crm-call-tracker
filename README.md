# CRM Call Tracker

A simple Flask-based web application for tracking incoming calls. Entries are stored in a SQLite database and can be viewed, edited and exported from a browser. This project is ideal for small teams needing a lightweight CRM for phone interactions.

## Features

* Add, edit and delete call logs
* Filter and search by caller name or status
* Dashboard statistics for new, followed-up and closed calls
* Export call logs to CSV
* JSON API for programmatic access (`/api/calls`)

## Quick start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python app.py
   ```
   The database is created on first launch.

Set the `DATABASE_FILE` environment variable to override the database path. The server port can be set via `PORT`.

## Testing

Run the test suite with:

```bash
pytest -q
```

## Deployment
The included `Procfile` runs the app with `python app.py`, making it suitable for platforms such as Heroku. For production use consider running via Gunicorn and a reverse proxy.



