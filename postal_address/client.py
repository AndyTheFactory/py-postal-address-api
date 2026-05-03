"""Client for AddressPerfect country-specific RapidAPI endpoints."""

from __future__ import annotations

import os
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
            raise PostalAddressError(
                f"Unsupported country '{country}'. Supported values: {supported}"
            )

        key = api_key or os.getenv("RAPIDAPI_KEY")
        if not key:
            raise PostalAddressError(
                "Missing API key. Provide api_key or set RAPIDAPI_KEY environment variable."
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

    def autocomplete(self, query: str) -> Any:
        """Search addresses with unstructured full-text query."""
        return self._get("/autocomplete", {"query": query})

    def get_street_list(
        self, street: str, zip_code: str | None = None, city: str | None = None
    ) -> Any:
        """Get a list of matching streets."""
        params = {"street": street, "zip": zip_code, "city": city}
        return self._get("/getstreetlist", params)

    def get_city_list(self, city: str, zip_code: str | None = None) -> Any:
        """Get a list of matching cities."""
        return self._get("/getcitylist", {"city": city, "zip": zip_code})

    def get_zip_list(self, zip_prefix: str, city: str | None = None) -> Any:
        """Get a list of matching zip codes."""
        return self._get("/getziplist", {"zip": zip_prefix, "city": city})

    def validate_address(
        self,
        street: str | None = None,
        house_number: str | None = None,
        zip_code: str | None = None,
        city: str | None = None,
    ) -> Any:
        """Validate and normalize an address."""
        params = {
            "street": street,
            "hnr": house_number,
            "zip": zip_code,
            "city": city,
        }
        return self._get("/validateaddress", params)

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
