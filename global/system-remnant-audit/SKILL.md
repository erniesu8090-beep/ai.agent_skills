---
name: system-remnant-audit
description: 對本機四大 AI Agent（Antigravity、Claude Code、Codex、OpenCode）與 Windows 工作列跳轉清單（Jump Lists）執行唯讀系統殘骸健檢。當使用者提到「檢查系統殘骸」、「歷史資料殘骸」、「空間健檢」、「清點舊版快取」、「工作列最近檔案怪怪的」、「Jump List 殘留」、「audit remnants」、「cleanup check」時載入。嚴格唯讀盤點、先報完整路徑清單並經使用者確認後才可移入回收筒，絕不自動刪檔。
---

# 系統歷史殘骸唯讀健檢（System Remnant Audit）

本 Skill 提供一鍵「只看不刪」的系統健檢流程，用來定期清點四大 AI Coding Agent（Antigravity、Claude Code、Codex、OpenCode）在本機留下的舊版資料夾、`.bak` 備份檔、安裝暫存，以及 Windows 工作列右鍵跳轉清單（Jump Lists）幽靈紀錄。

## 一鍵唯讀執行方式

於本 Skill 所在目錄下執行 `scripts/audit_remnants.py`（純 Python 3 標準庫，不需虛擬環境或第三方套件，跨平台相容）：

```bash
# 預設門檻：超過 60 天未更新、大於 5 MB 之項目
python scripts/audit_remnants.py

# 自訂天數或輸出結構化 JSON（方便程式或 AI 二次分析）
python scripts/audit_remnants.py --stale-days 30 --min-mb 1
python scripts/audit_remnants.py --json
```

> **路徑推算原則**：從全域技能目錄執行時，請由目前載入的 `SKILL.md` 所在資料夾推算 `scripts/audit_remnants.py` 的實際路徑（例如 `~/.gemini/config/skills/system-remnant-audit/scripts/audit_remnants.py`、`~/.claude/skills/system-remnant-audit/scripts/audit_remnants.py` 等），嚴禁寫死單一使用者帳號或磁碟代號。

## 檢查範圍

1. **四家 AI Agent 家目錄**：`~/.gemini`、`~/.claude`、`~/.codex`、`~/.config/opencode`
   - 依目錄內**最新檔案時間（`max_mtime`）**統計大小與檔案數，避免僅看頂層資料夾時間誤判現役目錄。
   - 彙整所有 `.bak` / `.backup` 歷史備份檔。
2. **Windows AppData（僅 `win32` 平台）**：
   - `%APPDATA%\Antigravity\`：區分「近期現役活躍項目」與「長期停更之舊版 VS Code 架構殘留（如舊 `User`、`CachedData` 等）」。
   - `%LOCALAPPDATA%\`：偵測 `antigravity*` / `*-updater` 等舊安裝暫存或空資料夾。
3. **Windows 工作列跳轉清單（Jump Lists，僅 `win32` 平台）**：
   - 唯讀掃描 `%APPDATA%\Microsoft\Windows\Recent\AutomaticDestinations` 與 `CustomDestinations`，找出關聯 AI 工具且內含已刪除路徑或逾期未更新的快取檔。

## 安全規範（絕對遵守）

1. **腳本永遠 100% 唯讀**：`audit_remnants.py` 只讀取檔案中繼資料（大小、時間）與 Jump List 二進位字串，絕不寫入、搬移或刪除任何檔案。
2. **不碰機密與權限設定檔**：不讀取 `.env`、憑證、`settings.json`、`opencode.jsonc` 或任何認證檔內容。
3. **清理前必須兩段式確認**：
   - 先將腳本找出的**完整路徑清單、大小與最後更新時間**呈現給使用者，並明確標出不可誤刪的現役目錄。
   - 必須使用選擇題工具或明確獲得使用者同意後，才可將確認項目**移入系統回收筒（或待刪除資料夾）**，嚴禁直接永久刪除。
   - 若清理了 Windows Jump List 檔，提醒使用者若工作列右鍵暫時未刷新，可於工作管理員重啟「Windows 檔案總管」或取消釘選再重釘選進行實測。
