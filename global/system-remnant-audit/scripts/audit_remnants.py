#!/usr/bin/env python3
"""Read-only system remnant auditor for AI coding agents and Windows Jump Lists.

Scans user-level AI agent directories (.gemini, .claude, .codex, .config/opencode),
AppData folders, and Windows Jump Lists (AutomaticDestinations / CustomDestinations)
to report stale caches, backup folders, .bak files, and orphaned Jump List entries.

Strictly read-only: never modifies, moves, or deletes any file or registry entry,
and never reads contents of credential, auth, or permission-restricted config files.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Jump List keyword matching to surface AI-agent-related taskbar caches
AGENT_KEYWORDS = (
    "antigravity",
    "claude",
    "codex",
    "opencode",
    "gemini",
)

# Directory/file name hints that commonly represent stale backups or old updaters
STALE_NAME_HINTS = (
    "backup",
    "ide",
    "browser-profile",
    "updater",
    "cached",
    "old",
    "tmp",
    "temp",
)

# Subpaths inside %APPDATA%\Antigravity known to be legacy VS Code fork artifacts
LEGACY_ANTIGRAVITY_NAMES = {
    "User",
    "Backups",
    "CachedConfigurations",
    "CachedData",
    "CachedExtensionVSIXs",
    "CachedProfilesData",
    "clp",
    "bin",
    "languagepacks.json",
    ".updaterId",
}

WIN_PATH_RE = re.compile(r"[A-Za-z]:\\(?:[^<>:\"/\\|?*\x00-\x1f]+\\)*[^<>:\"/\\|?*\x00-\x1f]*")


def format_dt(ts: float) -> str:
    """Format a POSIX timestamp as YYYY-MM-DD HH:MM:SS."""
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def dir_metrics(path: Path) -> tuple[int, int, float]:
    """Return (file_count, total_bytes, max_mtime) recursively without reading file contents."""
    newest = path.stat().st_mtime
    count = 0
    total_bytes = 0
    if path.is_file():
        return 1, path.stat().st_size, newest

    stack = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        st = entry.stat(follow_symlinks=False)
                        if st.st_mtime > newest:
                            newest = st.st_mtime
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        else:
                            count += 1
                            total_bytes += st.st_size
                    except OSError:
                        continue
        except OSError:
            continue
    return count, total_bytes, newest


def to_mb(size_bytes: int) -> float:
    """Convert bytes to megabytes rounded to 2 decimals."""
    return round(size_bytes / (1024 * 1024), 2)


def is_stale_candidate(
    name: str,
    age_days: float,
    size_bytes: int,
    file_count: int,
    stale_days: int,
    min_mb: float,
) -> tuple[bool, str]:
    """Decide whether an item looks like a historical remnant and explain why."""
    lower = name.lower()
    reasons: list[str] = []

    if age_days >= stale_days:
        reasons.append(f"超過 {stale_days} 天未更新（約 {int(age_days)} 天）")
    if any(hint in lower for hint in STALE_NAME_HINTS) and age_days >= 14:
        reasons.append("名稱含備份／舊版／快取特徵且已逾 14 天未變動")
    if file_count == 0 and size_bytes == 0 and age_days >= 7:
        reasons.append("空資料夾且逾 7 天未變動")

    # Require either stale age or explicit legacy hint + non-trivial age
    if age_days >= stale_days and (
        to_mb(size_bytes) >= min_mb
        or any(hint in lower for hint in STALE_NAME_HINTS)
        or name in LEGACY_ANTIGRAVITY_NAMES
        or file_count == 0
    ):
        return True, "；".join(reasons)
    if len(reasons) >= 2:
        return True, "；".join(reasons)
    return False, ""


def scan_top_level_children(
    root: Path,
    now_ts: float,
    stale_days: int,
    min_mb: float,
    bak_patterns: tuple[str, ...] = ("*.bak",),
) -> dict[str, Any]:
    """Inspect top-level children of a directory and collect .bak files."""
    if not root.exists():
        return {"exists": False, "path": str(root)}

    items: list[dict[str, Any]] = []
    bak_files: list[dict[str, Any]] = []
    total_bytes = 0

    try:
        entries = sorted(root.iterdir(), key=lambda p: p.name.lower())
    except OSError as exc:
        return {"exists": True, "path": str(root), "error": str(exc)}

    for entry in entries:
        try:
            count, sz, max_mt = dir_metrics(entry)
        except OSError:
            continue
        total_bytes += sz
        age_days = max(0.0, (now_ts - max_mt) / 86400.0)
        flagged, reason = is_stale_candidate(
            entry.name, age_days, sz, count, stale_days, min_mb
        )
        record = {
            "name": entry.name,
            "path": str(entry),
            "is_dir": entry.is_dir(),
            "files": count,
            "size_bytes": sz,
            "size_mb": to_mb(sz),
            "max_mtime": format_dt(max_mt),
            "age_days": round(age_days, 1),
            "stale_candidate": flagged,
            "reason": reason,
        }
        items.append(record)

    for pattern in bak_patterns:
        for bak in root.glob(pattern):
            if bak.is_file():
                try:
                    st = bak.stat()
                    bak_files.append(
                        {
                            "path": str(bak),
                            "size_bytes": st.st_size,
                            "mtime": format_dt(st.st_mtime),
                            "age_days": round(max(0.0, (now_ts - st.st_mtime) / 86400.0), 1),
                        }
                    )
                except OSError:
                    continue

    # Sort largest first for quick triage
    items.sort(key=lambda x: x["size_bytes"], reverse=True)
    return {
        "exists": True,
        "path": str(root),
        "total_mb": to_mb(total_bytes),
        "items": items,
        "bak_files": bak_files,
    }


def extract_utf16le_strings(raw: bytes, min_len: int = 5) -> list[str]:
    """Extract printable ASCII/CJK UTF-16LE strings from binary Windows files."""
    results: list[str] = []
    for offset in (0, 1):
        i = offset
        buf: list[str] = []
        while i + 1 < len(raw):
            ch = int.from_bytes(raw[i : i + 2], "little")
            if (0x20 <= ch <= 0x7E) or (0x4E00 <= ch <= 0x9FFF) or ch in (0x3000, 0xFF0C):
                buf.append(chr(ch))
            else:
                if len(buf) >= min_len:
                    results.append("".join(buf))
                buf = []
            i += 2
        if len(buf) >= min_len:
            results.append("".join(buf))
    return results


def audit_windows_jumplists(
    appdata: Path, now_ts: float, stale_days: int, include_all_jumplists: bool = False
) -> dict[str, Any]:
    """Read-only inspection of Windows Jump Lists and TaskBar/StartMenu AI shortcuts."""
    recent_dir = appdata / "Microsoft" / "Windows" / "Recent"
    jump_items: list[dict[str, Any]] = []

    for sub in ("AutomaticDestinations", "CustomDestinations"):
        folder = recent_dir / sub
        if not folder.exists():
            continue
        try:
            files = sorted(folder.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        except OSError:
            continue

        for fp in files:
            if not fp.is_file():
                continue
            try:
                st = fp.stat()
                raw = fp.read_bytes()
            except OSError:
                continue

            age_days = max(0.0, (now_ts - st.st_mtime) / 86400.0)
            strings = extract_utf16le_strings(raw)
            joined_lower = "\n".join(strings).lower()

            # Match AI tool binaries/profiles rather than arbitrary project subfolders
            matched_agents = [
                kw
                for kw in AGENT_KEYWORDS
                if any(
                    marker in joined_lower
                    for marker in (
                        f"{kw}.exe",
                        f"\\{kw}\\",
                        f".{kw}",
                        f"{kw}-",
                        f"com.google.{kw}",
                        f"google.{kw}",
                    )
                )
            ]
            if not matched_agents and not (include_all_jumplists and age_days >= stale_days):
                continue

            referenced_paths: list[dict[str, Any]] = []
            seen_paths: set[str] = set()
            for s in strings:
                for match in WIN_PATH_RE.findall(s):
                    clean = match.rstrip(" \t\r\n")
                    if len(clean) < 5 or clean in seen_paths:
                        continue
                    seen_paths.add(clean)
                    # Check existence only when path looks complete (no ~1 shortname truncation)
                    exists_flag: bool | None = None
                    if "~" not in clean:
                        try:
                            exists_flag = Path(clean).exists()
                        except OSError:
                            exists_flag = None
                    referenced_paths.append({"path": clean, "exists": exists_flag})

            missing_count = sum(1 for r in referenced_paths if r["exists"] is False)
            # Only flag as stale when the Jump List itself has gone stale_days without updates
            is_stale = age_days >= stale_days

            jump_items.append(
                {
                    "category": sub,
                    "file": fp.name,
                    "path": str(fp),
                    "size_bytes": st.st_size,
                    "mtime": format_dt(st.st_mtime),
                    "age_days": round(age_days, 1),
                    "matched_agents": matched_agents,
                    "sample_paths": referenced_paths[:10],
                    "missing_target_count": missing_count,
                    "stale_candidate": bool(is_stale),
                }
            )

    shortcuts: list[dict[str, Any]] = []
    shortcut_roots = [
        appdata / "Microsoft" / "Internet Explorer" / "Quick Launch" / "User Pinned" / "TaskBar",
        appdata / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    ]
    for sroot in shortcut_roots:
        if not sroot.exists():
            continue
        for lnk in sroot.rglob("*.lnk"):
            lower = lnk.name.lower()
            if not any(kw in lower for kw in AGENT_KEYWORDS):
                continue
            try:
                st = lnk.stat()
                raw = lnk.read_bytes()
                ascii_u16 = [
                    s for s in extract_utf16le_strings(raw, min_len=4)
                    if any(k in s.lower() for k in ("antigravity", "claude", "codex", "opencode", ".exe"))
                ]
                shortcuts.append(
                    {
                        "path": str(lnk),
                        "mtime": format_dt(st.st_mtime),
                        "hints": ascii_u16[:6],
                    }
                )
            except OSError:
                continue

    return {"jump_lists": jump_items, "shortcuts": shortcuts}


def audit_windows_local_appdata(
    localappdata: Path, now_ts: float, stale_days: int, min_mb: float
) -> list[dict[str, Any]]:
    """Find AI-agent-related directories in %LOCALAPPDATA%."""
    if not localappdata.exists():
        return []
    results: list[dict[str, Any]] = []
    try:
        entries = sorted(localappdata.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return []

    for entry in entries:
        lower = entry.name.lower()
        if not any(kw in lower for kw in AGENT_KEYWORDS):
            continue
        try:
            count, sz, max_mt = dir_metrics(entry)
        except OSError:
            continue
        age_days = max(0.0, (now_ts - max_mt) / 86400.0)
        flagged, reason = is_stale_candidate(
            entry.name, age_days, sz, count, stale_days, min_mb
        )
        results.append(
            {
                "name": entry.name,
                "path": str(entry),
                "files": count,
                "size_mb": to_mb(sz),
                "max_mtime": format_dt(max_mt),
                "age_days": round(age_days, 1),
                "stale_candidate": flagged,
                "reason": reason,
            }
        )
    return results


def run_audit(
    stale_days: int = 60, min_mb: float = 5.0, include_all_jumplists: bool = False
) -> dict[str, Any]:
    """Run full read-only audit and return structured findings."""
    now_ts = datetime.datetime.now().timestamp()
    home = Path.home()

    agent_homes = {
        "gemini": scan_top_level_children(
            home / ".gemini", now_ts, stale_days, min_mb, ("*.bak", "*.backup")
        ),
        "claude": scan_top_level_children(
            home / ".claude", now_ts, stale_days, min_mb, ("*.bak", "*.backup")
        ),
        "codex": scan_top_level_children(
            home / ".codex", now_ts, stale_days, min_mb, ("*.bak", "*.backup")
        ),
        "opencode": scan_top_level_children(
            home / ".config" / "opencode", now_ts, stale_days, min_mb, ("*.bak", "*.backup")
        ),
    }

    windows_data: dict[str, Any] = {"enabled": sys.platform == "win32"}
    if sys.platform == "win32":
        appdata_env = os.environ.get("APPDATA")
        local_env = os.environ.get("LOCALAPPDATA")
        if appdata_env:
            appdata = Path(appdata_env)
            windows_data["roaming_antigravity"] = scan_top_level_children(
                appdata / "Antigravity", now_ts, stale_days, min_mb
            )
            windows_data["jumplists"] = audit_windows_jumplists(
                appdata, now_ts, stale_days, include_all_jumplists=include_all_jumplists
            )
        if local_env:
            windows_data["local_appdata_agents"] = audit_windows_local_appdata(
                Path(local_env), now_ts, stale_days, min_mb
            )

    return {
        "audited_at": format_dt(now_ts),
        "platform": sys.platform,
        "params": {"stale_days": stale_days, "min_mb": min_mb},
        "agent_homes": agent_homes,
        "windows": windows_data,
    }


def render_report(report: dict[str, Any]) -> str:
    """Render a human-readable Traditional Chinese audit report."""
    lines: list[str] = []
    lines.append(f"# 系統歷史殘骸唯讀健檢報告 ({report['audited_at']})")
    lines.append(
        f"- 判定門檻：超過 {report['params']['stale_days']} 天未更新 / 單項 >= {report['params']['min_mb']} MB"
    )
    lines.append("- 模式：100% 唯讀盤點（未修改或刪除任何檔案）\n")

    candidates: list[tuple[str, float, str, str]] = []

    lines.append("## 1. 四家 AI Agent 家目錄盤點")
    for label, info in report["agent_homes"].items():
        if not info.get("exists"):
            lines.append(f"- `{label}`：目錄不存在（{info['path']}）")
            continue
        lines.append(f"- **`{label}`** (`{info['path']}`，總計 {info.get('total_mb', 0)} MB)")
        for item in info.get("items", []):
            tag = " [疑似殘骸]" if item["stale_candidate"] else ""
            if item["size_mb"] >= 1.0 or item["stale_candidate"]:
                lines.append(
                    f"  - `{item['name']}` | {item['size_mb']} MB | {item['files']} 檔 | 最新更新 `{item['max_mtime']}`{tag}"
                )
            if item["stale_candidate"]:
                candidates.append(
                    (item["path"], item["size_mb"], item["max_mtime"], item["reason"])
                )
        baks = info.get("bak_files", [])
        if baks:
            bak_mb = to_mb(sum(b["size_bytes"] for b in baks))
            lines.append(f"  - 規則/設定備份檔（`.bak`）：共 {len(baks)} 檔（{bak_mb} MB）")
            for b in baks:
                candidates.append((b["path"], to_mb(b["size_bytes"]), b["mtime"], "自動產生的 .bak 歷史備份"))

    win = report.get("windows", {})
    if win.get("enabled"):
        lines.append("\n## 2. Windows AppData 與安裝暫存")
        roaming = win.get("roaming_antigravity", {})
        if roaming.get("exists"):
            lines.append(
                f"- **Roaming Antigravity** (`{roaming['path']}`，總計 {roaming.get('total_mb', 0)} MB)"
            )
            stale_roaming = [i for i in roaming.get("items", []) if i["stale_candidate"]]
            active_roaming = [i for i in roaming.get("items", []) if not i["stale_candidate"] and i["size_mb"] >= 1.0]
            for item in stale_roaming:
                lines.append(
                    f"  - [疑似舊版殘骸] `{item['name']}` | {item['size_mb']} MB | 最新更新 `{item['max_mtime']}` | {item['reason']}"
                )
                candidates.append(
                    (item["path"], item["size_mb"], item["max_mtime"], item["reason"])
                )
            if active_roaming:
                active_names = ", ".join(f"{i['name']} ({i['size_mb']} MB)" for i in active_roaming[:8])
                lines.append(f"  - 現役活躍項目（勿動）：{active_names}")

        for item in win.get("local_appdata_agents", []):
            tag = " [疑似殘骸]" if item["stale_candidate"] else " [現役]"
            lines.append(
                f"- **LocalAppData** `{item['name']}` | {item['size_mb']} MB | {item['files']} 檔 | 最新更新 `{item['max_mtime']}`{tag}"
            )
            if item["stale_candidate"]:
                candidates.append(
                    (item["path"], item["size_mb"], item["max_mtime"], item["reason"])
                )

        jl = win.get("jumplists", {})
        lines.append("\n## 3. Windows 工作列跳轉清單（Jump Lists）")
        jump_entries = jl.get("jump_lists", [])
        if not jump_entries:
            lines.append("- 未發現與 AI 工具相關的陳舊或異常跳轉清單。")
        for j in jump_entries:
            agents = ",".join(j["matched_agents"]) or "無特定關鍵字(僅因久未更新列出)"
            tag = " [疑似殘骸]" if j["stale_candidate"] else ""
            lines.append(
                f"- `{j['category']}\\{j['file']}` | 關聯 `{agents}` | 更新 `{j['mtime']}` | 遺失目標數 {j['missing_target_count']}{tag}"
            )
            for sp in j["sample_paths"][:4]:
                mark = " (目標已不存在)" if sp["exists"] is False else ""
                lines.append(f"  - 紀錄路徑：`{sp['path']}`{mark}")
            if j["stale_candidate"]:
                reason = f"跳轉清單含 {j['missing_target_count']} 筆已消失路徑或逾 {report['params']['stale_days']} 天未更新"
                candidates.append((j["path"], to_mb(j["size_bytes"]), j["mtime"], reason))

        if jl.get("shortcuts"):
            lines.append("- 相關捷徑檔：")
            for sc in jl["shortcuts"]:
                lines.append(f"  - `{sc['path']}` (更新 `{sc['mtime']}`)")

    lines.append("\n## 4. 疑似歷史殘骸彙整（僅供確認，未執行任何刪除）")
    if not candidates:
        lines.append("- 太棒了！目前未偵測到符合門檻的歷史殘骸。")
    else:
        total_cand_mb = round(sum(c[1] for c in candidates), 2)
        lines.append(f"- 共找到 **{len(candidates)} 項** 候選項目，合計約 **{total_cand_mb} MB**：")
        for path_str, mb, mt, reason in candidates:
            lines.append(f"  - `{path_str}` ({mb} MB, 最後更新 `{mt}`) — {reason}")
        lines.append("\n> 如需清理，請由使用者逐一確認清單後，再移入 Windows 回收筒（切勿直接永久刪除）。")

    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Read-only audit of AI agent remnants and Windows Jump Lists."
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=60,
        help="Days since last file update to flag a folder as stale (default: 60).",
    )
    parser.add_argument(
        "--min-mb",
        type=float,
        default=5.0,
        help="Minimum folder size in MB to highlight as large stale data (default: 5.0).",
    )
    parser.add_argument(
        "--all-jumplists",
        action="store_true",
        help="Also include stale non-AI Windows Jump Lists older than --stale-days.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of Markdown report.",
    )
    args = parser.parse_args()

    report = run_audit(
        stale_days=args.stale_days,
        min_mb=args.min_mb,
        include_all_jumplists=args.all_jumplists,
    )
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
