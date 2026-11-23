#!/usr/bin/env python3
"""去 AI 味（Anti-AI-Slop）前端靜態品質閘門檢查腳本。

借鏡 Nutlope/hallmark 之 Floor / Reflex 分級檢查理念與本專案全域美學規範，
僅使用 Python 3 標準函式庫對 HTML / CSS 檔案執行靜態掃描，無須安裝 Node.js 或瀏覽器即可運作。

檢查分級：
- FLOOR（零容忍底線）：無障礙焦點、減少動態支援、viewport 設定、禁止 transition: all、禁止佔位假文案
- REFLEX（AI 套版習慣警訊）：紫藍漸層、科技深藍/全頁純白底、過度大圓角、Emoji 當圖示、全大寫眉標、中點標籤、空連結
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

TARGET_EXTS = {".html", ".htm", ".css"}

# Floor 規則檢查樣式
TRANSITION_ALL_RE = re.compile(r"\btransition\s*:\s*all\b", re.IGNORECASE)
HAS_ANIMATION_RE = re.compile(
    r"(?:@keyframes\b|\banimation\s*:|\btransition\s*:|\btransition-(?:property|duration)\b|"
    r"\banimate-(?:pulse|bounce|ping|spin)\b)",
    re.IGNORECASE,
)
REDUCED_MOTION_RE = re.compile(
    r"(?:prefers-reduced-motion|motion-reduce:|motion-safe:)",
    re.IGNORECASE,
)
INTERACTIVE_TAG_RE = re.compile(
    r"<(?:button|a\b|input\b|select\b|textarea\b)[^>]*>",
    re.IGNORECASE,
)
FOCUS_VISIBLE_RE = re.compile(
    r"(?::focus-visible\b|focus-visible:)",
    re.IGNORECASE,
)
HTML_DOC_RE = re.compile(r"<!doctype\s+html|<html\b", re.IGNORECASE)
VIEWPORT_META_RE = re.compile(
    r"""<meta[^>]+name\s*=\s*["']viewport["'][^>]*>""",
    re.IGNORECASE,
)
FAKE_COPY_RE = re.compile(
    r"\b(?:lorem\s+ipsum|dolor\s+sit\s+amet|acme\s+corp|john\s+doe|jane\s+doe|placeholder\.com)\b",
    re.IGNORECASE,
)

# Reflex 規則檢查樣式
TAILWIND_PURPLE_BLUE_RE = re.compile(
    r"(?:from-(?:indigo|purple|violet)-[3-8]00\b[^\"'>]*\bto-(?:blue|sky|pink|purple|indigo)-[3-8]00\b|"
    r"from-(?:blue|sky)-[3-8]00\b[^\"'>]*\bto-(?:purple|violet|indigo)-[3-8]00\b|"
    r"bg-gradient-to-[trbl]{1,2}\s+from-(?:indigo|purple|violet)-)",
    re.IGNORECASE,
)
CSS_PURPLE_BLUE_GRADIENT_RE = re.compile(
    r"linear-gradient\([^)]*(?:#6366f1|#8b5cf6|#a855f7|#7c3aed|#4f46e5)[^)]*(?:#3b82f6|#2563eb|#06b6d4|#ec4899|#a855f7)",
    re.IGNORECASE,
)
TECH_SLATE_DARK_RE = re.compile(
    r"(?:#0f172a\b|bg-slate-900\b|bg-slate-950\b)",
    re.IGNORECASE,
)
PURE_WHITE_BG_RE = re.compile(
    r"(?:background(?:-color)?\s*:\s*(?:#fff(?:fff)?\b|white\b)|<body[^>]*class=[\"'][^\"']*\bbg-white\b)",
    re.IGNORECASE,
)
HEAVY_ROUNDED_RE = re.compile(
    r"(?:\brounded-3xl\b|\brounded-2xl\b|border-radius\s*:\s*(?:2[4-9]|[3-9]\d)px)",
    re.IGNORECASE,
)
EMOJI_UI_RE = re.compile(
    r"<(?:h[1-6]|button|a|nav|th|label|span)[^>]*>[^<]*[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u27BF][^<]*</",
)
EYEBROW_ALLCAPS_RE = re.compile(
    r"""class\s*=\s*["'][^"']*(?=[^"']*\buppercase\b)(?=[^"']*\btracking-(?:wider|widest)\b)[^"']*["'][^>]*>[^<]{2,40}</(?:span|p|div)>\s*<h[1-3]\b""",
    re.IGNORECASE,
)
MIDDLE_DOT_META_RE = re.compile(
    r">[^<]{1,40}\s·\s[^<]{1,40}(?:\s·\s[^<]{1,40})?<",
)
DEAD_LINK_RE = re.compile(
    r"""<a\b[^>]*\bhref\s*=\s*["']\s*#?\s*["']""",
    re.IGNORECASE,
)


@dataclass
class Finding:
    """單一檢查發現項。"""

    level: str  # "FLOOR" 或 "REFLEX"
    rule: str
    line: int
    message: str
    snippet: str = ""


@dataclass
class FileReport:
    """單一檔案的掃描報告。"""

    path: str
    floor_count: int = 0
    reflex_count: int = 0
    findings: list[Finding] = field(default_factory=list)


def _line_of(text: str, pos: int) -> int:
    """由字元位移計算 1-based 行號。"""
    return text.count("\n", 0, pos) + 1


def _snippet_at(lines: list[str], line_no: int) -> str:
    """擷取指定行號的精簡預覽片段。"""
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()[:120]
    return ""


def _add_matches(
    findings: list[Finding],
    text: str,
    lines: list[str],
    pattern: re.Pattern[str],
    level: str,
    rule: str,
    message: str,
    limit: int = 5,
) -> None:
    """依正規表示式批次回報符合項，避免單檔洗版。"""
    for idx, match in enumerate(pattern.finditer(text)):
        if idx >= limit:
            break
        line_no = _line_of(text, match.start())
        findings.append(
            Finding(
                level=level,
                rule=rule,
                line=line_no,
                message=message,
                snippet=_snippet_at(lines, line_no),
            )
        )


def lint_content(content: str, suffix: str) -> list[Finding]:
    """對單一 HTML 或 CSS 文字內容執行 Floor 與 Reflex 檢查。"""
    findings: list[Finding] = []
    lines = content.splitlines()
    is_html = suffix.lower() in {".html", ".htm"}

    # --- FLOOR（零容忍底線）---
    _add_matches(
        findings,
        content,
        lines,
        TRANSITION_ALL_RE,
        "FLOOR",
        "no-transition-all",
        "禁用 transition: all，請改為明確列出屬性（例如 opacity, transform）。",
    )

    _add_matches(
        findings,
        content,
        lines,
        FAKE_COPY_RE,
        "FLOOR",
        "no-fake-placeholder-copy",
        "偵測到未替換的佔位假文案（如 Lorem ipsum / Acme Corp），請改為真實業務內容。",
    )

    if is_html and HTML_DOC_RE.search(content) and not VIEWPORT_META_RE.search(content):
        findings.append(
            Finding(
                level="FLOOR",
                rule="viewport-meta-required",
                line=1,
                message="完整 HTML 文件缺少 <meta name=\"viewport\" ...>，手機版可能強制縮放或破版。",
            )
        )

    if is_html and INTERACTIVE_TAG_RE.search(content) and not FOCUS_VISIBLE_RE.search(content):
        findings.append(
            Finding(
                level="FLOOR",
                rule="focus-visible-required",
                line=1,
                message="頁面含互動元件（button/a/input），但未發現 :focus-visible 或 focus-visible: 鍵盤焦點樣式。",
            )
        )

    if HAS_ANIMATION_RE.search(content) and not REDUCED_MOTION_RE.search(content):
        findings.append(
            Finding(
                level="FLOOR",
                rule="reduced-motion-required",
                line=1,
                message="偵測到轉場或動畫設定，但缺少 prefers-reduced-motion / motion-reduce 降動態保護。",
            )
        )

    # --- REFLEX（AI 套版常見破綻）---
    _add_matches(
        findings,
        content,
        lines,
        TAILWIND_PURPLE_BLUE_RE,
        "REFLEX",
        "ai-purple-gradient",
        "偵測到常見 AI 紫藍漸層 Tailwind 類別，請改採主題規範色系或實色表面。",
    )
    _add_matches(
        findings,
        content,
        lines,
        CSS_PURPLE_BLUE_GRADIENT_RE,
        "REFLEX",
        "ai-purple-gradient",
        "偵測到常見 AI 紫藍 linear-gradient 漸層，請確認是否為刻意設計選擇。",
    )
    _add_matches(
        findings,
        content,
        lines,
        TECH_SLATE_DARK_RE,
        "REFLEX",
        "ai-default-slate-dark",
        "偵測到預設科技深藍（#0F172A / slate-900）；依去 AI 味規範建議改用石墨深炭灰（#1E2022）或主題指定色。",
    )
    _add_matches(
        findings,
        content,
        lines,
        PURE_WHITE_BG_RE,
        "REFLEX",
        "pure-white-surface",
        "偵測到純白背景（#FFFFFF / bg-white）；高資訊密度介面建議改用暖米白（#FAF7F2 / #F6F4EE）降低刺眼感。",
    )

    rounded_matches = list(HEAVY_ROUNDED_RE.finditer(content))
    if len(rounded_matches) >= 3:
        first_line = _line_of(content, rounded_matches[0].start())
        findings.append(
            Finding(
                level="REFLEX",
                rule="excessive-rounded-corners",
                line=first_line,
                message=f"偵測到 {len(rounded_matches)} 處大圓角（rounded-2xl/3xl 或 >=24px），建議改採克制圓角（rounded-md）。",
                snippet=_snippet_at(lines, first_line),
            )
        )

    if is_html:
        _add_matches(
            findings,
            content,
            lines,
            EMOJI_UI_RE,
            "REFLEX",
            "emoji-as-ui-icon",
            "在標題、按鈕或導覽元素內偵測到 Emoji，建議改為克制 SVG 圖示或純文字。",
        )
        _add_matches(
            findings,
            content,
            lines,
            EYEBROW_ALLCAPS_RE,
            "REFLEX",
            "eyebrow-all-caps",
            "偵測到標題上方的高字距全大寫眉標（ALL-CAPS eyebrow），此為常見 AI 套版破綻。",
        )
        _add_matches(
            findings,
            content,
            lines,
            MIDDLE_DOT_META_RE,
            "REFLEX",
            "middle-dot-meta",
            "偵測到使用中點（·）串接的標籤字串，建議改用結構化欄位或清晰間距。",
        )
        _add_matches(
            findings,
            content,
            lines,
            DEAD_LINK_RE,
            "REFLEX",
            "dead-placeholder-link",
            "偵測到 href=\"#\" 或空 href 假連結，請補齊真實目標或改為語意化 button。",
        )

    return findings


def collect_targets(target: Path) -> list[Path]:
    """收集要掃描的 HTML / CSS 檔案清單。"""
    if target.is_file():
        return [target]
    if target.is_dir():
        files = [
            p
            for p in sorted(target.rglob("*"))
            if p.is_file()
            and p.suffix.lower() in TARGET_EXTS
            and "node_modules" not in p.parts
            and ".venv" not in p.parts
        ]
        return files
    return []


def scan_path(target: Path) -> list[FileReport]:
    """掃描指定路徑並回傳各檔案報告。"""
    reports: list[FileReport] = []
    for file_path in collect_targets(target):
        content = file_path.read_text(encoding="utf-8", errors="replace")
        findings = lint_content(content, file_path.suffix)
        floor_count = sum(1 for item in findings if item.level == "FLOOR")
        reflex_count = sum(1 for item in findings if item.level == "REFLEX")
        reports.append(
            FileReport(
                path=str(file_path),
                floor_count=floor_count,
                reflex_count=reflex_count,
                findings=findings,
            )
        )
    return reports


def print_human_report(reports: list[FileReport]) -> None:
    """以繁體中文易讀格式輸出掃描報告。"""
    total_floor = sum(r.floor_count for r in reports)
    total_reflex = sum(r.reflex_count for r in reports)
    print(f"[slop_lint] 已掃描 {len(reports)} 個檔案 | FLOOR 違規: {total_floor} | REFLEX 警訊: {total_reflex}")

    for report in reports:
        if not report.findings:
            print(f"  [PASS] {report.path}")
            continue
        print(f"  [WARN] {report.path} (FLOOR={report.floor_count}, REFLEX={report.reflex_count})")
        for item in report.findings:
            snippet_info = f" -> `{item.snippet}`" if item.snippet else ""
            print(f"    - [{item.level}] L{item.line} ({item.rule}): {item.message}{snippet_info}")


def main() -> int:
    """CLI 主進入點。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="去 AI 味（Anti-AI-Slop）前端靜態品質閘門檢查腳本（純 Python 3 標準庫）。"
    )
    parser.add_argument("target", help="目標 HTML/CSS 檔案或專案目錄路徑")
    parser.add_argument("--json", action="store_true", help="改以 JSON 格式輸出結果")
    parser.add_argument(
        "--strict-reflex",
        action="store_true",
        help="將 REFLEX 警訊亦視為失敗（exit code 1）；預設僅 FLOOR 違規導致失敗",
    )
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"[ERROR] 找不到目標路徑：{target}", file=sys.stderr)
        return 2

    reports = scan_path(target)
    if not reports:
        print(f"[WARN] 在 {target} 未找到可掃描的 .html / .htm / .css 檔案。")
        return 0

    total_floor = sum(r.floor_count for r in reports)
    total_reflex = sum(r.reflex_count for r in reports)

    if args.json:
        payload = {
            "scanned_files": len(reports),
            "total_floor": total_floor,
            "total_reflex": total_reflex,
            "reports": [
                {
                    "path": r.path,
                    "floor_count": r.floor_count,
                    "reflex_count": r.reflex_count,
                    "findings": [asdict(f) for f in r.findings],
                }
                for r in reports
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_human_report(reports)

    if total_floor > 0:
        return 1
    if args.strict_reflex and total_reflex > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
