"""Smoke tests verifying that the package imports and its public API behaves correctly.

These tests exercise the core paths without making real network requests so they
can run in any environment (including CI) without a valid RapidAPI key.
"""

import pytest

from postal_address import PostalAddressClient, PostalAddressError


def test_public_symbols_importable() -> None:
    """All symbols listed in __all__ are importable."""
    assert PostalAddressClient is not None
    assert PostalAddressError is not None


def test_client_init_de() -> None:
    """Client initialises successfully for a supported country code."""
    client = PostalAddressClient(country="de", api_key="smoke-test-key")
    assert client.country == "de"
    assert client.host == "addressperfect-german-streets.p.rapidapi.com"
    assert client.base_url == "https://addressperfect-german-streets.p.rapidapi.com"


@pytest.mark.parametrize("code", ["de", "sk", "nl", "fr", "cz", "ch", "be", "at"])
def test_client_init_all_supported_countries(code: str) -> None:
    """Client initialises without error for every supported country."""
    client = PostalAddressClient(country=code, api_key="smoke-test-key")
    assert client.country == code


def test_unsupported_country_raises() -> None:
    """An unsupported country code raises PostalAddressError with a helpful message."""
    with pytest.raises(PostalAddressError, match="Unsupported country"):
        PostalAddressClient(country="xx", api_key="smoke-test-key")


def test_missing_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing API key raises PostalAddressError with a helpful message."""
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    with pytest.raises(PostalAddressError, match="Missing API key"):
        PostalAddressClient(country="de")


def test_env_api_key_is_picked_up(monkeypatch: pytest.MonkeyPatch) -> None:
    """Client uses RAPIDAPI_KEY from the environment when no key is passed."""
    monkeypatch.setenv("RAPIDAPI_KEY", "env-key-smoke")
    client = PostalAddressClient(country="nl")
    assert client.country == "nl"


def test_country_code_is_normalized() -> None:
    """Country codes are lowercased and stripped before lookup."""
    client = PostalAddressClient(country=" DE ", api_key="smoke-test-key")
    assert client.country == "de"
