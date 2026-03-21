# Tooling

Automation code for this knowledge repository.

- `scripts/`: sync and schedule guard scripts
- `tests/`: unit tests for sync + schedule guard

Local checks:

```bash
python3 -m unittest discover -s tooling/tests -p 'test_*.py'
python3 tooling/scripts/sync_knowledge.py
```

Local GitHub Actions run with `act`:

```bash
act workflow_dispatch -j sync --container-architecture linux/amd64
```
