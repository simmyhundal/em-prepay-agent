"""The README stays short, no doc heading names a milestone, and every relative link in the README and docs resolves. Run: python tests/test_readme_sync.py"""
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def pages():
    return [os.path.join(ROOT, "README.md")] + [os.path.join(ROOT, "docs", n) for n in sorted(os.listdir(os.path.join(ROOT, "docs"))) if n.endswith(".md")]


def test_readme_is_short():
    text = open(os.path.join(ROOT, "README.md")).read()
    assert len(text) <= 7000, f"the README is capped at 7,000 characters (now {len(text)})"


def test_no_section_title_in_the_docs_names_a_milestone():
    for page in pages():
        for line in open(page):
            if line.startswith("#"):
                assert "(Milestone" not in line and "Milestone " not in line.split("(")[0], (page, line)


def test_every_relative_link_resolves():
    for page in pages():
        text = open(page).read()
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text) + re.findall(r'src="([^"]+)"', text):
            if target.startswith(("http", "mailto:")):
                continue
            path = os.path.normpath(os.path.join(os.path.dirname(page), target))
            assert os.path.exists(path), f"{os.path.relpath(page, ROOT)} links to {target}, which does not exist"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
