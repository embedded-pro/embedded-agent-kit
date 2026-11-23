def build(kit):
    files = {}
    for bundle, spec in kit.bundles().items():
        for agent in spec["agents"]:
            files[f"dist/claude/{bundle}/agents/{agent}.md"] = kit.agent(agent, "claude")
    return files


def sync(kit, repo_dir, bundles):
    written = kit.install(repo_dir, "claude", bundles, ".claude")
    shim = repo_dir / "CLAUDE.md"
    if not shim.exists():
        shim.write_text("@AGENTS.md\n")
    elif "@AGENTS.md" not in shim.read_text():
        kit.warn("CLAUDE.md does not import AGENTS.md; add '@AGENTS.md'")
    return written
