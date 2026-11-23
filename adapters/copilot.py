def build(kit):
    files = {}
    for bundle, spec in kit.bundles().items():
        base = f"dist/copilot/{bundle}"
        for agent in spec["agents"]:
            files[f"{base}/agents/{agent}.agent.md"] = kit.agent(agent, "copilot")
        for skill in spec["skills"]:
            files[f"{base}/skills/{skill}/SKILL.md"] = kit.skill(skill)
    return files


def sync(kit, repo_dir, bundles):
    written = []
    for bundle in bundles:
        source = kit.root / f"dist/copilot/{bundle}"
        for path in sorted(p for p in source.rglob("*") if p.is_file()):
            target = f".github/{path.relative_to(source)}"
            (repo_dir / target).parent.mkdir(parents=True, exist_ok=True)
            (repo_dir / target).write_text(path.read_text())
            written.append(target)
    return written
