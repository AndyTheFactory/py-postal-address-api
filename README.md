# postal-address

Python package for country-aware street/address autocomplete and validation using AddressPerfect APIs on RapidAPI.

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

## Package layout

- `postal_address/` package implementation
- `tests/` unit tests
- `pyproject.toml` build and dependency config
