# Warranted Agent Examples

These examples are compact public artifacts for the warranted-agent framework.

- `research_success.json` shows the success path ending in `WARRANTY_RELEASED`.
- `payment_without_delivery.json` shows the failure path ending in `USER_PAID_FROM_BOND`.
- `registry_discovery.json` shows warrantability-based discovery.

Generate full live local output with:

```powershell
python -m flowmemory_compiler.cli agent-runtime-demo --json
python -m flowmemory_compiler.cli agent-registry-demo --json
python -m flowmemory_compiler.cli release-transcript --json
```

The examples are intentionally small. The canonical launch object is the release transcript.
