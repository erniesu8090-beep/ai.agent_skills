from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

TOP_METADATA_ALLOWLIST = {"accelerator", "colab", "kernelspec", "language_info"}
COLAB_METADATA_ALLOWLIST = {"provenance", "gpuType", "toc_visible"}
FORBIDDEN_CELL_META_KEYS = {"executionInfo", "outputId"}
GPU_CHOICES = ("L4", "A100", "G4", "T4")


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "_", lowered)
    collapsed = re.sub(r"_+", "_", cleaned).strip("_")
    return collapsed or "colab_trial"


def get_source_text(cell: dict[str, Any]) -> str:
    source = cell.get("source", [])
    if isinstance(source, str):
        return source
    if isinstance(source, list):
        return "".join(str(line) for line in source)
    return ""


def get_source_lines(cell: dict[str, Any]) -> list[str]:
    source = cell.get("source", [])
    if isinstance(source, str):
        return source.splitlines(keepends=True)
    if isinstance(source, list):
        return [str(line) for line in source]
    return []


def load_template(skill_dir: Path) -> dict[str, Any]:
    template_path = skill_dir / "assets" / "colab_notebook.ipynb"
    if not template_path.exists():
        raise SystemExit(f"找不到骨架範本：{template_path}")
    with template_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit(f"骨架格式錯誤（非 JSON 物件）：{template_path}")
    return data


def write_notebook(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def cmd_new(args: argparse.Namespace, skill_dir: Path) -> int:
    notebook = load_template(skill_dir)
    cells = notebook.get("cells")
    if not isinstance(cells, list) or not cells:
        raise SystemExit("骨架範本缺少 cells 陣列")

    first_cell = cells[0]
    if not isinstance(first_cell, dict) or first_cell.get("cell_type") != "markdown":
        raise SystemExit("骨架範本第 0 格必須為 markdown 說明格")

    lines = get_source_lines(first_cell)
    title_line = f"# 🧪 {args.title.strip()}\n"
    if lines:
        lines[0] = title_line
    else:
        lines = [title_line]
    first_cell["source"] = lines

    metadata = notebook.setdefault("metadata", {})
    if isinstance(metadata, dict):
        colab_meta = metadata.setdefault("colab", {})
        if isinstance(colab_meta, dict):
            colab_meta["gpuType"] = args.gpu

    if args.out is not None:
        out_path = args.out.resolve()
    else:
        out_path = (Path.cwd() / "colab" / f"{slugify(args.title)}.ipynb").resolve()

    if out_path.exists() and not args.force:
        print(f"[ERROR] 目標檔案已存在，若要覆寫請加上 --force：{out_path}", file=sys.stderr)
        return 1

    write_notebook(out_path, notebook)
    print(f"[OK] 已從骨架建立 Colab 筆記本：{out_path}（預設 GPU：{args.gpu}）")
    return 0


def extract_embedded_scripts(tree: ast.AST) -> list[tuple[str, str]]:
    """找出指定給 script 或 *_script 的多行字串常數，供二次語法檢查。"""
    found: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue
        text = node.value.value
        if "\n" not in text:
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and (
                target.id == "script" or target.id.endswith("_script")
            ):
                found.append((target.id, text))
    return found


def validate_single_notebook(nb_path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        raw = nb_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        return [f"JSON 解析失敗：{exc}"], []

    if not isinstance(data, dict):
        return ["頂層 JSON 必須是物件（dict）"], []

    if data.get("nbformat") != 4:
        warnings.append(f"nbformat 為 {data.get('nbformat')!r}，建議維持 4")

    cells = data.get("cells")
    if not isinstance(cells, list) or not cells:
        errors.append("缺少有效的 cells 陣列")
        return errors, warnings

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("缺少頂層 metadata 物件")
    else:
        extra_top = sorted(set(metadata.keys()) - TOP_METADATA_ALLOWLIST)
        if extra_top:
            if "executionInfo" in extra_top:
                errors.append("頂層 metadata 含有 executionInfo（含執行痕跡）")
            else:
                warnings.append(f"頂層 metadata 含白名單外欄位：{', '.join(extra_top)}")
        colab_meta = metadata.get("colab")
        if not isinstance(colab_meta, dict):
            warnings.append("metadata.colab 缺失，建議保留骨架設定")
        else:
            extra_colab = sorted(set(colab_meta.keys()) - COLAB_METADATA_ALLOWLIST)
            if extra_colab:
                warnings.append(f"metadata.colab 含白名單外欄位：{', '.join(extra_colab)}")
            if colab_meta.get("toc_visible") is not True:
                warnings.append("metadata.colab.toc_visible 未設為 true（左側目錄不會自動展開）")

    h1_count = 0
    for idx, cell in enumerate(cells):
        if not isinstance(cell, dict):
            errors.append(f"Cell[{idx}] 格式不是物件")
            continue

        cell_meta = cell.get("metadata")
        if isinstance(cell_meta, dict):
            hit_forbidden = sorted(set(cell_meta.keys()) & FORBIDDEN_CELL_META_KEYS)
            if hit_forbidden:
                errors.append(
                    f"Cell[{idx}] metadata 含執行痕跡／帳號欄位：{', '.join(hit_forbidden)}"
                )

        cell_type = cell.get("cell_type")
        text = get_source_text(cell)

        if cell_type == "markdown":
            for line in text.splitlines():
                if re.match(r"^#\s+\S", line):
                    h1_count += 1
                    if idx != 0:
                        warnings.append(
                            f"Cell[{idx}] 使用了一級標題（#），建議改用 ## 或 ### 以維持左側目錄階層"
                        )
        elif cell_type == "code":
            if cell.get("execution_count") is not None:
                errors.append(f"Cell[{idx}] execution_count 未清除（應為 null）")
            outputs = cell.get("outputs")
            if outputs != []:
                errors.append(f"Cell[{idx}] outputs 未清空（應為 []）")

            first_line = text.splitlines()[0] if text.splitlines() else ""
            if "# @title" not in first_line or 'display-mode: "form"' not in first_line:
                warnings.append(
                    f'Cell[{idx}] 首行缺少標準 Colab 摺疊標題（# @title ... {{ display-mode: "form" }}）'
                )

            try:
                tree = ast.parse(text, filename=f"{nb_path.name}#cell[{idx}]")
            except SyntaxError as exc:
                errors.append(
                    f"Cell[{idx}] Python 語法錯誤（第 {exc.lineno} 行）：{exc.msg}"
                )
                continue

            for var_name, embedded in extract_embedded_scripts(tree):
                try:
                    ast.parse(embedded, filename=f"{nb_path.name}#cell[{idx}]:{var_name}")
                except SyntaxError as exc:
                    errors.append(
                        f"Cell[{idx}] 內嵌字串 {var_name} Python 語法錯誤（第 {exc.lineno} 行）：{exc.msg}"
                    )
        else:
            warnings.append(f"Cell[{idx}] 類型為 {cell_type!r}，非 markdown/code")

    if h1_count == 0:
        warnings.append("整份筆記本缺少一級標題（# ）")
    elif h1_count > 1:
        warnings.append(f"整份筆記本共有 {h1_count} 個一級標題（# ），建議僅第 0 格使用 1 個")

    return errors, warnings


def collect_notebooks(targets: list[Path]) -> list[Path]:
    notebooks: list[Path] = []
    for target in targets:
        resolved = target.resolve()
        if not resolved.exists():
            raise SystemExit(f"找不到指定路徑：{target}")
        if resolved.is_dir():
            notebooks.extend(sorted(resolved.rglob("*.ipynb")))
        else:
            notebooks.append(resolved)
    return notebooks


def cmd_validate(args: argparse.Namespace) -> int:
    notebooks = collect_notebooks(args.targets)
    if not notebooks:
        print("[WARN] 未找到任何 .ipynb 檔案。")
        return 1 if args.strict else 0

    failed = 0
    warned = 0
    for nb in notebooks:
        errors, warnings = validate_single_notebook(nb)
        if errors:
            failed += 1
            print(f"[FAIL] {nb}")
        elif warnings:
            warned += 1
            status = "FAIL(strict)" if args.strict else "WARN"
            print(f"[{status}] {nb}")
        else:
            print(f"[PASS] {nb}")

        for err in errors:
            print(f"  - ERROR: {err}")
        for warn in warnings:
            print(f"  - WARN : {warn}")

    total = len(notebooks)
    passed = total - failed - warned
    print(f"\n驗證完成：共 {total} 份｜通過 {passed}｜警告 {warned}｜失敗 {failed}")
    if failed > 0 or (args.strict and warned > 0):
        return 1
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    target = args.target.resolve()
    if not target.exists():
        print(f"[ERROR] 找不到檔案：{target}", file=sys.stderr)
        return 1
    if not args.in_place and args.out is None:
        print("[ERROR] 請指定 --in-place 或 --out <輸出路徑>。", file=sys.stderr)
        return 1

    with target.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict) or not isinstance(data.get("cells"), list):
        print(f"[ERROR] 檔案不是有效的 .ipynb 結構：{target}", file=sys.stderr)
        return 1

    for cell in data["cells"]:
        if not isinstance(cell, dict):
            continue
        cell["metadata"] = {}
        if cell.get("cell_type") == "code":
            cell["execution_count"] = None
            cell["outputs"] = []

    raw_meta = data.get("metadata")
    if isinstance(raw_meta, dict):
        cleaned_meta: dict[str, Any] = {}
        for key in ("accelerator", "colab", "kernelspec", "language_info"):
            if key not in raw_meta:
                continue
            if key == "colab" and isinstance(raw_meta[key], dict):
                cleaned_colab = {
                    ck: cv
                    for ck, cv in raw_meta[key].items()
                    if ck in COLAB_METADATA_ALLOWLIST
                }
                cleaned_meta["colab"] = cleaned_colab
            else:
                cleaned_meta[key] = raw_meta[key]
        data["metadata"] = cleaned_meta

    dest = target if args.in_place else args.out.resolve()
    write_notebook(dest, data)
    print(f"[OK] 已清除輸出與執行痕跡並儲存至：{dest}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Google Colab GPU 筆記本建檔、清理與驗證工具"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="從標準骨架建立新的 Colab 筆記本")
    p_new.add_argument("--title", required=True, help="筆記本標題（如：pdf2epub：版面模型試跑）")
    p_new.add_argument("--out", type=Path, default=None, help="輸出 .ipynb 路徑")
    p_new.add_argument(
        "--gpu",
        choices=GPU_CHOICES,
        default="L4",
        help="預設 Colab GPU 型號（預設：L4）",
    )
    p_new.add_argument("--force", action="store_true", help="允許覆寫已存在的檔案")

    p_val = sub.add_parser("validate", help="驗證 .ipynb 格式、Python 語法與乾淨度")
    p_val.add_argument("targets", nargs="+", type=Path, help=".ipynb 檔案或資料夾路徑")
    p_val.add_argument("--strict", action="store_true", help="將警告也視為驗證失敗")

    p_clean = sub.add_parser("clean", help="清除 .ipynb 輸出、execution_count 與 executionInfo")
    p_clean.add_argument("target", type=Path, help="要清理的 .ipynb 檔案路徑")
    p_clean.add_argument("--in-place", action="store_true", help="直接覆寫原檔案")
    p_clean.add_argument("--out", type=Path, default=None, help="另存為新檔案路徑")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    skill_dir = Path(__file__).resolve().parents[1]

    if args.command == "new":
        return cmd_new(args, skill_dir)
    if args.command == "validate":
        return cmd_validate(args)
    if args.command == "clean":
        return cmd_clean(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
