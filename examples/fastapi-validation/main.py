"""FastAPI server with Swiss address validation for user registration."""

import os
import sys
import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

# Add parent directory to path for local imports
sys.path.insert(0, str(sys.path[0]) + "/../..")

from postal_address import PostalAddressClient, PostalAddressError

app = FastAPI(
    title="Swiss Address API",
    description="User registration with Swiss address validation",
    version="1.0.0",
)

# Store users in memory (replace with database in production)
users_db: dict[str, dict[str, Any]] = {}


class AddressData(BaseModel):
    """Data model for Swiss address fields."""

    street: str
    house_number: str | None = None
    postal_code: str
    city: str


class UserRegistrationRequest(BaseModel):
    """Data model for user registration request."""

    email: EmailStr
    first_name: str
    last_name: str
    street: str
    house_number: str | None = None
    postal_code: str
    city: str


class AddressValidationResult(BaseModel):
    """Data model for Swiss address validation result."""

    status: str  # "valid", "invalid", or "error"
    normalized_street: str | None = None
    normalized_postal_code: str | None = None
    normalized_city: str | None = None
    message: str | None = None


class UserResponse(BaseModel):
    """Data model for user response."""

    user_id: str
    email: str
    first_name: str
    last_name: str
    street: str
    house_number: str | None
    postal_code: str
    city: str
    address_validation: AddressValidationResult


class AutocompleteResult(BaseModel):
    """Data model for address autocomplete result."""

    label: str
    street: str
    postal_code: str
    city: str


class AutocompleteResponse(BaseModel):
    """Data model for autocomplete response."""

    suggestions: list[AutocompleteResult]


def get_api_client() -> PostalAddressClient:
    """Get configured Swiss address client."""
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="API key not configured",
        )
    try:
        return PostalAddressClient(country="ch", api_key=api_key)
    except PostalAddressError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize API client: {exc}",
        ) from exc


def validate_swiss_address(address: AddressData) -> AddressValidationResult:
    """Validate a Swiss address using the API."""
    try:
        client = get_api_client()
        result = client.validate_address(
            street=address.street,
            house_number=address.house_number,
            zip_code=address.postal_code,
            city=address.city,
        )

        if result.Flag in [1, 2]:
            return AddressValidationResult(
                status="valid",
                normalized_street=result.Street or address.street,
                normalized_postal_code=result.Zipcode or address.postal_code,
                normalized_city=result.City or address.city,
                message="Address validated successfully",
            )
        else:
            return AddressValidationResult(
                status="invalid",
                normalized_street=address.street,
                normalized_postal_code=address.postal_code,
                normalized_city=address.city,
                message=f"Address could not be validated: {result.FlagText}",
            )
    except PostalAddressError as exc:
        return AddressValidationResult(
            status="error",
            normalized_street=address.street,
            normalized_postal_code=address.postal_code,
            normalized_city=address.city,
            message=str(exc),
        )


@app.post("/register", response_model=UserResponse)
async def register_user(req: UserRegistrationRequest) -> UserResponse:
    """Register a new user with Swiss address validation."""
    # Validate address
    address = AddressData(
        street=req.street,
        house_number=req.house_number,
        postal_code=req.postal_code,
        city=req.city,
    )
    validation = validate_swiss_address(address)

    # Create user
    user_id = str(uuid.uuid4())
    user = {
        "user_id": user_id,
        "email": req.email,
        "first_name": req.first_name,
        "last_name": req.last_name,
        "street": validation.normalized_street or req.street,
        "house_number": req.house_number,
        "postal_code": validation.normalized_postal_code or req.postal_code,
        "city": validation.normalized_city or req.city,
        "address_validation": validation,
    }
    users_db[user_id] = user

    return UserResponse(
        user_id=user_id,
        email=req.email,
        first_name=req.first_name,
        last_name=req.last_name,
        street=validation.normalized_street or req.street,
        house_number=req.house_number,
        postal_code=validation.normalized_postal_code or req.postal_code,
        city=validation.normalized_city or req.city,
        address_validation=validation,
    )


@app.get("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_swiss_address(q: str) -> AutocompleteResponse:
    """Get Swiss address suggestions for autocomplete."""
    if not q or len(q) < 2:
        return AutocompleteResponse(suggestions=[])

    try:
        client = get_api_client()
        results = client.autocomplete(q)

        suggestions = []
        if isinstance(results, list):
            for item in results[:10]:  # Limit to 10 suggestions
                suggestion = AutocompleteResult(
                    label=item.Street,
                    street=item.Street,
                    postal_code=item.Zipcode,
                    city=item.City,
                )
                if suggestion.label:
                    suggestions.append(suggestion)

        return AutocompleteResponse(suggestions=suggestions)

    except PostalAddressError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Autocomplete failed: {exc}",
        ) from exc


@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str) -> UserResponse:
    """Get user registration details."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found",
        )

    user = users_db[user_id]
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        street=user["street"],
        house_number=user.get("house_number"),
        postal_code=user["postal_code"],
        city=user["city"],
        address_validation=user["address_validation"],
    )


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    print("Starting Swiss Address API server...")
    print("Open http://localhost:8200/docs for interactive documentation")
    uvicorn.run(app, host="0.0.0.0", port=8200)
