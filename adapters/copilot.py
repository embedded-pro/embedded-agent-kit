def build(kit):
    files = {}
    for bundle, spec in kit.bundles().items():
        for agent in spec["agents"]:
            files[f"dist/copilot/{bundle}/agents/{agent}.agent.md"] = kit.agent(agent, "copilot")
    return files


def sync(kit, repo_dir, bundles):
    return kit.install(repo_dir, "copilot", bundles, ".github")
