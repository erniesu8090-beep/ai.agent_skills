#!/usr/bin/env python3
"""跨平台技能快速驗證器（Antigravity / Claude Code / Codex / OpenCode / Gemini App）。

結合以下檢查規則，且僅使用 Python 3 標準函式庫（不需 PyYAML）：
1. YAML Frontmatter 結構與允許欄位檢查（name、description、license、allowed-tools、metadata、compatibility）
2. 命名格式（kebab-case、<=64 字元）與 description 單行/長度/角括號檢查（相容 Gemini CLI/App）
3. Antigravity 單檔大小上限（24,000 bytes）與建議行數（<=500 行）檢查
4. 殘留 TODO、冗餘說明檔（README.md 等）與 Gemini App 檔型白名單提示
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
GEMINI_WHITELIST_EXTS = {".pdf", ".csv", ".py", ".txt", ".md"}
SYSTEM_JUNK_NAMES = {".ds_store", "thumbs.db"}
SYSTEM_JUNK_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
EXTRANEOUS_DOCS = {
    "README.md",
    "CHANGELOG.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
}

MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
ANTIGRAVITY_MAX_BYTES = 24_000
ANTIGRAVITY_WARN_BYTES = 20_000
RECOMMENDED_MAX_LINES = 500

TODO_TAG = "TO" + "DO:"
TODO_PATTERN = re.compile(rf"(?:\b{re.escape(TODO_TAG)}|\[{re.escape(TODO_TAG)})")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
TOP_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:(.*)$")
MULTILINE_INDICATORS = {">", "|", ">-", "|-"}


@dataclass
class ValidationReport:
    """技能驗證結果結構。"""

    valid: bool
    message: str
    skill_path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int | str] = field(default_factory=dict)


def _unquote(value: str) -> str:
    """移除成對單引號或雙引號並去除前後空白。"""
    v = value.strip()
    if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
        return v[1:-1].strip()
    return v


def parse_frontmatter(content: str) -> tuple[dict[str, object], set[str], list[str]]:
    """使用純標準庫解析 YAML Frontmatter 頂層欄位並偵測多行區塊。

    回傳：(欄位字典, 使用多行語法的欄位集合, 解析錯誤訊息清單)。
    """
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return {}, set(), ["SKILL.md 開頭缺少標準 '---' YAML Frontmatter 分隔線"]

    lines = normalized.split("\n")
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, set(), ["SKILL.md 缺少結束的 '---' YAML Frontmatter 分隔線"]

    fm_lines = lines[1:end_idx]
    parsed: dict[str, object] = {}
    multiline_keys: set[str] = set()
    errors: list[str] = []

    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if line[0].isspace():
            errors.append(f"Frontmatter 第 {i + 2} 行出現預期外的縮排：'{line}'")
            i += 1
            continue

        match = TOP_KEY_RE.match(line)
        if not match:
            errors.append(f"Frontmatter 第 {i + 2} 行語法無效：'{line}'")
            i += 1
            continue

        key = match.group(1)
        raw_val = match.group(2).strip()

        # 收集緊隨其後的縮排子行（如 metadata 子鍵或 >- / | 多行字串）
        sub_lines: list[str] = []
        j = i + 1
        while j < len(fm_lines):
            nxt = fm_lines[j]
            if not nxt.strip() or nxt.strip().startswith("#"):
                sub_lines.append(nxt)
                j += 1
                continue
            if nxt[0].isspace():
                sub_lines.append(nxt)
                j += 1
                continue
            break

        non_empty_sub = [s for s in sub_lines if s.strip() and not s.strip().startswith("#")]

        if raw_val in MULTILINE_INDICATORS:
            multiline_keys.add(key)
            parsed[key] = " ".join(s.strip() for s in non_empty_sub)
        elif raw_val == "" and non_empty_sub:
            # 可能是巢狀 mapping（如 metadata:）或沒有 indicator 的多行純文字
            if all(":" in s for s in non_empty_sub):
                nested: dict[str, str] = {}
                for s in non_empty_sub:
                    sub_m = TOP_KEY_RE.match(s.strip())
                    if sub_m:
                        nested[sub_m.group(1)] = _unquote(sub_m.group(2))
                parsed[key] = nested
            else:
                multiline_keys.add(key)
                parsed[key] = " ".join(s.strip() for s in non_empty_sub)
        else:
            if non_empty_sub:
                multiline_keys.add(key)
                joined = f"{_unquote(raw_val)} " + " ".join(s.strip() for s in non_empty_sub)
                parsed[key] = joined.strip()
            else:
                parsed[key] = _unquote(raw_val)

        i = j

    return parsed, multiline_keys, errors


def _validate_metadata_fields(
    frontmatter: dict[str, object],
    multiline_keys: set[str],
    allow_multiline: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    """檢核允許欄位、name、description 與 compatibility。"""
    unexpected = sorted(set(frontmatter.keys()) - ALLOWED_PROPERTIES)
    if unexpected:
        allowed_str = ", ".join(sorted(ALLOWED_PROPERTIES))
        errors.append(
            f"Frontmatter 含有未預期欄位：{', '.join(unexpected)}（允許欄位：{allowed_str}）"
        )

    name_val = frontmatter.get("name")
    if name_val is None or not str(name_val).strip():
        errors.append("Frontmatter 缺少必填欄位 'name'")
    elif not isinstance(name_val, str):
        errors.append(f"'name' 必須為字串，實際為 {type(name_val).__name__}")
    else:
        name = name_val.strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            errors.append(f"技能名稱 '{name}' 必須為 kebab-case（僅限小寫英數與連字號）")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            errors.append(f"技能名稱 '{name}' 不可由 '-' 開頭／結尾或包含連續 '--'")
        if len(name) > MAX_SKILL_NAME_LENGTH:
            errors.append(f"技能名稱長度為 {len(name)} 字元，超過上限 {MAX_SKILL_NAME_LENGTH}")

    desc_val = frontmatter.get("description")
    if desc_val is None or not str(desc_val).strip():
        errors.append("Frontmatter 缺少必填欄位 'description'")
    elif not isinstance(desc_val, str):
        errors.append(f"'description' 必須為字串，實際為 {type(desc_val).__name__}")
    else:
        desc = desc_val.strip()
        if "description" in multiline_keys or "\n" in desc:
            msg = (
                "'description' 使用了多行折行（如 >- / | 或換行）；為相容 Google Gemini CLI "
                "與 Gemini App 解析器，請改寫為單行字串"
            )
            if allow_multiline:
                warnings.append(msg)
            else:
                errors.append(msg)
        if "<" in desc or ">" in desc:
            errors.append("'description' 不可包含角括號（< 或 >）")
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"'description' 長度為 {len(desc)} 字元，超過上限 {MAX_DESCRIPTION_LENGTH}"
            )

    compat_val = frontmatter.get("compatibility")
    if compat_val is not None and str(compat_val).strip():
        if not isinstance(compat_val, str):
            errors.append(f"'compatibility' 必須為字串，實際為 {type(compat_val).__name__}")
        elif len(compat_val) > MAX_COMPATIBILITY_LENGTH:
            errors.append(
                f"'compatibility' 長度為 {len(compat_val)} 字元，超過上限 {MAX_COMPATIBILITY_LENGTH}"
            )


def _scan_directory_hygiene(
    skill_path: Path,
    strict: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    """掃描 TODO 殘留、冗餘文件、系統垃圾檔與 Gemini App 白名單相容性。"""
    for doc_name in sorted(EXTRANEOUS_DOCS):
        if (skill_path / doc_name).exists():
            warnings.append(
                f"技能目錄內存在 '{doc_name}'；為節省 Token 與相容 Gemini App 上傳，建議移除或改放母本庫外層"
            )

    non_gemini_files: list[str] = []
    junk_found: list[str] = []
    todo_files: list[str] = []

    for item in sorted(skill_path.rglob("*")):
        rel_parts = item.relative_to(skill_path).parts
        if any(part in SYSTEM_JUNK_DIRS or part.endswith("-workspace") for part in rel_parts):
            if item.is_dir() and item.name in {"__pycache__"}:
                junk_found.append(str(item.relative_to(skill_path)))
            continue
        if not item.is_file():
            continue

        rel_str = item.relative_to(skill_path).as_posix()
        lower_name = item.name.lower()
        if lower_name in SYSTEM_JUNK_NAMES or item.suffix.lower() in {".pyc", ".pyo"}:
            junk_found.append(rel_str)
            continue

        if item.suffix.lower() not in GEMINI_WHITELIST_EXTS and rel_parts[0] not in {"evals"}:
            non_gemini_files.append(rel_str)

        try:
            text = item.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        scan_target = INLINE_CODE_RE.sub("", text) if item.suffix.lower() == ".md" else text
        if TODO_PATTERN.search(scan_target):
            todo_files.append(rel_str)

    if todo_files:
        msg = f"發現未解決的 TODO 標記：{', '.join(todo_files)}"
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    if junk_found:
        warnings.append(
            f"偵測到系統或編譯暫存檔（上傳 Gemini App 前應排除）：{', '.join(junk_found[:5])}"
        )

    if non_gemini_files:
        preview = ", ".join(non_gemini_files[:5])
        suffix = f" 等 {len(non_gemini_files)} 個檔案" if len(non_gemini_files) > 5 else ""
        warnings.append(
            f"含 Gemini App 上傳白名單 (.pdf/.csv/.py/.txt/.md) 以外檔案：{preview}{suffix}（打包時可加 --gemini 自動過濾）"
        )


def inspect_skill(
    skill_path: str | Path,
    strict: bool = False,
    allow_multiline: bool = False,
) -> ValidationReport:
    """執行完整跨平台技能驗證並回傳結構化報告。"""
    target = Path(skill_path).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    stats: dict[str, int | str] = {}

    if not target.exists() or not target.is_dir():
        return ValidationReport(
            valid=False,
            message=f"路徑不存在或非資料夾：{target}",
            skill_path=str(target),
            errors=[f"路徑不存在或非資料夾：{target}"],
        )

    skill_md = target / "SKILL.md"
    if not skill_md.exists():
        return ValidationReport(
            valid=False,
            message="找不到必填檔案 SKILL.md",
            skill_path=str(target),
            errors=["找不到必填檔案 SKILL.md"],
        )

    raw_bytes = skill_md.read_bytes()
    content = raw_bytes.decode("utf-8").lstrip("\ufeff")
    line_count = len(content.splitlines())
    byte_count = len(raw_bytes)
    stats = {"skill_md_bytes": byte_count, "skill_md_lines": line_count}

    if byte_count > ANTIGRAVITY_MAX_BYTES:
        errors.append(
            f"SKILL.md 大小為 {byte_count:,} bytes，超過 Antigravity 單檔上限 {ANTIGRAVITY_MAX_BYTES:,} bytes"
        )
    elif byte_count > ANTIGRAVITY_WARN_BYTES:
        warnings.append(
            f"SKILL.md 大小為 {byte_count:,} bytes，接近 Antigravity 上限 {ANTIGRAVITY_MAX_BYTES:,} bytes"
        )

    if line_count > RECOMMENDED_MAX_LINES:
        warnings.append(
            f"SKILL.md 共 {line_count} 行，建議控制在 {RECOMMENDED_MAX_LINES} 行內並將細節拆至 references/"
        )

    frontmatter, multiline_keys, parse_errors = parse_frontmatter(content)
    errors.extend(parse_errors)
    if not parse_errors:
        _validate_metadata_fields(frontmatter, multiline_keys, allow_multiline, errors, warnings)
        stats["name"] = str(frontmatter.get("name", ""))

    _scan_directory_hygiene(target, strict, errors, warnings)

    valid = len(errors) == 0
    if valid:
        summary = "Skill is valid!" if not warnings else f"Skill is valid!（含 {len(warnings)} 項提醒）"
    else:
        summary = f"驗證失敗（共 {len(errors)} 項錯誤）"

    return ValidationReport(
        valid=valid,
        message=summary,
        skill_path=str(target),
        errors=errors,
        warnings=warnings,
        stats=stats,
    )


def validate_skill(
    skill_path: str | Path,
    strict: bool = False,
    allow_multiline: bool = False,
) -> tuple[bool, str]:
    """相容舊版介面的驗證函式，回傳 (是否通過, 摘要訊息)。"""
    report = inspect_skill(skill_path, strict=strict, allow_multiline=allow_multiline)
    if report.valid:
        if report.warnings:
            detail = "; ".join(report.warnings)
            return True, f"{report.message} -> {detail}"
        return True, report.message
    return False, "; ".join(report.errors)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="驗證技能是否符合 Antigravity、Claude Code、Codex、OpenCode 與 Gemini App 跨平台規範。"
    )
    parser.add_argument("skill_dir", help="技能資料夾路徑")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="嚴格模式：殘留 TODO 標記也視為驗證失敗（打包前建議啟用）",
    )
    parser.add_argument(
        "--allow-multiline",
        action="store_true",
        help="允許 description 使用 YAML 多行折行（將降級為警告，不建議用於 Gemini）",
    )
    parser.add_argument("--json", action="store_true", help="輸出 JSON 格式完整報告")
    args = parser.parse_args()

    report = inspect_skill(
        args.skill_dir, strict=args.strict, allow_multiline=args.allow_multiline
    )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(f"[SKILL] {report.skill_path}")
        if report.stats:
            print(
                f"[STATS] SKILL.md = {report.stats.get('skill_md_lines', 0)} 行 / "
                f"{report.stats.get('skill_md_bytes', 0):,} bytes"
            )
        for warn in report.warnings:
            print(f"[WARN] {warn}")
        for err in report.errors:
            print(f"[ERROR] {err}")
        tag = "[OK]" if report.valid else "[FAIL]"
        print(f"{tag} {report.message}")

    return 0 if report.valid else 1


if __name__ == "__main__":
    sys.exit(main())
