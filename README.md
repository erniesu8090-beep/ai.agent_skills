# AI Agent Skills (ai.agent_skills)

本倉庫為各 AI Coding Agent（Claude Code、Antigravity、OpenCode）的**技能母本庫（Skills Templates）**。

與規則母本庫 [`ai.agent_rules`](../ai.agent_rules/) 形成完全對稱的分工架構：
- **`ai.agent_rules`**：管 Agent 行為規則（Rules）與專案文件範本（`AGENTS.md`、`PROGRESS.md`、`SPEC.md`）。
- **`ai.agent_skills`**：管 Agent 外掛能力（Skills）與工具呼叫流程母本。

---

## 技能架構（二分法）

本工作區採用最簡二分架構，不設額外中間層：

| 技能分類 | 範圍與生命週期 | 存放與部署方式 | 收錄技能 |
|---|---|---|---|
| **全域技能 (Global)** | 跨所有專案通用、所有 Agent 隨時調用的規範與核心能力。 | 由本倉庫一鍵部署至使用者全域目錄：<br>• `~/.claude/skills/`<br>• `~/.gemini/config/skills/`<br>• `~/.config/opencode/skills/` | • `opencode-runner/` |
| **專案專屬技能 (Project-specific)** | 僅特定業務專案會用到的專用工具與流程母本。 | 平時於本倉庫作為**備用範本**；當特定專案需要時，複製至該專案的 `.agents/skills/` 內隨專案 Git 倉庫版控。 | • `gemini-web-imagegen/`<br>• `google-flow-bridge/` |

---

## 技能清單

| 技能目錄 | 名稱 | 分類 | 說明 |
|---|---|---|---|
| `opencode-runner/` | OpenCode CLI Runner | 全域技能 | 提供 OpenCode 子代理唯讀審查（`--agent plan`）、防卡死調用（`< nul`）與動態工作池安全規範。 |
| `gemini-web-imagegen/` | Gemini Web Image Generator CLI | 專案備用 | 沿用 gemini.google.com 網頁登入額度的免 API 金鑰 2K 生圖與圖生圖工具（需要時放入專案）。 |
| `google-flow-bridge/` | Google Flow Bridge | 專案備用 | 自動化調用 Google Flow 生成 Nano Banana 2K 圖片或 Veo MP4 影片（需要時放入專案）。 |

---

## 使用與部署方式

### 1. 全域技能一鍵部署
若更新了全域技能（如 `opencode-runner`），或在新電腦環境初始化：
- **Windows**：雙擊或執行 `deploy_skills.bat`
- **Linux / macOS**：執行 `sh deploy_skills.sh`

腳本會自動將全域技能鏡像複製至三大 Agent 的全域目錄，具備內容比對（相同自動略過）與 `.bak` 備份機制。

### 2. 專案專屬技能取用
當特定專案（如影音創作或遊戲專案）需要特定技能時，直接複製該技能資料夾至專案根目錄的 `.agents/skills/`：
```powershell
# 範例：將生圖技能複製至特定專案
Copy-Item -Recurse gemini-web-imagegen ..\media.projects\short.video_studio\.agents\skills\
```
放入後隨該專案的 Git 倉庫進行提交與同步，完全不依賴外部全域環境。
