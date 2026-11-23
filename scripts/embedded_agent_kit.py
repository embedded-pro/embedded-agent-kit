#!/usr/bin/env python3
import argparse
import hashlib
import importlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
ADAPTERS = ["claude", "copilot"]
LOCK = ".embedded-agent-kit.json"
BLOCK = re.compile(r"<!-- shared:begin (\S+) sha256:(\w+) -->\n(.*?)<!-- shared:end -->\n", re.S)
REPO_SECTIONS = ["## Domain", "## Build", "## Exceptions"]


class Kit:
    root = ROOT

    def version(self):
        return (ROOT / "VERSION").read_text().strip()

    def bundles(self):
        return json.loads((ROOT / "bundles.json").read_text())

    def agent(self, name, vendor):
        front = (ROOT / f"agents/{name}/{vendor}.yml").read_text()
        return f"---\n{front}---\n" + (ROOT / f"agents/{name}/body.md").read_text()

    def skill(self, name):
        return (ROOT / f"skills/{name}/SKILL.md").read_text()

    def install(self, repo_dir, vendor, bundles, target_root):
        written = []
        for bundle in bundles:
            source = ROOT / f"dist/{vendor}/{bundle}"
            for path in sorted(p for p in source.rglob("*") if p.is_file()):
                written.append(copy(path, repo_dir, f"{target_root}/{path.relative_to(source)}"))
        return written

    @staticmethod
    def dump(data):
        lines = ["{"]
        for index, (key, value) in enumerate(data.items()):
            comma = "," if index < len(data) - 1 else ""
            lines += json_member(json.dumps(key), value, comma)
        return "\n".join(lines + ["}"]) + "\n"

    @staticmethod
    def warn(message):
        print(f"warning: {message}")


def json_member(key, value, comma):
    if not isinstance(value, list):
        return [f"  {key}: {json.dumps(value)}{comma}"]
    one_line = f"  {key}: [{', '.join(json.dumps(v) for v in value)}]{comma}"
    if len(one_line) <= 80:
        return [one_line]
    items = [f"    {json.dumps(v)}," for v in value]
    items[-1] = items[-1].rstrip(",")
    return [f"  {key}: ["] + items + [f"  ]{comma}"]


def copy(source, repo_dir, target):
    (repo_dir / target).parent.mkdir(parents=True, exist_ok=True)
    (repo_dir / target).write_text(source.read_text())
    return target


def sync_skills(repo_dir, bundles):
    names = [s for b in bundles for s in Kit().bundles()[b]["skills"]]
    return [copy(ROOT / f"skills/{n}/SKILL.md", repo_dir, f".claude/skills/{n}/SKILL.md") for n in names]


def adapters():
    return [importlib.import_module(f"adapters.{name}") for name in ADAPTERS]


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def build(check):
    files = {path: text for a in adapters() for path, text in a.build(Kit()).items()}
    stale = [p for p, text in files.items() if not (ROOT / p).exists() or (ROOT / p).read_text() != text]
    orphans = [str(p.relative_to(ROOT)) for p in (ROOT / "dist").rglob("*") if p.is_file()
               and str(p.relative_to(ROOT)) not in files] if (ROOT / "dist").exists() else []
    if check:
        for p in stale + orphans:
            print(f"stale: {p}")
        return 1 if stale or orphans else 0
    for p in orphans:
        (ROOT / p).unlink()
    for p, text in files.items():
        (ROOT / p).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / p).write_text(text)
    return 0


def shared_block(kit):
    text = (ROOT / "rules/shared.md").read_text()
    return f"<!-- shared:begin {kit.version()} sha256:{digest(text)} -->\n{text}<!-- shared:end -->\n"


def sync_agents_md(kit, repo_dir, name):
    path = repo_dir / "AGENTS.md"
    if not path.exists():
        template = (ROOT / "rules/repo-template.md").read_text()
        path.write_text(f"# {name} — Agent Rules\n\n{shared_block(kit)}\n{template}")
        return
    text = path.read_text()
    if not BLOCK.search(text):
        sys.exit(f"{path}: no shared block; migrate it by hand first")
    path.write_text(BLOCK.sub(lambda _: shared_block(kit), text, count=1))


def consumer_bundles(repo_dir, requested):
    lock = repo_dir / LOCK
    bundles = requested or (json.loads(lock.read_text())["bundles"] if lock.exists() else None)
    if not bundles:
        sys.exit(f"{repo_dir}: no {LOCK}; pass --bundles for the first sync")
    unknown = sorted(set(bundles) - set(Kit().bundles()))
    if unknown:
        sys.exit(f"unknown bundle(s): {', '.join(unknown)}")
    return bundles


def sync(repo_dir, requested, name):
    kit = Kit()
    bundles = consumer_bundles(repo_dir, requested)
    lock = repo_dir / LOCK
    previous = set(json.loads(lock.read_text())["files"]) if lock.exists() else set()
    sync_agents_md(kit, repo_dir, name or repo_dir.resolve().name)
    written = sync_skills(repo_dir, bundles)
    written = sorted(set(written) | {f for a in adapters() for f in a.sync(kit, repo_dir, bundles)})
    for stale in previous - set(written):
        path = repo_dir / stale
        path.unlink(missing_ok=True)
        while path.parent != repo_dir and not any(path.parent.iterdir()):
            path = path.parent
            path.rmdir()
    lock.write_text(kit.dump({"version": kit.version(), "bundles": bundles, "files": written}))
    return 0


def verify(repo_dir):
    text = (repo_dir / "AGENTS.md").read_text()
    match = BLOCK.search(text)
    errors = []
    if not match:
        errors.append("shared block missing")
    elif digest(match.group(3)) != match.group(2):
        errors.append("shared block edited locally; change it in embedded-agent-kit")
    errors += [f"missing section: {s}" for s in REPO_SECTIONS if not re.search(rf"^{re.escape(s)}\b", text, re.M)]
    for e in errors:
        print(f"AGENTS.md: {e}")
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(prog="embedded_agent_kit")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").add_argument("--check", action="store_true")
    s = sub.add_parser("sync")
    s.add_argument("repo_dir", type=pathlib.Path)
    s.add_argument("--bundles", type=lambda v: [b for b in v.split(",") if b],
                   help="comma-separated bundles; default: the bundles in the consumer's lock file")
    s.add_argument("--name", help="title for a new AGENTS.md; default: the directory name")
    sub.add_parser("verify").add_argument("repo_dir", type=pathlib.Path)
    a = parser.parse_args()
    if a.cmd == "build":
        return build(a.check)
    if a.cmd == "sync":
        return sync(a.repo_dir, a.bundles, a.name)
    return verify(a.repo_dir)


if __name__ == "__main__":
    sys.exit(main())
