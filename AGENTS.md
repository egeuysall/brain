# AGENTS

This repository uses modular agent instructions under `/agents`.

## Read Order

1. `/agents/README.md`
2. `/agents/01-ryva-core.mdx`
3. `/agents/02-output-principles.mdx`
4. `/agents/03-outbound-philosophy.mdx`
5. `/agents/04-icp-and-conversion.mdx`
6. `/agents/05-artifact-and-messaging.mdx`
7. `/agents/06-dm-playbook.mdx`
8. `/agents/07-research-playbook-usage.mdx`
9. `/agents/08-snapshot-usage.mdx`

## Required Runtime Inputs

- `resources/threads/RESEARCH_PLAYBOOK.mdx`
- `tooling/snapshot.json`

`tooling/snapshot.json` is a static architecture reference for how Ryva works.
It may be stale by date and that is acceptable.
Do not auto-refresh or overwrite it during normal agent runs.
