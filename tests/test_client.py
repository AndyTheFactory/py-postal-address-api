import pytest

from postal_address import PostalAddressClient, PostalAddressError


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


def test_init_uses_country_specific_host():
    client = PostalAddressClient(country="de", api_key="k")
    assert client.host == "addressperfect-german-streets.p.rapidapi.com"


def test_init_fails_without_key(monkeypatch):
    monkeypatch.delenv("RAPIDAPI_KEY", raising=False)
    with pytest.raises(PostalAddressError):
        PostalAddressClient(country="de")


def test_autocomplete_calls_expected_endpoint():
    response = DummyResponse(200, [{"Street": "Elisabethstr"}])
    session = DummySession(response)
    client = PostalAddressClient(country="fr", api_key="k", session=session)

    payload = client.autocomplete("Elisabeth")

    assert payload == [{"Street": "Elisabethstr"}]
    assert len(session.calls) == 1
    call = session.calls[0]
    assert call["url"].endswith("/autocomplete")
    assert call["params"] == {"query": "Elisabeth"}
    assert call["headers"]["x-rapidapi-host"] == "addressperfect-france-streets.p.rapidapi.com"


def test_api_error_raises_postal_address_error():
    response = DummyResponse(422, {"detail": [{"msg": "bad request"}]})
    session = DummySession(response)
    client = PostalAddressClient(country="de", api_key="k", session=session)

    with pytest.raises(PostalAddressError):
        client.get_street_list("ab")
