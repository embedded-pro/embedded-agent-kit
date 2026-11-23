# embedded-agent-kit

Vendor-neutral rules, agents and skills for AI coding assistants on embedded C++ projects, synced to Claude Code and GitHub Copilot.

| Path | Content |
|---|---|
| `rules/shared.md` | Shared AGENTS.md sections. Synced into each consumer between `shared:begin`/`shared:end`. |
| `rules/repo-template.md` | *Domain*, *Build*, *Exceptions* skeleton for a new consumer. |
| `agents/<name>/` | One agent: `body.md` (vendor-neutral) and one `<vendor>.yml` header per vendor. |
| `skills/<name>/SKILL.md` | One skill. Synced to `.claude/skills/`, which Claude Code and Copilot both read. |
| `bundles.json` | Agent and skill groups a consumer can enable. |
| `consumers.json` | Consumer repositories and their bundles. |
| `adapters/<vendor>.py` | `build` writes `dist/<vendor>/`; `sync` copies it into a consumer (`.claude/agents/`, `.github/agents/`). |
| `dist/` | Generated. Do not edit. |
| `scripts/embedded_agent_kit.py` | `build [--check]`, `sync <dir> <repo>`, `verify <dir>`. |

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

1. Add it to `consumers.json`.
2. Move its shared rules out of its AGENTS.md; keep *Domain*, *Build*, *Exceptions*.
3. Add `.github/workflows/agents.yml`:

```yaml
on: [pull_request]
jobs:
  agents:
    uses: embedded-pro/embedded-agent-kit/.github/workflows/verify-consumer.yml@main
```
