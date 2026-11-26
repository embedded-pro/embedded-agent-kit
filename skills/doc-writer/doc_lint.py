#!/usr/bin/env python3
"""Check documents against the embedded-agent-kit Documentation rules.

Usage: doc_lint.py <repo_dir>. Exit 1 on an error. Sentence length is a warning.
Allowed terms: one per line in <docs>/.doc-lint-allow (for example a wire-contract message name).
"""
import pathlib
import re
import sys

DOC_DIRS = ["documentation", "docs", "doc"]
KINDS = ["theory", "architecture", "design", "verification_and_validation"]
FRONT_MATTER = ["title", "type", "status", "version", "date"]
MAX_WORDS = 25

FENCE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
CODE_SPAN = re.compile(r"`([^`\n]+)`")
CODE_LIKE = re.compile(r"::|\w\(|\.(?:hpp|cpp|h|c|py|cmake|json|ya?ml)\b|^[\w.-]+/[\w./-]+$"
                       r"|^[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+$|^[a-z]+(?:_[a-z0-9]+)+$|^[a-z]+[A-Z]\w*$")
HARDWARE = re.compile(r"\b(?:STM32\w*|TM4C\w*|NUCLEO\w*|EK-\w+|ESP32\w*|nRF5\d\w*|RP2040|ATSAM\w*|ATmega\w*"
                      r"|MSP430\w*|LPC\d+\w*|i\.MX\w*|PIC\d+\w*|\d+(?:\.\d+)? ?MHz"
                      r"|(?:status|control|configuration|reset|identity|data) registers?"
                      r"|registers? (?:write|read|map|bits?))\b", re.I)
OPEN_QUESTIONS = re.compile(r"^#+\s.*\bopen questions?\b", re.I | re.M)
NOT_RESPONSIBLE = re.compile(r"\bnot responsible\b", re.I)
MATH = re.compile(r"\$\$.*?\$\$|\$[^$]+\$", re.S)
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def code_name(span):
    """A code identifier or source path. A formula has spaces; a document path is not code."""
    if re.search(r"\s", span) or span.endswith(".md"):
        return False
    if span.split("/")[0] in DOC_DIRS + KINDS + ["tikz", "animations", "templates"]:
        return False
    return bool(CODE_LIKE.search(span))


def docs_root(repo_dir):
    return next((repo_dir / d for d in DOC_DIRS if (repo_dir / d).is_dir()), None)


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def front_matter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    keys = re.findall(r"^(\w+):", match.group(1), re.M) if match else []
    return [k for k in FRONT_MATTER if k not in keys]


def prose(text):
    """Text without fences, front matter, headings, tables, quotes and lists, with blank-line paragraphs."""
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    text = re.sub(r"^\$\$.*?^\$\$", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S | re.M)
    text = re.sub(r"\A---\n.*?\n---\n", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"^[ \t]*(?:#|\||>|[-*+]\s|\d+\.\s|<).*$", "", text, flags=re.M)


def long_sentences(text):
    body = prose(text)
    for paragraph in re.finditer(r"(?:[^\n]+\n?)+", body):
        flat = MATH.sub("x", CODE_SPAN.sub("x", paragraph.group(0).replace("\n", " ")))
        for sentence in SENTENCE.split(flat):
            if len(sentence.split()) > MAX_WORDS:
                yield line_of(body, paragraph.start()), len(sentence.split())


def check(path, kind, text, allowed):
    errors, warnings = [], []
    missing = front_matter(text)
    if missing:
        errors.append((1, f"front matter misses {', '.join(missing)}"))
    for m in OPEN_QUESTIONS.finditer(text):
        errors.append((line_of(text, m.start()), "Open Questions section: open an issue and link it"))
    if kind == "design":
        body = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), text)
        for m in NOT_RESPONSIBLE.finditer(body):
            errors.append((line_of(text, m.start()), "'not responsible' list: state boundaries in Interfaces"))
        for m in CODE_SPAN.finditer(body):
            span = m.group(1)
            if code_name(span) and span not in allowed:
                errors.append((line_of(text, m.start()), f"code name `{m.group(1)}`: name the component"))
        for m in HARDWARE.finditer(text):
            if m.group(0) not in allowed:
                errors.append((line_of(text, m.start()), f"hardware '{m.group(0)}': say 'the target'"))
    for line, words in long_sentences(text):
        warnings.append((line, f"sentence of {words} words (ASD-STE100: <= {MAX_WORDS})"))
    return errors, warnings


def lint(repo_dir):
    root = docs_root(repo_dir)
    if root is None:
        print(f"{repo_dir}: no {'/'.join(DOC_DIRS)} folder")
        return 1
    allow_file = root / ".doc-lint-allow"
    allowed = set(allow_file.read_text().split("\n")) - {""} if allow_file.exists() else set()
    n_errors = n_warnings = 0
    for kind in KINDS:
        for path in sorted((root / kind).rglob("*.md")) if (root / kind).is_dir() else []:
            if path.name == "README.md":
                continue
            errors, warnings = check(path, kind, path.read_text(), allowed)
            rel = path.relative_to(repo_dir)
            for line, msg in errors:
                print(f"{rel}:{line}: error: {msg}")
            for line, msg in warnings:
                print(f"{rel}:{line}: warning: {msg}")
            n_errors += len(errors)
            n_warnings += len(warnings)
    print(f"doc-lint: {n_errors} errors, {n_warnings} warnings")
    return 1 if n_errors else 0


if __name__ == "__main__":
    sys.exit(lint(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
