# FastAPI User Registration with Swiss Address Validation

This example shows how to build a FastAPI endpoint that validates Swiss user addresses during registration.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your RapidAPI key:
```bash
export RAPIDAPI_KEY="your_rapidapi_key"
```

3. Run the server:
```bash
python -m uvicorn main:app --reload
```

## API Endpoints

### POST /register
Register a new user with Swiss address validation.

Request:
```json
{
    "email": "user@example.com",
    "first_name": "Alice",
    "last_name": "Müller",
    "street": "Bahnhofstrasse",
    "house_number": "1",
    "postal_code": "8001",
    "city": "Zurich"
}
```

Response (200):
```json
{
    "user_id": "user_123",
    "email": "user@example.com",
    "first_name": "Alice",
    "last_name": "Müller",
    "street": "Bahnhofstrasse",
    "house_number": "1",
    "postal_code": "8001",
    "city": "Zurich",
    "address_validation": {
        "status": "valid",
        "normalized_street": "Bahnhofstrasse",
        "normalized_postal_code": "8001",
        "normalized_city": "Zurich"
    }
}
```

### GET /autocomplete
Get address suggestions for Swiss addresses.

Query param: `q=search_query`

Response:
```json
{
    "suggestions": [
        {
            "label": "Bahnhofstrasse, 8001 Zurich",
            "street": "Bahnhofstrasse",
            "postal_code": "8001",
            "city": "Zurich"
        }
    ]
}
```

## Testing

Use curl or the interactive Swagger UI at http://localhost:8000/docs

```bash
# Register user
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "first_name": "Alice",
    "last_name": "Müller",
    "street": "Bahnhofstrasse",
    "house_number": "1",
    "postal_code": "8001",
    "city": "Zurich"
  }'

# Get autocomplete suggestions
curl "http://localhost:8000/autocomplete?q=Bahnhof"
```

## Key Features

- Input validation with Pydantic models
- Swiss address validation against RapidAPI
- Automatic address normalization
- Error handling with descriptive messages
- Request/response logging
- Interactive API documentation (Swagger)
