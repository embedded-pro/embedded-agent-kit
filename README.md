# embedded-agent-kit

Vendor-neutral rules, agents and skills for AI coding assistants on embedded C++ projects, synced to Claude Code and GitHub Copilot.

| Path | Content |
|---|---|
| `rules/shared.md` | Shared AGENTS.md sections. Synced into each consumer between `shared:begin`/`shared:end`. |
| `rules/repo-template.md` | *Domain*, *Build*, *Exceptions* skeleton for a new consumer. |
| `agents/<name>/` | One agent: `body.md` (vendor-neutral) and one `<vendor>.yml` header per vendor. |
| `skills/<name>/SKILL.md` | One skill. Synced to `.claude/skills/`, which Claude Code and Copilot both read. |
| `bundles.json` | Agent and skill groups a consumer can enable. |
| `action.yml` | `verify` action. Consumers pin it by commit SHA. |
| `adapters/<vendor>.py` | `build` writes `dist/<vendor>/`; `sync` copies it into a consumer (`.claude/agents/`, `.github/agents/`). |
| `dist/` | Generated. Do not edit. |
| `scripts/embedded_agent_kit.py` | `build [--check]`, `sync <dir> [--bundles a,b] [--name N]`, `verify <dir>`. |

Consumers get plain files, not plugins: a Claude Code plugin enabled in a repository's settings
does not install itself and is not added in cloud sessions. Plain files work everywhere.

## Change a rule, agent or skill

1. Edit `rules/`, `agents/` or `skills/`.
2. Run `python3 scripts/embedded_agent_kit.py build`.
3. Bump `VERSION`.
4. Merge and publish a release. `sync.yml` opens one PR per consumer.

## Add a vendor

1. Add `adapters/<vendor>.py` with `build(kit)` and `sync(kit, repo_dir, bundles)`.
2. Add it to `ADAPTERS` in `scripts/embedded_agent_kit.py`.
3. Add `agents/<name>/<vendor>.yml` for each agent.

## Add a consumer

The kit keeps no list of consumers. Each consumer owns its adoption: its bundles are in its own
`.embedded-agent-kit.json`.

1. In the consumer, run `python3 <kit>/scripts/embedded_agent_kit.py sync . --bundles core` (add `toolbox` for a
   toolbox). This writes the agents, the skills, `.embedded-agent-kit.json` and, if missing, `AGENTS.md`.
2. Move its shared rules out of its AGENTS.md; keep *Domain*, *Build*, *Exceptions*.
3. Add `.github/workflows/agents.yml`, pinned to a kit release by commit SHA:

```yaml
name: Agent Rules
on: [pull_request]
permissions: {}
jobs:
  agents-md:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: embedded-pro/embedded-agent-kit@<commit-sha> # v<version>
```

Later syncs read the bundles from `.embedded-agent-kit.json`. `sync.yml` finds every repository the sync app can
reach that has that file, and opens one PR per consumer that also moves the action pin to the new release.

## Release

1. Bump `VERSION`; run `python3 scripts/embedded_agent_kit.py build`.
2. Merge, then tag the merge commit `v<VERSION>` and publish a GitHub release for it.
