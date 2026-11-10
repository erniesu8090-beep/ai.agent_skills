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
| **全域技能 (Global)** | 跨所有專案通用、所有 Agent 隨時調用的規範與核心能力。 | 由本倉庫一鍵部署至使用者全域目錄：<br>• `~/.claude/skills/`<br>• `~/.gemini/config/skills/`<br>• `~/.config/opencode/skills/` | • `global/opencode-runner/` |
| **專案專屬技能 (Project-specific)** | 僅特定業務專案會用到的專用工具與流程母本。 | 平時於本倉庫作為**備用範本**；當特定專案需要時，複製至該專案的 `.agents/skills/` 內隨專案 Git 倉庫版控。 | • `project/frontend-suite/`<br>• `project/document-skills/`<br>• `project/skill-creator/`<br>• `project/gemini-web-imagegen/`<br>• `project/google-flow-bridge/`<br>• `project/threejs/` |

---

## 技能清單

| 技能目錄 | 名稱 | 分類 | 來源 | 說明 |
|---|---|---|---|---|
| `global/opencode-runner/` | OpenCode CLI Runner | 全域技能 | 自訂 | 提供 OpenCode 子代理唯讀審查（`--agent plan`）、防卡死調用（`< nul`）與動態工作池安全規範。 |
| `project/frontend-suite/` | Frontend Suite (UI/UX, Theming & Testing) | 專案備用 | Anthropic 官方 | 前端 GUI 排版與設計全功能四合一套件：涵蓋前端美學與反樣板感（frontend-design）、10 款主題與色票生成（theme-factory）、React 18 + shadcn 工程化打包（web-artifacts-builder）、Playwright 截圖排版驗證（webapp-testing）。 |
| `project/document-skills/` | Document Skills Suite (Office & PDF) | 專案備用 | Anthropic 官方 | Office 與 PDF 全功能處理套件：涵蓋 Word 排版、Excel 試算表與 recalc 公式重算、PPT 投影片生成、PDF 提取與表單填寫。 |
| `project/skill-creator/` | Agent Skill Creator & Evaluator | 專案備用 | Anthropic 官方 | 建立、優化、評測與除錯 Agent Skills 的標準指引與評估工具。 |
| `project/gemini-web-imagegen/` | Gemini Web Image Generator CLI | 專案備用 | 自訂 | 沿用 gemini.google.com 網頁登入額度的免 API 金鑰 2K 生圖與圖生圖工具（需要時放入專案）。 |
| `project/google-flow-bridge/` | Google Flow Bridge | 專案備用 | 自訂 | 自動化調用 Google Flow 生成 Nano Banana 2K 圖片或 Veo MP4 影片（需要時放入專案）。 |
| `project/threejs/` | Three.js r170 Web 3D Suite | 專案備用 | 自訂 | Three.js r170 現代 Web 3D 開發與模型檢視器指引（含最新繁中文件、Import Map 單檔架構、GLTF 載入與效能最佳化）。 |

> **來源說明**：
> - **Anthropic 官方**：引用自 Anthropic 官方開源技能庫 [`anthropics/skills`](https://github.com/anthropics/skills)。
> - **自訂**：本工作區依特定工作流或跨引擎需求自研之專案與全域規範。

---

## 使用與部署方式

### 1. 全域技能一鍵部署（本機三大 Agent）
若更新了全域技能（如 `global/opencode-runner`），或在新電腦環境初始化：
- **Windows**：雙擊或執行 `deploy_global_skills.bat`
- **Linux / macOS**：執行 `sh deploy_global_skills.sh`

腳本會自動將全域技能鏡像複製至三大 Agent 的全域目錄，具備內容比對（相同自動略過）、`.bak` 備份機制，並自動清理已下線的全域技能。

### 2. 專案專屬技能取用（本機各專案）
當特定專案（如影音創作、前端網頁、辦公自動化或逆向專案）需要特定技能時，直接複製該技能資料夾至專案根目錄的 `.agents/skills/`：
```powershell
# 範例 1：將前端 GUI 排版美化套件複製至網頁專案
Copy-Item -Recurse project\frontend-suite ..\my_web_app\.agents\skills\

# 範例 2：將辦公文檔全功能套件複製至股票助理專案
Copy-Item -Recurse project\document-skills ..\tw.stock_assistant\.agents\skills\

# 範例 3：將生圖技能複製至短影音專案
Copy-Item -Recurse project\gemini-web-imagegen ..\media.projects\short.video_studio\.agents\skills\
```
放入後隨該專案的 Git 倉庫進行提交與同步，完全不依賴外部全域環境。

> **註**：本母本庫專案（`ai.agent_skills`）本身亦已於 `.agents/skills/skill-creator/` 安裝技能製作工具，常駐支援母本庫之技能擴充、撰寫與 Eval 評測。

### 3. 安裝至 Google Gemini 官方網頁版 / 手機 App (gemini.google.com)
Google Gemini 官方應用程式已全面將 Gems 升級為 **Skills（技能）** 架構，原生支援 `agentskills.io` 開放標準的 `SKILL.md`。

> **⚠️ Gemini 官方 App 檔案格式白名單限制**：
> 官方上傳介面目前**僅支援五種檔案類型**：**`PDF`、`CSV`、`PY`、`TXT`、`MD`**。
> 若資料夾中夾帶 Python 編譯快取（`__pycache__/*.pyc`）、網頁檔（`.html`）或結構描述檔（`.xml`、`.xsd`），系統將拒絕上傳並提示不支援該類型。

#### 上傳方式 A：單檔選取上傳（最推薦、最輕量）
Gemini 雲端 App 主要是依據 Markdown 專家指南來引導雲端模型行為，直接選取文件最快速：
1. 瀏覽器造訪 [gemini.google.com](https://gemini.google.com) ➜ 點選左側 **「Skills」** ➜ 點選 **「新增技能（Create Skill / +）」**。
2. 點選 **「選取 檔案（Select Files）」**：
   - 安裝 `skill-creator`：選取 `project/skill-creator/SKILL.md` 即可。
   - 安裝 `document-skills`：選取 `project/document-skills/SKILL.md` 以及 `references/` 底下的 4 個指南（`docx.md`、`xlsx.md`、`pptx.md`、`pdf.md`）。
3. 檢查名稱與觸發描述無誤後，點選 **「儲存 / 啟用」**。

#### 上傳方式 B：整包資料夾上傳
若希望上傳整個技能目錄，請確保資料夾內**無 `__pycache__` 或非白名單檔案**：
1. 本專案已排除所有 `.pyc` 快取。
2. 若資料夾內含 `.html`（如評測工具）或 `.xsd`，請先將其移除或移出，確保資料夾內僅存 `.py`、`.md`、`.txt`。
3. 點選 **「選取 資料夾」** 進行上傳並儲存。

#### 對話調用方式
- **手動調用**：在任何 Gemini 對話框輸入 `@技能名稱`（例如 `@document-skills 請幫我做一份財務報表 Excel`）。
- **自動觸發**：直接輸入需求（如「產出 16:9 簡報投影片」或「設計一個新的 Agent Skill」），Gemini 將自動匹配並載入該技能規範。
