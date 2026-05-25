# postal-address

Python package for country-aware street/address autocomplete and validation using [AddressPerfect APIs on RapidAPI](https://rapidapi.com/search?term=AddressPerfect%20APIs&sortBy=ByAlphabetical).

## Features

- Single codebase for multiple countries
- Country selected via one constructor parameter
- API key from env var (`RAPIDAPI_KEY`) or constructor argument
- Wrapper methods for all main endpoints from the API spec

## Supported countries

- `de` German Streets API
- `sk` Slovak Streets API
- `nl` Dutch Streets API
- `fr` France Streets API
- `cz` Czech Streets API
- `ch` Swiss Streets API
- `be` Belgium Streets API
- `at` Austrian Streets API

## Installation (uv)

```bash
uv sync
```

For development dependencies:

```bash
uv sync --extra dev
```

## API key setup

Option 1: set environment variable

```bash
export RAPIDAPI_KEY="your_key_here"
```

Option 2: pass key directly to the client constructor.

## Usage

```python
from postal_address import PostalAddressClient

client = PostalAddressClient(country="de")

# Full-text autocomplete
results = client.autocomplete("Elisabeth")
print(results)

# Street-only autocomplete
streets = client.get_street_list("Elisab", zip_code="80797", city="München")
print(streets)
```

## Running tests

```bash
uv run pytest
```

## Examples

The `examples/` directory contains fully-working code samples for common use cases. All examples focus on **Swiss addresses** (country code `ch`) to demonstrate integration patterns.

### 1. Django Registration Form with Autocomplete

**Location:** `examples/django-registration-form/`

Real-time address autocomplete for a Django user registration form:
- Form with Swiss address fields
- AJAX endpoint for autocomplete suggestions
- Address validation on form submission

**Quick Start:**
```bash
cd examples/django-registration-form
pip install -r requirements.txt
# Configure RAPIDAPI_KEY, then integrate into your Django app
export RAPIDAPI_KEY="your_key_here"
python manage.py runserver
```

### 2. Batch Excel Processing

**Location:** `examples/batch-excel-processing/`

Validate customer addresses in bulk from an Excel file:
- Reads customer data from Excel (XLSX)
- Validates each address against the Swiss API
- Normalizes address components (street, postal code, city)
- Outputs results with color-coded validation status
- Detailed error reporting

**Quick Start:**
```bash
cd examples/batch-excel-processing
pip install -r requirements.txt
python create_sample_data.py
python batch_address_validator.py sample_customers.xlsx validated_customers.xlsx
```

### 3. FastAPI Address Validation Endpoint

**Location:** `examples/fastapi-validation/`

REST API for Swiss address validation and autocomplete:
- `POST /register` - Validate and register users with Swiss addresses
- `GET /autocomplete` - Get autocomplete suggestions
- `GET /users/{user_id}` - Retrieve stored user registrations
- Interactive Swagger documentation at `/docs`

**Quick Start:**
```bash
cd examples/fastapi-validation
pip install -r requirements.txt
python -m uvicorn main:app --reload
# Open http://localhost:8000/docs
```

## Package layout

- `postal_address/` package implementation
- `tests/` unit tests
- `examples/` documented code examples (Django, batch Excel, FastAPI)
- `pyproject.toml` build and dependency config
