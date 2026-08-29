import json

import pytest
from unittest.mock import Mock, patch

from lawcite.api import client
from lawcite.api.client import (
    resolve_law,
    parse_identifier,
    eli_pdf_url,
    eli_url,
    cache_dir,
    _is_rate_limited,
    RateLimitError,
)


def _resp(payload, status=200, json_ct=True):
    r = Mock()
    r.status_code = status
    r.headers = {"Content-Type": "application/json" if json_ct else "text/html"}
    r.json.return_value = payload
    r.raise_for_status = Mock()
    return r


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("LAWCITE_CACHE_DIR", str(tmp_path))
    return tmp_path


def test_url_helpers():
    assert (
        eli_pdf_url(2024, 1150)
        == "https://www.retsinformation.dk/eli/lta/2024/1150/pdf"
    )
    assert eli_url(2024, 1150) == "https://www.retsinformation.dk/eli/lta/2024/1150"
    assert eli_pdf_url(2024, 1150, "ltc").endswith("/ltc/2024/1150/pdf")


def test_cache_dir_created(_tmp_cache):
    assert cache_dir() == _tmp_cache
    assert cache_dir().is_dir()


def test_is_rate_limited_variants():
    assert _is_rate_limited(_resp({}, status=429)) is True
    assert _is_rate_limited(_resp({"error": "Rate limit overskredet"})) is True
    assert _is_rate_limited(_resp({"error": "something else"})) is False
    assert _is_rate_limited(_resp(None, json_ct=False)) is False
    bad = Mock()
    bad.status_code = 200
    bad.headers = {"Content-Type": "application/json"}
    bad.json.side_effect = ValueError("not json")
    assert _is_rate_limited(bad) is False


def test_resolve_success_and_cache(_tmp_cache):
    with patch("requests.get", return_value=_resp({"year": 2024, "number": 1150})) as g:
        assert resolve_law("konkurrenceloven") == (2024, 1150)
        assert g.call_count == 1
    # second call served from the resolve cache (no network)
    with patch("requests.get") as g2:
        assert resolve_law("Konkurrenceloven") == (2024, 1150)  # case-insensitive key
        g2.assert_not_called()
    cached = json.loads((_tmp_cache / "resolve.json").read_text(encoding="utf-8"))
    assert cached["konkurrenceloven"] == [2024, 1150]


def test_resolve_404_raises_valueerror():
    with patch("requests.get", return_value=_resp({"detail": "none"}, status=404)):
        with pytest.raises(ValueError, match="No law matched"):
            resolve_law("nonexistent-law")


def test_resolve_300_ambiguous():
    payload = {"candidates": [{"short_name": "LBK nr 1", "popular_title": "A"}]}
    with patch("requests.get", return_value=_resp(payload, status=300)):
        with pytest.raises(ValueError, match="Ambiguous"):
            resolve_law("lov")


def test_resolve_rate_limited():
    with patch("requests.get", return_value=_resp({"error": "Rate limit"}, status=429)):
        with pytest.raises(RateLimitError):
            resolve_law("konkurrenceloven")


def test_resolve_no_cache_flag(_tmp_cache):
    with patch("requests.get", return_value=_resp({"year": 2020, "number": 1})) as g:
        resolve_law("x", use_cache=False)
        resolve_law("x", use_cache=False)
        assert g.call_count == 2  # nothing cached
    assert not (_tmp_cache / "resolve.json").exists()


def test_parse_identifier_dispatch():
    assert parse_identifier("2024/1150") == (2024, 1150)
    with patch.object(client, "resolve_law", return_value=(2024, 1150)) as r:
        assert parse_identifier("konkurrenceloven") == (2024, 1150)
        r.assert_called_once()


def test_resolve_corrupt_cache_refetches(_tmp_cache):
    (_tmp_cache / "resolve.json").write_text("{ not json", encoding="utf-8")
    with patch("requests.get", return_value=_resp({"year": 2024, "number": 1150})) as g:
        assert resolve_law("konkurrenceloven") == (2024, 1150)
        assert g.call_count == 1  # corrupt cache ignored, re-resolved


def test_get_law_corrupt_cache_refetches(_tmp_cache):
    (_tmp_cache / "law-2024-1150.json").write_text("{ not json", encoding="utf-8")
    payload = {"year": 2024, "number": 1150, "structure": {"chapters": []}}
    with patch("requests.get", return_value=_resp(payload)) as g:
        assert client.get_law(2024, 1150) == payload
        assert g.call_count == 1  # corrupt cache forced a re-fetch
