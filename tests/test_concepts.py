"""Concept pages exist with their four parts, every one has a glossary row, and the pages written for outside readers link the project terms they use. Run: python tests/test_concepts.py"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONCEPTS = os.path.join(ROOT, "docs", "concepts")
OUTSIDE_PAGES = ["docs/concepts/README.md"]          # add each new or changed page here (docs/process.md, Writing for outside readers)
OLD = []                                              # retired names that may not appear outside code spans: add as terms are renamed


def pages():
    return sorted(n for n in os.listdir(CONCEPTS) if n.endswith(".md") and n != "README.md")


def test_each_concept_page_has_its_four_parts_and_a_glossary_row():
    glossary = open(os.path.join(ROOT, "docs", "glossary.md")).read()
    index = open(os.path.join(CONCEPTS, "README.md")).read()
    assert len(pages()) >= 10
    for n in pages():
        text = open(os.path.join(CONCEPTS, n)).read()
        for part in ("**What it means.**", "**Why it exists.**", "**Example.**", "**Where to find it.**"):
            assert part in text, (n, part)
        assert f"concepts/{n}" in glossary, f"{n} has no glossary row"
        assert f"({n})" in index, f"{n} is not in the concepts index"


def test_old_names_do_not_appear_outside_code():
    for rel in OUTSIDE_PAGES:
        text = re.sub(r"`[^`]*`", "", open(os.path.join(ROOT, rel)).read())
        for old in OLD:
            assert old not in text, (rel, old)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
