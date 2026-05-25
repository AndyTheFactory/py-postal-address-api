# Batch Processing: Excel Customer Address Validation (Swiss)

This example shows how to batch-process customer addresses from an Excel file using Swiss address validation API.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your RapidAPI key:
```bash
export RAPIDAPI_KEY="your_rapidapi_key"
```

3. Prepare an Excel file with customer data in columns: Street, HouseNumber, PostalCode, City

## Usage

```bash
python batch_address_validator.py input.xlsx output.xlsx
```

## Features

- Reads customer data from Excel
- Validates each address against Swiss API
- Marks validation success/failure
- Normalizes address components (street, postal code, city)
- Exports results to new Excel file with status and normalized data
- Progress bar shows batch processing status
- Error handling with detailed logs

## Input File Format

Expected columns in Excel:
- Street (required)
- HouseNumber (optional)
- PostalCode (required)
- City (required)

## Output File Format

Original columns plus:
- ValidationStatus: "valid", "invalid", or "error"
- NormalizedStreet: Corrected street name
- NormalizedPostalCode: Corrected postal code
- NormalizedCity: Corrected city name
- ErrorMessage: Details if validation failed
