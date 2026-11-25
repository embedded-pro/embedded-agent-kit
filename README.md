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
| `templates/agents.yml` | Consumer workflow that runs `verify`. `sync --ref` writes it, pinned to a release. |
| `release-please-config.json` | Release settings. `.release-please-manifest.json` holds the last released version. |
| `adapters/<vendor>.py` | `build` writes `dist/<vendor>/`; `sync` copies it into a consumer (`.claude/agents/`, `.github/agents/`). |
| `dist/` | Generated. Do not edit. |
| `scripts/embedded_agent_kit.py` | `build [--check]`, `sync <dir> [--bundles a,b] [--name N] [--ref SHA --tag T]`, `verify <dir>`. |

Consumers get plain files, not plugins: a Claude Code plugin enabled in a repository's settings
does not install itself and is not added in cloud sessions. Plain files work everywhere.

## Change a rule, agent or skill

1. Edit `rules/`, `agents/` or `skills/`.
2. Run `python3 scripts/embedded_agent_kit.py build`.
3. Write Conventional Commit messages (`feat:`, `fix:`, `feat!:`). Do not edit `VERSION`.
4. Merge the release PR (see *Release*). `sync.yml` opens one PR per consumer.

## Add a vendor

1. Add `adapters/<vendor>.py` with `build(kit)` and `sync(kit, repo_dir, bundles)`.
2. Add it to `ADAPTERS` in `scripts/embedded_agent_kit.py`.
3. Add `agents/<name>/<vendor>.yml` for each agent.

## Add a consumer

The kit keeps no list of consumers. Each consumer owns its adoption: its bundles are in its own
`.embedded-agent-kit.json`.

1. In the consumer, run `python3 <kit>/scripts/embedded_agent_kit.py sync . --bundles core --ref <sha> --tag <tag>`,
   with the commit SHA and tag of the latest kit release. Add `toolbox` for a toolbox, `planning` for roadmap planning and feature delivery. This writes the agents, the
   skills, `.embedded-agent-kit.json`, `.github/workflows/agents.yml` and, if missing, `AGENTS.md`.
2. Move its shared rules out of its AGENTS.md; keep *Domain*, *Build*, *Exceptions*.

Later syncs read the bundles from `.embedded-agent-kit.json`. `sync.yml` finds every repository the sync app can
reach that has that file, and opens one PR per consumer. That PR also rewrites `agents.yml`, pinned to the new
release. Do not edit `agents.yml` in a consumer.

## Release

`release-please.yml` keeps a release PR open on `main`. It sets `VERSION` and `CHANGELOG.md` from the commit titles.
Before 1.0, `feat!` and `feat` bump the minor version; `fix` bumps the patch.
Merge the release PR: release-please tags the merge commit `v<VERSION>` and publishes the release.
It uses the `FOREST_RELEASER_APP_ID` app, so the published release starts `sync.yml`.
