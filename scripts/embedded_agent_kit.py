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
        return json.dumps(data, indent=2) + "\n"

    @staticmethod
    def warn(message):
        print(f"warning: {message}")


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


def sync(repo_dir, repo):
    kit = Kit()
    bundles = json.loads((ROOT / "consumers.json").read_text())[repo]
    lock = repo_dir / LOCK
    previous = set(json.loads(lock.read_text())["files"]) if lock.exists() else set()
    sync_agents_md(kit, repo_dir, repo.split("/")[1])
    written = sync_skills(repo_dir, bundles)
    written = sorted(set(written) | {f for a in adapters() for f in a.sync(kit, repo_dir, bundles)})
    for stale in previous - set(written):
        (repo_dir / stale).unlink(missing_ok=True)
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
    s.add_argument("repo")
    sub.add_parser("verify").add_argument("repo_dir", type=pathlib.Path)
    a = parser.parse_args()
    if a.cmd == "build":
        return build(a.check)
    if a.cmd == "sync":
        return sync(a.repo_dir, a.repo)
    return verify(a.repo_dir)


if __name__ == "__main__":
    sys.exit(main())
