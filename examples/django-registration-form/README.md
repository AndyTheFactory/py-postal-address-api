# Django Registration Form with Swiss Address Autocomplete

This is a standalone Django app example. You can run it directly from this folder.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure your API key:

```bash
export RAPIDAPI_KEY="your_rapidapi_key"
```

3. Run database migrations:

```bash
python manage.py migrate
```

4. Start the server:

```bash
python manage.py runserver
```

5. Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/register/`

## Project Structure

- `manage.py` - Django entrypoint
- `standalone_project/` - Django project settings and root URLs
- `registration_app/` - App code (models, forms, views, urls, templates)

## Behavior

1. User types a Swiss address prefix (for example `Bahnhofstrasse`).
2. Frontend calls `GET /api/ch-address/autocomplete/?q=...`.
3. Suggestions populate a dropdown.
4. Selecting a suggestion fills postal code and city.
5. On submit, the backend validates and stores the registration.
