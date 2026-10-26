"""Every column of every table in the README has a row in the glossary, so a reader can look up what the column means (a README without tables passes). Run: python tests/test_readme_columns.py"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def plain(cell):
    cell = re.sub(r'\[([^\]]*)\]\((?:[^()"]|"[^"]*")*\)', r"\1", cell)        # a link's text (its hover title may hold parentheses)
    return re.sub(r"[*`_]", "", cell).strip().lower()


def readme_columns():
    cols, lines = [], open(os.path.join(ROOT, "README.md")).read().splitlines()
    for i, l in enumerate(lines[:-1]):
        if l.startswith("|") and "-" in lines[i + 1] and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            cols += [plain(c) for c in re.split(r"\|(?=(?:[^\"]|\"[^\"]*\")*$)", l.strip().strip("|")) if c.strip()]
    return cols


def glossary_terms():
    terms = set()
    for l in open(os.path.join(ROOT, "docs", "glossary.md")):
        if l.startswith("|"):
            terms.add(plain(l.strip().strip("|").split("|")[0]))
    return terms


def test_every_readme_table_column_has_a_glossary_row():
    terms = glossary_terms()
    missing = [c for c in readme_columns() if c not in terms]
    assert not missing, f"README table columns without a glossary row: {missing}"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
