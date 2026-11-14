#!/usr/bin/env python3
"""技能初始化工具（適用於 Antigravity、Claude Code、Codex、OpenCode 與 Gemini App）。

建立符合 agentskills.io 開放標準與跨平台交集規範的技能資料夾骨架（SKILL.md 與選用資源目錄），
僅使用 Python 3 標準函式庫，無任何第三方套件依賴。

用法：
    python init_skill.py <skill-name> --path <output-dir> [--resources scripts,references,assets] [--examples]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_SKILL_NAME_LENGTH = 64
ALLOWED_RESOURCES = ("scripts", "references", "assets")
# 組合佔位標籤，避免初始化器原始碼在自我驗證時被誤判為未完成待辦
_TODO_TAG = "TO" + "DO:"

SKILL_TEMPLATE = """---
name: {skill_name}
description: "[{todo} 用單行文字說明此技能的功能、適用情境與具體觸發關鍵字（禁止換行或折行語法、不可含角括號、建議 1024 字元內）]"
---

# {skill_title}

[{todo} 用 1–2 句話說明此技能解決什麼問題與核心產出。]

## 適用情境

- [{todo} 列出使用者會說什麼或遇到什麼任務時應觸發此技能]
- [{todo} 補充邊界條件或不要觸發的情境（若有）]

## 核心執行流程

### 1. [{todo} 第一步名稱]
- [{todo} 填寫具體可執行的步驟、指令或判斷標準]

### 2. [{todo} 第二步名稱]
- [{todo} 若需呼叫附帶腳本，以相對路徑引用（例如 `[helper.py](./scripts/helper.py)`）]

## 品質與驗證標準

- [{todo} 說明完成後應檢查哪些項目或執行哪些驗證指令]
{resources_section}"""

RESOURCES_SECTION_TEMPLATE = """
## 附帶資源說明

{resources_bullets}"""

RESOURCE_DESCRIPTIONS = {
    "scripts": "- `scripts/`：確定性或重複性工作的可執行腳本（建議僅用 Python 標準庫並指定 UTF-8）。",
    "references": "- `references/`：僅在特定分支才需要讀入的參考文件與規格（與 `SKILL.md` 維持一層深度）。",
    "assets": "- `assets/`：輸出成品時直接複製或套用的範本、資料檔或媒體資源。",
}

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""{skill_name} 的輔助執行腳本範例。

請改寫為實際邏輯；若不需要腳本請移除此檔案與空的 scripts/ 目錄。
"""

from __future__ import annotations

from pathlib import Path


def main() -> None:
    skill_dir = Path(__file__).resolve().parent.parent
    print(f"[INFO] 技能根目錄: {{skill_dir}}")
    # {todo} 在此實作實際邏輯


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = """# {skill_title} 參考文件

此為參考文件範本，請替換為實際規格、指令對照或領域知識；若不需要請刪除此檔。

## 目錄（文件超過 100 行時建議保留）

- [核心規則](#核心規則)
- [常見問題](#常見問題)

## 核心規則

- {todo} 填寫不常變動但詳細的規格、參數表或範例，避免塞進 `SKILL.md` 占用常駐空間。

## 常見問題

- {todo} 列出實作或驗證時常見的陷阱與解法。
"""

EXAMPLE_ASSET = """# {skill_title} 輸出資源範本

此位置存放輸出成品時會用到的範本或靜態檔案（例如 .csv、.txt、.md 等）。
{todo} 替換為實際資源檔；若不需要請刪除此檔。
"""


def normalize_skill_name(raw_name: str) -> str:
    """將輸入名稱正規化為小寫連字號格式（kebab-case）。"""
    normalized = raw_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized


def title_case_skill_name(skill_name: str) -> str:
    """將連字號技能名稱轉為標題格式。"""
    return " ".join(word.capitalize() for word in skill_name.split("-") if word)


def parse_resources(raw_resources: str) -> list[str]:
    """解析並驗證 --resources 參數清單。"""
    if not raw_resources.strip():
        return []
    items = [item.strip().lower() for item in raw_resources.split(",") if item.strip()]
    invalid = sorted({item for item in items if item not in ALLOWED_RESOURCES})
    if invalid:
        allowed = ", ".join(ALLOWED_RESOURCES)
        raise ValueError(f"不支援的資源目錄：{', '.join(invalid)}（僅支援：{allowed}）")
    deduped: list[str] = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped


def create_resource_dirs(
    skill_dir: Path,
    skill_name: str,
    skill_title: str,
    resources: list[str],
    include_examples: bool,
) -> None:
    """依選擇建立 scripts/、references/、assets/ 目錄與可選範例檔案。"""
    example_files = {
        "scripts": ("example.py", EXAMPLE_SCRIPT.format(skill_name=skill_name, todo=_TODO_TAG)),
        "references": ("guide.md", EXAMPLE_REFERENCE.format(skill_title=skill_title, todo=_TODO_TAG)),
        "assets": ("template.txt", EXAMPLE_ASSET.format(skill_title=skill_title, todo=_TODO_TAG)),
    }
    for resource in resources:
        target_dir = skill_dir / resource
        target_dir.mkdir(parents=True, exist_ok=True)
        if include_examples:
            filename, content = example_files[resource]
            file_path = target_dir / filename
            file_path.write_text(content, encoding="utf-8")
            print(f"[OK] 已建立 {resource}/{filename}")
        else:
            print(f"[OK] 已建立目錄 {resource}/")


def build_skill_markdown(skill_name: str, resources: list[str]) -> str:
    """組裝初始 SKILL.md 內容（符合跨平台單行 description 與精簡規範）。"""
    skill_title = title_case_skill_name(skill_name)
    if resources:
        bullets = "\n".join(RESOURCE_DESCRIPTIONS[r] for r in resources)
        resources_section = RESOURCES_SECTION_TEMPLATE.format(resources_bullets=bullets)
    else:
        resources_section = ""
    return SKILL_TEMPLATE.format(
        skill_name=skill_name,
        skill_title=skill_title,
        resources_section=resources_section,
        todo=_TODO_TAG,
    )


def init_skill(
    skill_name: str,
    output_parent: Path,
    resources: list[str],
    include_examples: bool,
) -> Path | None:
    """建立新技能目錄與模板檔案，失敗時回傳 None。"""
    skill_dir = output_parent.resolve() / skill_name
    if skill_dir.exists():
        print(f"[ERROR] 目標技能目錄已存在：{skill_dir}")
        return None

    try:
        skill_dir.mkdir(parents=True, exist_ok=False)
        print(f"[OK] 已建立技能目錄：{skill_dir}")
        skill_md_path = skill_dir / "SKILL.md"
        skill_md_path.write_text(
            build_skill_markdown(skill_name, resources), encoding="utf-8"
        )
        print("[OK] 已建立 SKILL.md")
        if resources:
            create_resource_dirs(
                skill_dir, skill_name, title_case_skill_name(skill_name), resources, include_examples
            )
    except OSError as exc:
        print(f"[ERROR] 建立檔案時發生錯誤：{exc}")
        return None

    print(f"\n[DONE] 技能 '{skill_name}' 初始化完成：{skill_dir}")
    print("下一步：")
    print(f"1. 編輯 SKILL.md，將所有 [{_TODO_TAG} ...] 替換為具體單行 description 與步驟說明。")
    if resources:
        print("2. 實作或替換附帶資源，並刪去不需要的範例檔（切勿在技能內新增 README.md）。")
    print("3. 執行 quick_validate.py --strict 檢查跨平台格式與 TODO 殘留。")
    return skill_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="建立適用於 Antigravity、Claude Code、Codex、OpenCode 與 Gemini App 的標準技能骨架。"
    )
    parser.add_argument("skill_name", help="技能名稱（將自動正規化為小寫連字號格式）")
    parser.add_argument("--path", required=True, help="技能輸出的上層目錄路徑")
    parser.add_argument(
        "--resources",
        default="",
        help="要建立的資源子目錄，以逗號分隔：scripts,references,assets",
    )
    parser.add_argument(
        "--examples",
        action="store_true",
        help="在建立的資源目錄內放入範本檔案（需搭配 --resources）",
    )
    args = parser.parse_args()

    skill_name = normalize_skill_name(args.skill_name)
    if not skill_name:
        print("[ERROR] 技能名稱至少須包含一個英數字元。")
        return 1
    if len(skill_name) > MAX_SKILL_NAME_LENGTH:
        print(
            f"[ERROR] 技能名稱 '{skill_name}' 長度為 {len(skill_name)} 字元，"
            f"超過上限 {MAX_SKILL_NAME_LENGTH} 字元。"
        )
        return 1
    if skill_name != args.skill_name:
        print(f"[INFO] 技能名稱已正規化：'{args.skill_name}' -> '{skill_name}'")

    try:
        resources = parse_resources(args.resources)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    if args.examples and not resources:
        print("[ERROR] 使用 --examples 時必須同時指定 --resources。")
        return 1

    result = init_skill(skill_name, Path(args.path), resources, args.examples)
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())
