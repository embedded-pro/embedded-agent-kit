import json

MARKETPLACE = "embedded-agent-kit"
MARKETPLACE_REPO = "embedded-pro/embedded-agent-kit"


def build(kit):
    files = {}
    plugins = []
    for bundle, spec in kit.bundles().items():
        base = f"dist/claude/{bundle}"
        files[f"{base}/.claude-plugin/plugin.json"] = kit.dump(
            {"name": bundle, "version": kit.version(), "description": spec["description"]})
        for agent in spec["agents"]:
            files[f"{base}/agents/{agent}.md"] = kit.agent(agent, "claude")
        for skill in spec["skills"]:
            files[f"{base}/skills/{skill}/SKILL.md"] = kit.skill(skill)
        plugins.append({"name": bundle, "source": f"./{base}", "description": spec["description"]})
    files[".claude-plugin/marketplace.json"] = kit.dump(
        {"name": MARKETPLACE, "owner": {"name": "embedded-pro"}, "plugins": plugins})
    return files


def sync(kit, repo_dir, bundles):
    path = repo_dir / ".claude/settings.json"
    settings = json.loads(path.read_text()) if path.exists() else {}
    settings.setdefault("extraKnownMarketplaces", {})[MARKETPLACE] = {
        "source": {"source": "github", "repo": MARKETPLACE_REPO}}
    enabled = settings.setdefault("enabledPlugins", {})
    for key in [k for k in enabled if k.endswith(f"@{MARKETPLACE}")]:
        del enabled[key]
    enabled.update({f"{b}@{MARKETPLACE}": True for b in bundles})
    path.parent.mkdir(exist_ok=True)
    path.write_text(kit.dump(settings))

    shim = repo_dir / "CLAUDE.md"
    if not shim.exists():
        shim.write_text("@AGENTS.md\n")
    elif "@AGENTS.md" not in shim.read_text():
        kit.warn("CLAUDE.md does not import AGENTS.md; add '@AGENTS.md'")
    return []
