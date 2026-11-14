---
name: skill-creator
description: Create, edit, validate, and package Agent Skills following the agentskills.io standard. Use when users want to create a skill from scratch, refactor or slim down an existing skill, refine a skill's trigger description, validate SKILL.md frontmatter, or package a skill folder into a .skill archive.
---

# Skill Creator (Slim Edition)

A streamlined guide and toolset for creating, refactoring, validating, and packaging Agent Skills across Antigravity, Claude Code, Codex, and OpenCode.

## Core Process

1. **Capture Intent** — Clarify what the skill enables, when it should trigger, expected outputs, and required bundled resources.
2. **Interview & Research** — Identify edge cases, constraints, existing scripts/patterns, and target agent environments (keeping instructions agent-neutral unless the skill targets a specific tool).
3. **Author `SKILL.md` & Resources** — Write concise instructions and add deterministic `scripts/`, on-demand `references/`, or output `assets/` as needed.
4. **Validate & Package** — Run `scripts/quick_validate.py` (and `scripts/package_skill.py` when distributing).
5. **Iterate on Real Usage** — Test on real tasks, trim token bloat, and refine the `description` trigger if the skill under- or over-triggers.

---

## Creating a Skill

### Capture Intent

If the current conversation already demonstrates a workflow to capture (e.g., "turn this into a skill"), extract the steps, tools, corrections, and input/output formats from history first, then confirm gaps with the user:

1. What should this skill enable the agent to do?
2. When should this skill trigger (what user phrases or contexts)?
3. What is the expected output format or verification bar?
4. Which bundled resources (`scripts/`, `references/`, `assets/`) are actually needed?

### Anatomy of a Skill

```text
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required; optional: license, compatibility, metadata, allowed-tools)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic or repetitive tasks
    ├── references/ - Docs loaded into context only when needed
    └── assets/     - Templates, icons, fonts, boilerplate used in outputs
```

Do not add extraneous user docs (`README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md`) inside a skill folder unless the skill's specific repository convention requires it.

### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (`name` + `description`) — Always in context (~100 words).
2. **`SKILL.md` body** — Loaded only when the skill triggers (keep under 500 lines).
3. **Bundled resources** — Loaded or executed on demand (scripts can run without reading them into context).

**Key patterns:**
- **Domain / Router organization**: When a skill covers multiple domains, workflows, or platforms, keep routing and shared principles in `SKILL.md` and split variant details into `references/<variant>.md`.
- **Single-level references**: Link reference files directly from `SKILL.md` and state clearly *when* to read each file. For long reference files (>300 lines), include a table of contents.
- **Avoid duplication**: Keep details in either `SKILL.md` or `references/`, not both.

---

## Writing `SKILL.md`

### Frontmatter Rules

- **`name`**: Lowercase letters, digits, and hyphens only (`kebab-case`, max 64 chars, must match the skill folder name).
- **`description`**: Primary triggering mechanism (max 1024 chars, no `<` or `>`). Include **both** what the skill does AND specific triggers/contexts for when to use it. Put all "when to use" cues here rather than in the body.
- **`license` / `compatibility` / `metadata` / `allowed-tools`**: Optional standard fields supported by `quick_validate.py`.

### Writing Style

- **Concise is key**: Only include procedural knowledge, edge cases, and commands the model cannot reliably infer on its own.
- **Explain the why**: Explaining reasoning works better than brittle all-caps commands.
- **Prefer imperative form** for step-by-step workflows and explicit examples for output formats.
- **Principle of Lack of Surprise**: Skills must never contain malware, exploit code, or hidden instructions that contradict the stated purpose.

---

## Validation & Packaging

Always run the validation script from the skill-creator folder (or pass its path) after creating or modifying any skill:

### 1. Validate Structure & Frontmatter

```bash
python .agents/skills/skill-creator/scripts/quick_validate.py <path-to-skill-folder>
```

Checks checked by `quick_validate.py`:
- `SKILL.md` exists and starts with valid YAML frontmatter.
- Only allowed frontmatter keys (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`).
- `name` is valid `kebab-case` (≤ 64 chars).
- `description` is present, ≤ 1024 chars, and free of `<` / `>`.

### 2. Package into `.skill` Archive (Optional)

When distributing a standalone `.skill` bundle:

```bash
python -m scripts.package_skill <path-to-skill-folder> [output-directory]
```

*(Run from `.agents/skills/skill-creator/` so `scripts.quick_validate` resolves cleanly.)*

It runs `quick_validate.py` first and creates `<skill-name>.skill` (zip format), automatically excluding `__pycache__/`, `*.pyc`, `node_modules/`, `.DS_Store`, and root `evals/`.
