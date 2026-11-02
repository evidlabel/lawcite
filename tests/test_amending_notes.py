"""Forvaltningsloven (LBK 433/2014): the amending laws' commencement clauses at
the end of the act must not replace § 3, § 4 and § 7, and numbered items get
keys of their own."""

import json
from pathlib import Path

import yaml

from lawcite.parse.parse_api import parse_law_structure
from lawcite.save.common import cite_label, section_slug
from lawcite.save.formats import HayagrivaFormat, MarkdownFormat

FIXTURE = Path(__file__).parent / "data" / "forvaltningsloven_2014_433.json"


def _law():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_real_text_survives_the_amending_notes(capsys):
    out = parse_law_structure(_law())
    assert out[("2", "3", "Stk. 1.")].startswith(
        "Den, der virker inden for den offentlige forvaltning"
    )
    assert out[("2", "4", "Stk. 1.")].startswith("Bestemmelserne i § 3 gælder ikke")
    assert out[("3", "7", "Stk. 1.")].startswith(
        "En forvaltningsmyndighed skal i fornødent omfang"
    )
    assert not any("træder i kraft" in text for text in out.values())
    assert "appears twice" not in capsys.readouterr().err


def test_duplicate_keeps_the_first(capsys):
    law = {
        "structure": {
            "chapters": [
                {
                    "chapter_number": "",
                    "paragraph_groups": [
                        {
                            "paragraphs": [
                                {
                                    "number": "§ 1.",
                                    "stk": [{"number": "Stk. 1.", "text": "first"}],
                                },
                                {
                                    "number": "§ 1.",
                                    "stk": [{"number": "Stk. 1.", "text": "second"}],
                                },
                            ]
                        }
                    ],
                },
            ]
        }
    }
    out = parse_law_structure(law)
    assert list(out.values()) == ["first"]
    assert "appears twice" in capsys.readouterr().err


def test_unnumbered_only_act_is_kept():
    law = {
        "structure": {
            "chapters": [
                {
                    "chapter_number": "",
                    "paragraph_groups": [
                        {
                            "paragraphs": [
                                {
                                    "number": "§ 1.",
                                    "stk": [
                                        {"number": "Stk. 1.", "text": "Loven gælder."}
                                    ],
                                },
                            ]
                        }
                    ],
                }
            ]
        }
    }
    assert parse_law_structure(law) == {("1", "1", "Stk. 1."): "Loven gælder."}


def test_numbered_items_have_keys():
    out = parse_law_structure(_law())
    assert out[("2", "3", "Stk. 1. nr. 1")].startswith(
        "vedkommende selv har en særlig personlig"
    )
    # the stk entry still carries the items folded in
    assert "1) vedkommende selv" in out[("2", "3", "Stk. 1.")]


def test_section_slug_and_label():
    assert section_slug("Stk. 1.") == "stk1"
    assert section_slug("Stk. 2. nr. 3") == "stk2nr3"
    assert section_slug("Stk. 1. litra a") == "stk1litraa"
    assert cite_label("7", "Stk. 1.", 1) == "§ 7"
    assert cite_label("7", "Stk. 2.", 2) == "§ 7, stk. 2"
    assert cite_label("3", "Stk. 1. nr. 2", 3) == "§ 3, stk. 1, nr. 2"
    assert cite_label("5", "Stk. 1. nr. 2", 1) == "§ 5, nr. 2"


def test_yaml_keys_and_no_stk1_label(tmp_path):
    out = parse_law_structure(_law())
    path = tmp_path / "fvl.yml"
    HayagrivaFormat().write(
        out,
        document_title="Forvaltningsloven",
        document_author="Justitsministeriet",
        document_url="https://www.retsinformation.dk/eli/lta/2014/433",
        document_date="2014-04-22",
        output_path=str(path),
        law_id="fvl",
        namespace="lbk2014-433",
    )
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert entries["lbk2014-433:p3stk1"]["title"].startswith("Den, der virker")
    assert entries["lbk2014-433:p3stk1nr1"]["author"] == [
        "Forvaltningsloven § 3, stk. 1, nr. 1"
    ]
    assert entries["lbk2014-433:p7stk1"]["author"] == ["Forvaltningsloven § 7, stk. 1"]
    assert not any(
        "Stk. 1." in a for e in entries.values() for a in e.get("author", [])
    )


def test_markdown_has_no_stk1_label_and_no_item_repeats(tmp_path):
    out = parse_law_structure(_law())
    path = tmp_path / "fvl.md"
    MarkdownFormat().write(
        out,
        document_title="Forvaltningsloven",
        document_author="",
        document_url="",
        document_date="",
        output_path=str(path),
        law_id="fvl",
    )
    md = path.read_text(encoding="utf-8")
    assert "Stk. 1." not in md
    assert "Stk. 2. " in md
    assert md.count("vedkommende selv har en særlig personlig") == 1
