# Install and Compatibility

This skill uses Codex skill structure as the source of truth and can be copied into other agent ecosystems that accept `SKILL.md`-based skills.

## Canonical Structure

- `SKILL.md` (required)
- `agents/openai.yaml` (recommended UI metadata)
- `references/` (optional docs)
- `scripts/` (optional utilities)

## Install Paths

### Codex Global

```bash
mkdir -p ~/.codex/skills
cp -R paperbanana-agentic-illustration ~/.codex/skills/
```

### antigravity Project-Level

```bash
mkdir -p .agent/skills
cp -R paperbanana-agentic-illustration .agent/skills/
```

### antigravity Global

```bash
mkdir -p ~/.gemini/antigravity/skills
cp -R paperbanana-agentic-illustration ~/.gemini/antigravity/skills/
```

## Compatibility Notes

- If a host ignores `agents/openai.yaml`, workflow still runs from `SKILL.md`.
- Keep relative internal paths unchanged (`references/...`, `scripts/...`).
- Re-run validation after copy to detect accidental line-ending or encoding issues.

## Version-Drift Warning

antigravity loader paths may vary by release. If the host does not discover the skill, check local docs or runtime config and keep this skill folder unchanged while adjusting only install location.
