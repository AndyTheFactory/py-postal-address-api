"""Client for AddressPerfect country-specific RapidAPI endpoints."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests

from .exceptions import PostalAddressError

_COUNTRY_HOSTS: dict[str, str] = {
    "de": "addressperfect-german-streets.p.rapidapi.com",
    "sk": "addressperfect-slovak-streets.p.rapidapi.com",
    "nl": "addressperfect-dutch-streets.p.rapidapi.com",
    "fr": "addressperfect-france-streets.p.rapidapi.com",
    "cz": "addressperfect-czech-streets.p.rapidapi.com",
    "ch": "addressperfect-swiss-streets.p.rapidapi.com",
    "be": "addressperfect-belgium-streets.p.rapidapi.com",
    "at": "addressperfect-austrian-streets.p.rapidapi.com",
}
_REGISTER_URLS: dict[str, str] = {
    "de": "https://rapidapi.com/AndyTheFactory/api/addressperfect-german-streets",
    "sk": "https://rapidapi.com/AndyTheFactory/api/addressperfect-slovak-streets",
    "nl": "https://rapidapi.com/AndyTheFactory/api/addressperfect-dutch-streets",
    "fr": "https://rapidapi.com/AndyTheFactory/api/addressperfect-france-streets",
    "cz": "https://rapidapi.com/AndyTheFactory/api/addressperfect-czech-streets",
    "ch": "https://rapidapi.com/AndyTheFactory/api/addressperfect-swiss-streets",
    "be": "https://rapidapi.com/AndyTheFactory/api/addressperfect-belgium-streets",
    "at": "https://rapidapi.com/AndyTheFactory/api/addressperfect-austrian-streets",
}


@dataclass
class AddressResponse:
    """Response class for Address Validation and Autocomplete results."""

    Street: str
    Street_Long: str
    Hnr: str | None
    Zipcode: str
    City: str
    Country: str
    HnrValid: int
    Flag: int
    FlagText: str | None
    RatingOverall: int
    RatingStr: int
    RatingZIP: int
    RatingCity: int


class PostalAddressClient:
    """Simple wrapper around AddressPerfect RapidAPI endpoints.

    Args:
        country: Country code for selecting API host.
        api_key: RapidAPI key. If omitted, uses RAPIDAPI_KEY environment variable.
        timeout: Request timeout in seconds.
        session: Optional requests Session (useful for testing).
    """

    def __init__(
        self,
        country: str,
        api_key: str | None = None,
        timeout: float = 10.0,
        session: requests.Session | None = None,
    ) -> None:
        code = country.lower().strip()
        if code not in _COUNTRY_HOSTS:
            supported = ", ".join(sorted(_COUNTRY_HOSTS))
            raise PostalAddressError(f"Unsupported country '{country}'. Supported values: {supported}")

        key = api_key or os.getenv("RAPIDAPI_KEY")
        if not key:
            raise PostalAddressError(
                "Missing API key. Provide api_key or set RAPIDAPI_KEY environment variable.",
                f"Get a free API key from RapidAPI: {_REGISTER_URLS[code]}",
            )

        self.country = code
        self.host = _COUNTRY_HOSTS[code]
        self.base_url = f"https://{self.host}"
        self.timeout = timeout
        self._session = session or requests.Session()
        self._headers = {
            "x-rapidapi-key": key,
            "x-rapidapi-host": self.host,
            "Content-Type": "application/json",
        }

    def autocomplete(self, query: str) -> list[AddressResponse]:
        """Search addresses with unstructured full-text query.
        Args:
            query: Free-form search string (e.g. "Bahnhofstr 1 Zurich")
        Returns:
            List of matching address objects with details.
        """
        results = self._get("/autocomplete", {"query": query})
        return [AddressResponse(**item) for item in results]

    def get_street_list(self, street: str, zip_code: str | None = None, city: str | None = None) -> list[str]:
        """Get a list of matching streets.
        Args:
            street: Partial Street name (prefix) to search for.
            zip_code: Optional zip code to narrow the search.
            city: Optional city name to narrow the search.
        Returns:
            List of matching street names.
        """
        params = {"street": street, "zip": zip_code, "city": city}
        return self._get("/getstreetlist", params)

    def get_city_list(self, city: str, zip_code: str | None = None) -> list[str]:
        """Get a list of matching cities.
        Args:
            city: Partial city name (prefix) to search for.
            zip_code: Optional zip code to narrow the search.
        Returns:
            List of matching city names.
        """
        return self._get("/getcitylist", {"city": city, "zip": zip_code})

    def get_zip_list(self, zip_prefix: str, city: str | None = None) -> list[str]:
        """Get a list of matching zip codes.
        Args:
            zip_prefix: Partial zip code (prefix) to search for.
            city: Optional city name to narrow the search.
        Returns:
            List of matching zip codes.
        """
        return self._get("/getziplist", {"zip": zip_prefix, "city": city})

    def validate_address(
        self,
        street: str | None = None,
        house_number: str | None = None,
        zip_code: str | None = None,
        city: str | None = None,
    ) -> AddressResponse:
        """Validate and normalize an address.
        Args:
            street: Street name of the address.
            house_number: House number of the address.
            zip_code: Zip code of the address.
            city: City name of the address.
        Returns:
            AddressResponse object containing the validated and normalized address.
        """
        params = {
            "street": street,
            "hnr": house_number,
            "zip": zip_code,
            "city": city,
        }
        result = self._get("/validateaddress", params)
        return AddressResponse(**result)

    def _get(self, path: str, params: dict[str, Any]) -> Any:
        clean_params = {k: v for k, v in params.items() if v is not None}
        try:
            response = self._session.get(
                f"{self.base_url}{path}",
                params=clean_params,
                headers=self._headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise PostalAddressError(f"Request failed: {exc}") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise PostalAddressError("API did not return valid JSON.") from exc

        if response.status_code >= 400:
            raise PostalAddressError(f"API error {response.status_code}: {payload}")

        return payload
