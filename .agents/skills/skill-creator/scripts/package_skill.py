#!/usr/bin/env python3
"""跨平台技能潔淨打包工具（支援產出 Gemini App 可直傳的 .zip 或 .skill）。

預設行為：
1. 先執行 quick_validate.py 嚴格驗證（含單行 description、24KB 上限與 TODO 阻擋）。
2. 自動排除 .git、__pycache__、*.pyc、.DS_Store、evals 等開發暫存與敏感檔。
3. 壓縮檔預設根目錄直接放入 SKILL.md（符合 Gemini App 上傳格式要求），輸出為 .zip；
   若需傳統外包一層目錄的 .skill 封裝，可加 --wrap-dir --ext .skill。
4. 若指定 --gemini，僅保留 Gemini App 上傳白名單（.pdf, .csv, .py, .txt, .md）。
"""

from __future__ import annotations

import argparse
import fnmatch
import sys
import zipfile
from pathlib import Path

try:
    from scripts.quick_validate import GEMINI_WHITELIST_EXTS, inspect_skill
except ImportError:
    from quick_validate import GEMINI_WHITELIST_EXTS, inspect_skill

EXCLUDE_DIRS = {
    "__pycache__",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "scratch",
    "_pending_delete_",
    "__MACOSX",
}
ROOT_EXCLUDE_DIRS = {"evals"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db", ".env"}
EXCLUDE_GLOBS = ("*.pyc", "*.pyo", "*.bak", "*.bak_*", ".env.*")


def should_exclude(rel_to_skill: Path) -> bool:
    """判斷相對於技能根目錄的檔案是否應在打包時排除。"""
    parts = rel_to_skill.parts
    if any(part in EXCLUDE_DIRS or part.endswith("-workspace") for part in parts):
        return True
    if parts and parts[0] in ROOT_EXCLUDE_DIRS:
        return True
    name = rel_to_skill.name
    if name == ".env.example":
        return False
    if name in EXCLUDE_FILES:
        return True
    return any(fnmatch.fnmatch(name, pattern) for pattern in EXCLUDE_GLOBS)


def package_skill(
    skill_path: str | Path,
    output_dir: str | Path | None = None,
    *,
    gemini_only: bool = False,
    wrap_dir: bool = False,
    extension: str = ".zip",
    skip_validate: bool = False,
) -> Path | None:
    """驗證並將技能資料夾打包為潔淨壓縮檔，回傳輸出路徑或 None。"""
    target = Path(skill_path).resolve()
    if not target.exists() or not target.is_dir():
        print(f"[ERROR] 找不到技能資料夾：{target}")
        return None
    if not (target / "SKILL.md").exists():
        print(f"[ERROR] 技能資料夾缺少 SKILL.md：{target}")
        return None

    if not skip_validate:
        print("[CHECK] 執行嚴格打包前驗證...")
        report = inspect_skill(target, strict=True)
        for warn in report.warnings:
            print(f"[WARN] {warn}")
        if not report.valid:
            for err in report.errors:
                print(f"[ERROR] {err}")
            print("[FAIL] 驗證未通過，已中止打包。")
            return None
        print(f"[OK] {report.message}\n")

    out_root = Path(output_dir).resolve() if output_dir else Path.cwd()
    out_root.mkdir(parents=True, exist_ok=True)

    ext = extension if extension.startswith(".") else f".{extension}"
    suffix = "_gemini" if gemini_only else ""
    archive_path = out_root / f"{target.name}{suffix}{ext}"

    added_files: list[str] = []
    skipped_files: list[str] = []
    non_whitelist_in_zip: list[str] = []

    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in sorted(target.rglob("*")):
                if not file_path.is_file():
                    continue
                rel_to_skill = file_path.relative_to(target)
                if should_exclude(rel_to_skill):
                    skipped_files.append(rel_to_skill.as_posix())
                    continue

                if gemini_only and file_path.suffix.lower() not in GEMINI_WHITELIST_EXTS:
                    skipped_files.append(f"{rel_to_skill.as_posix()} (非 Gemini 白名單)")
                    continue

                if file_path.suffix.lower() not in GEMINI_WHITELIST_EXTS:
                    non_whitelist_in_zip.append(rel_to_skill.as_posix())

                arcname = (
                    (Path(target.name) / rel_to_skill) if wrap_dir else rel_to_skill
                ).as_posix()
                zipf.write(file_path, arcname)
                added_files.append(arcname)
    except OSError as exc:
        print(f"[ERROR] 建立壓縮檔失敗：{exc}")
        return None

    if not added_files:
        print("[ERROR] 沒有任何檔案被納入壓縮包。")
        return None

    print(f"[OK] 已打包 {len(added_files)} 個檔案 -> {archive_path}")
    for item in added_files:
        print(f"  + {item}")
    if skipped_files:
        print(f"[INFO] 已略過 {len(skipped_files)} 個排除或非白名單項目")

    if not gemini_only and non_whitelist_in_zip:
        print(
            "\n[HINT] 此壓縮包內含 Gemini App 上傳白名單 (.pdf/.csv/.py/.txt/.md) 以外檔案："
            f"{', '.join(non_whitelist_in_zip[:5])}"
        )
        print("       若要直接上傳至 Gemini App，請改加 --gemini 參數重新打包。")

    return archive_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="將技能資料夾打包為潔淨 .zip 或 .skill 壓縮檔（預設根目錄直接包含 SKILL.md）。"
    )
    parser.add_argument("skill_dir", help="要打包的技能資料夾路徑")
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="輸出目錄（預設為目前工作目錄）",
    )
    parser.add_argument(
        "--gemini",
        action="store_true",
        help="僅打包 Gemini App 白名單檔型 (.pdf, .csv, .py, .txt, .md)",
    )
    parser.add_argument(
        "--wrap-dir",
        action="store_true",
        help="在壓縮檔內多包一層 <skill-name>/ 資料夾（預設為根目錄直接放 SKILL.md）",
    )
    parser.add_argument(
        "--ext",
        default=".zip",
        help="輸出副檔名（預設 .zip，相容需要時可改 .skill）",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="跳過驗證直接打包（僅供除錯使用）",
    )
    args = parser.parse_args()

    result = package_skill(
        args.skill_dir,
        args.output_dir,
        gemini_only=args.gemini,
        wrap_dir=args.wrap_dir,
        extension=args.ext,
        skip_validate=args.skip_validate,
    )
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
