import json
from unittest.mock import Mock, patch

from lawcite.parse.parse_api import (
    parse_selector,
    derive_namespace,
    parse_law_structure,
    filter_by_selector,
)
from lawcite.api.client import parse_identifier, get_law, RateLimitError


def test_parse_selector_forms():
    assert parse_selector(None) is None
    assert parse_selector("") is None
    assert parse_selector("9") == {"9"}
    assert parse_selector("9-12") == {"9", "10", "11", "12"}
    assert parse_selector("9,11,15a") == {"9", "11", "15a"}
    assert parse_selector("9-11,20") == {"9", "10", "11", "20"}


def test_parse_selector_edge_cases():
    # empty items in the list are skipped; non-numeric range bounds kept literally
    assert parse_selector("9,,11") == {"9", "11"}
    assert parse_selector("9a-12") == {"9a-12"}


def test_norm_para_no_match():
    from lawcite.parse.parse_api import _norm_para

    assert _norm_para("no paragraph here") == "no paragraph here"
    assert _norm_para("") == ""


def test_derive_namespace():
    assert derive_namespace("LBK nr 1150 af 03/11/2024", 2024, 1150) == "lbk2024-1150"
    assert derive_namespace("LOV nr 638 af 11/06/2024", 2024, 638) == "lov2024-638"
    assert derive_namespace("", 2024, 1150) == "2024-1150"


def test_parse_identifier_year_number():
    assert parse_identifier("2024/1150") == (2024, 1150)
    assert parse_identifier("2024 1150") == (2024, 1150)


def test_litra_folding():
    law = {
        "structure": {
            "chapters": [
                {
                    "chapter_number": "Kapitel 2",
                    "paragraph_groups": [
                        {
                            "paragraphs": [
                                {
                                    "number": "§ 6.",
                                    "stk": [
                                        {
                                            "number": "Stk. 1.",
                                            "text": "Det er forbudt at indgå aftaler, der",
                                            "litra": [
                                                {
                                                    "number": "a)",
                                                    "text": "fastsætter priser,",
                                                },
                                                {
                                                    "number": "b)",
                                                    "text": "begrænser produktionen.",
                                                },
                                            ],
                                        }
                                    ],
                                }
                            ]
                        }
                    ],
                }
            ]
        }
    }
    out = parse_law_structure(law)
    text = out[("2", "6", "Stk. 1.")]
    assert "a) fastsætter priser," in text
    assert "b) begrænser produktionen." in text


def test_filter_by_selector():
    content = {
        ("1", "9", "Stk. 1."): "a",
        ("1", "10", "Stk. 1."): "b",
        ("1", "15a", "Stk. 1."): "c",
    }
    assert set(filter_by_selector(content, None)) == set(content)
    assert set(filter_by_selector(content, {"9", "15a"})) == {
        ("1", "9", "Stk. 1."),
        ("1", "15a", "Stk. 1."),
    }


def _json_response(payload, status=200):
    resp = Mock()
    resp.status_code = status
    resp.headers = {"Content-Type": "application/json"}
    resp.json.return_value = payload
    resp.raise_for_status = Mock()
    return resp


def test_get_law_caches(tmp_path, monkeypatch):
    monkeypatch.setenv("LAWCITE_CACHE_DIR", str(tmp_path))
    payload = {"year": 2024, "number": 1150, "structure": {"chapters": []}}

    with patch("requests.get", return_value=_json_response(payload)) as mock_get:
        first = get_law(2024, 1150)
        second = get_law(2024, 1150)  # served from cache

    assert first == payload == second
    assert mock_get.call_count == 1  # second call hit the cache, not the network
    cached = json.loads((tmp_path / "law-2024-1150.json").read_text(encoding="utf-8"))
    assert cached["number"] == 1150


def test_get_law_rate_limited(tmp_path, monkeypatch):
    monkeypatch.setenv("LAWCITE_CACHE_DIR", str(tmp_path))
    limited = _json_response({"error": "Rate limit overskredet"}, status=429)

    with patch("requests.get", return_value=limited):
        try:
            get_law(2025, 716)
            raise AssertionError("expected RateLimitError")
        except RateLimitError:
            pass
