import pytest

from postal_address import PostalAddressClient, PostalAddressError
from postal_address.client import AddressResponse

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_address(
    street="Elisabethstrasse",
    street_long="Elisabethstrasse",
    hnr=None,
    zipcode="75008",
    city="Paris",
    country="FR",
    hnr_valid=0,
    flag=1,
    flag_text="Street and zip code valid",
    rating_overall=90,
    rating_str=95,
    rating_zip=90,
    rating_city=85,
) -> dict:
    """Return a realistic raw API payload dict for one address entry."""
    return {
        "Street": street,
        "Street_Long": street_long,
        "Hnr": hnr,
        "Zipcode": zipcode,
        "City": city,
        "Country": country,
        "HnrValid": hnr_valid,
        "Flag": flag,
        "FlagText": flag_text,
        "RatingOverall": rating_overall,
        "RatingStr": rating_str,
        "RatingZIP": rating_zip,
        "RatingCity": rating_city,
    }


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class DummySession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append(
            {
                "url": url,
                "params": params,
                "headers": headers,
                "timeout": timeout,
            }
        )
        return self.response


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------


def test_init_uses_country_specific_host():
    client = PostalAddressClient(country="de", api_key="k")
    assert client.host == "addressperfect-german-streets.p.rapidapi.com"


def test_init_fails_without_key(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    with pytest.raises(PostalAddressError):
        PostalAddressClient(country="de")


# ---------------------------------------------------------------------------
# autocomplete
# ---------------------------------------------------------------------------


def test_autocomplete_returns_address_response_objects():
    raw = [
        _make_address(street="Elisabethstrasse", zipcode="75008", city="Paris"),
        _make_address(street="Elisabethweg", zipcode="75009", city="Paris"),
    ]
    session = DummySession(DummyResponse(200, raw))
    client = PostalAddressClient(country="fr", api_key="k", session=session)

    results = client.autocomplete("Elisabeth")

    assert len(results) == 2
    assert all(isinstance(r, AddressResponse) for r in results)
    assert results[0].Street == "Elisabethstrasse"
    assert results[0].Zipcode == "75008"
    assert results[0].City == "Paris"
    assert results[1].Street == "Elisabethweg"


def test_autocomplete_calls_expected_endpoint():
    session = DummySession(DummyResponse(200, [_make_address()]))
    client = PostalAddressClient(country="fr", api_key="k", session=session)

    client.autocomplete("Elisabeth")

    assert len(session.calls) == 1
    call = session.calls[0]
    assert call["url"].endswith("/autocomplete")
    assert call["params"] == {"query": "Elisabeth"}
    assert call["headers"]["x-rapidapi-host"] == "addressperfect-france-streets.p.rapidapi.com"


def test_autocomplete_empty_list():
    session = DummySession(DummyResponse(200, []))
    client = PostalAddressClient(country="fr", api_key="k", session=session)

    results = client.autocomplete("xyz")

    assert results == []


# ---------------------------------------------------------------------------
# validate_address
# ---------------------------------------------------------------------------


def test_validate_address_returns_address_response():
    raw = _make_address(
        street="Bahnhofstrasse",
        street_long="Bahnhofstrasse",
        hnr="1",
        zipcode="8001",
        city="Zurich",
        country="CH",
        hnr_valid=1,
        flag=1,
        flag_text="Street and zip code valid",
    )
    session = DummySession(DummyResponse(200, raw))
    client = PostalAddressClient(country="ch", api_key="k", session=session)

    result = client.validate_address(street="Bahnhofstrasse", house_number="1", zip_code="8001", city="Zurich")

    assert isinstance(result, AddressResponse)
    assert result.Street == "Bahnhofstrasse"
    assert result.Hnr == "1"
    assert result.Zipcode == "8001"
    assert result.City == "Zurich"
    assert result.Flag == 1
    assert result.FlagText == "Street and zip code valid"


def test_validate_address_calls_expected_endpoint():
    session = DummySession(DummyResponse(200, _make_address()))
    client = PostalAddressClient(country="ch", api_key="k", session=session)

    client.validate_address(street="Bahnhofstrasse", zip_code="8001", city="Zurich")

    call = session.calls[0]
    assert call["url"].endswith("/validateaddress")
    assert call["params"]["street"] == "Bahnhofstrasse"
    assert call["params"]["zip"] == "8001"
    assert call["params"]["city"] == "Zurich"
    assert "hnr" not in call["params"]  # None params are stripped


def test_validate_address_invalid_flag():
    raw = _make_address(flag=3, flag_text="Street not found", rating_overall=20)
    session = DummySession(DummyResponse(200, raw))
    client = PostalAddressClient(country="de", api_key="k", session=session)

    result = client.validate_address(street="Madeupstrasse", zip_code="10115", city="Berlin")

    assert result.Flag == 3
    assert result.FlagText == "Street not found"


# ---------------------------------------------------------------------------
# get_street_list / get_city_list / get_zip_list
# ---------------------------------------------------------------------------


def test_get_street_list_returns_strings():
    session = DummySession(DummyResponse(200, ["Hauptstrasse", "Hauptweg", "Hauptallee"]))
    client = PostalAddressClient(country="de", api_key="k", session=session)

    result = client.get_street_list(street="Haupt", zip_code="10115", city="Berlin")

    assert result == ["Hauptstrasse", "Hauptweg", "Hauptallee"]
    call = session.calls[0]
    assert call["url"].endswith("/getstreetlist")
    assert call["params"] == {"street": "Haupt", "zip": "10115", "city": "Berlin"}


def test_get_city_list_returns_strings():
    session = DummySession(DummyResponse(200, ["Zurich", "Zug", "Zollikon"]))
    client = PostalAddressClient(country="ch", api_key="k", session=session)

    result = client.get_city_list(city="Z", zip_code="80")

    assert result == ["Zurich", "Zug", "Zollikon"]
    call = session.calls[0]
    assert call["url"].endswith("/getcitylist")
    assert call["params"] == {"city": "Z", "zip": "80"}


def test_get_zip_list_returns_strings():
    session = DummySession(DummyResponse(200, ["8001", "8002", "8003"]))
    client = PostalAddressClient(country="ch", api_key="k", session=session)

    result = client.get_zip_list(zip_prefix="800", city="Zurich")

    assert result == ["8001", "8002", "8003"]
    call = session.calls[0]
    assert call["url"].endswith("/getziplist")
    assert call["params"] == {"zip": "800", "city": "Zurich"}


def test_get_street_list_optional_params_omitted():
    """zip_code and city are optional; None values must not appear in the request."""
    session = DummySession(DummyResponse(200, ["Marktstrasse"]))
    client = PostalAddressClient(country="de", api_key="k", session=session)

    client.get_street_list(street="Markt")

    call = session.calls[0]
    assert "zip" not in call["params"]
    assert "city" not in call["params"]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_api_error_raises_postal_address_error():
    response = DummyResponse(422, {"detail": [{"msg": "bad request"}]})
    session = DummySession(response)
    client = PostalAddressClient(country="de", api_key="k", session=session)

    with pytest.raises(PostalAddressError):
        client.get_street_list("ab")


def test_network_error_raises_postal_address_error():
    import requests as req

    class ErrorSession:
        def get(self, *args, **kwargs):
            raise req.ConnectionError("unreachable")

    client = PostalAddressClient(country="de", api_key="k", session=ErrorSession())

    with pytest.raises(PostalAddressError, match="Request failed"):
        client.autocomplete("test")


def test_invalid_json_raises_postal_address_error():
    class BadJsonResponse:
        status_code = 200

        def json(self):
            raise ValueError("no json")

    class BadJsonSession:
        def get(self, *args, **kwargs):
            return BadJsonResponse()

    client = PostalAddressClient(country="de", api_key="k", session=BadJsonSession())

    with pytest.raises(PostalAddressError, match="valid JSON"):
        client.autocomplete("test")
