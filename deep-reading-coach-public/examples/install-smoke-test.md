# Local installation smoke test

The repository was tested as a local source with the public `skills` CLI using this equivalent command shape:

```bash
skills add /path/to/deep-reading-coach --skill deep-reading-coach --agent codex --copy -y
```

Sanitized result:

```text
Local path validated
Found 1 skill
Selected 1 skill: deep-reading-coach
copy → Codex
Installation complete
Installed 1 skill: deep-reading-coach
```

The installed copy contained `SKILL.md`, `agents/openai.yaml`, all four reference protocols, the multi-format inspector, its regression tests, and `test-prompts.json`.

This confirms local repository discovery and copying. It does not claim that a public GitHub URL works before the repository has been published; that URL must be smoke-tested again after publication.
