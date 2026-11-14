#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


def _strip_yaml_quotes(value: str) -> str:
    """Strip matching surrounding single or double quotes from a YAML scalar."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _parse_frontmatter_fallback(frontmatter_text: str) -> dict:
    """Parse simple SKILL.md YAML frontmatter using only the Python standard library."""
    result = {}
    lines = frontmatter_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if line[0].isspace():
            raise ValueError(f"Unexpected indentation at line {i + 1}: {line}")
        if ":" not in line:
            raise ValueError(f"Invalid YAML line {i + 1}: {line}")

        key, raw_val = line.split(":", 1)
        key = key.strip()
        val = raw_val.strip()

        if val in (">", ">-", "|", "|-"):
            fold = val.startswith(">")
            block_lines = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip():
                    block_lines.append("")
                    i += 1
                    continue
                if nxt[0].isspace():
                    block_lines.append(nxt.strip() if fold else nxt.lstrip())
                    i += 1
                    continue
                break
            joiner = " " if fold else "\n"
            result[key] = joiner.join(part for part in block_lines if part != "" or not fold).strip()
            continue

        if val == "":
            nested = {}
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt.strip() or nxt.strip().startswith("#"):
                    i += 1
                    continue
                if nxt[0].isspace():
                    if ":" not in nxt:
                        raise ValueError(f"Invalid nested YAML line {i + 1}: {nxt}")
                    nkey, nval = nxt.strip().split(":", 1)
                    nested[nkey.strip()] = _strip_yaml_quotes(nval.strip())
                    i += 1
                    continue
                break
            result[key] = nested if nested else ""
            continue

        # Handle unquoted multiline continuation (plain scalar)
        parts = [_strip_yaml_quotes(val)]
        i += 1
        while i < len(lines) and lines[i].strip() and lines[i][0].isspace():
            parts.append(lines[i].strip())
            i += 1
        result[key] = " ".join(parts)

    return result


def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        if yaml is not None:
            frontmatter = yaml.safe_load(frontmatter_text)
        else:
            frontmatter = _parse_frontmatter_fallback(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except Exception as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)