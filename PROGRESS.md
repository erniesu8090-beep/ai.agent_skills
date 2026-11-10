# PROGRESS　進度與交接

> 最後更新：2026-11-10（住家開發機）
> 新對話接手：先讀 `AGENTS.md` → 本檔

## 一、目前階段

**維護中**。

- 最後一次 commit：`7af538f`（新增 Gemini 官方 App 技能安裝指引與白名單規範說明）

已完成：

1. 建立 Git 倉庫、`AGENTS.md`、`README.md`。
2. 收納三大共用技能：`gemini-web-imagegen`、`google-flow-bridge`、`opencode-runner`。
3. 全面清點本機（住家開發機 home）全域、外掛與各專案技能安裝位置與清冊。
4. 確立二分架構（全域唯一 `opencode-runner`；多媒體、辦公與前端排版技能保留為專案備用庫）。
5. 與 `ai.agent_rules` 徹底獨立解耦：`ai.agent_rules` 刪除 `templates/skills/` 與部署邏輯；建立本倉庫之 `deploy_global_skills.bat` 與 `deploy_global_skills.sh`，通過三大全域目錄部署驗證。
6. 收納 Anthropic 官方文檔四件套（`xlsx`、`pdf`、`docx`、`pptx`）與 `skill-creator` 至 `project/` 專案備用母本庫，作為跨專案調用與進階辦公/技能開發範本。
7. 清理專案根目錄搬移殘留之快取資料夾，確保倉庫結構嚴格遵循 `global/` 與 `project/` 二分規範。
8. 為本專案 `ai.agent_skills` 安裝 `.agents/skills/skill-creator`，作為本倉庫開發、優化與評測 Agent 技能之常駐專案技能。
9. 將辦公文檔四件套（Word、Excel、PPT、PDF）重構合併為單一聚合技能 `project/document-skills/`，採 Router 架構分流與共用 `scripts/office/` 去重，並安全移除原分散目錄。
10. 依據 `/skill-creator` 標準將前端 GUI 美學四件套（`frontend-design`、`theme-factory`、`web-artifacts-builder`、`webapp-testing`）重構合併為單一聚合技能 `project/frontend-suite/`，採四本柱 Router 架構分流與資源整合。
11. 移除 `global/frontend-design/` 並移入 `_pending_delete_/`，更新 `deploy_global_skills.bat` / `.sh`，加入自動清理各 Agent 下線技能邏輯，全域技能收斂為唯一之 `opencode-runner`。
12. 將 Web 3D 檢視器技能 `threejs` 自 `ai.agent_rules` 遷入 `project/threejs/` 作為專案備用母本，補齊雙庫解耦與 README 技能清單（2026-11-10）。

## 二、使用者已確認的事

- **技能架構定案為二分法**：只區分「全域技能（Global）」與「專案專屬技能（Project-specific）」，不設中間領域層（2026-11-08 使用者確認）。
- **母本庫對稱定位**：本倉庫定位為各 AI Agent 的**技能母本庫**，與 `ai.agent_rules` 規則母本庫功能完全對稱；兩者各自獨立無相依（2026-11-08 使用者確認）。
- **全域技能收納項**：收納 `opencode-runner`（跨引擎唯讀審查規範）。全域真實維護母本定於 `ai.agent_skills\global\`。原 `frontend-design` 依使用者需求改為併入專案備用之 `project/frontend-suite/` 按需載入（2026-11-10 使用者確認）。
- **專案備用技能處置**：前端 GUI 美學全功能套件（`frontend-suite`）、辦公文檔四件套（`document-skills`）、技能製作評測（`skill-creator`）、生圖/影音（`gemini-web-imagegen`、`google-flow-bridge`）確認屬專案專屬性質（非全域），保留在 `ai.agent_skills\project\` 作為備用與共用範本庫，待未來特定專案需要時再複製進該專案的 `.agents/skills/`（2026-11-08 及 2026-11-10 使用者確認）。
- **專案專屬技能部署原則**：隨專案各自的 Git 倉庫版本控管與同步，免額外安裝腳本或全域設定。

## 三、待使用者決定（下次討論從這裡開始）

（目前沒有）

## 四、已查證的重要發現（本機技能清點總表）

### 1. 三大 AI Agent 全域技能安裝位置（User Global Skills）

三大 Agent 在本機的使用者全域技能目錄均已實測定位，目前均已安裝 `opencode-runner`：

| Agent | 全域技能安裝目錄 | 目前已安裝技能 | 說明 |
|---|---|---|---|
| **Antigravity** | `C:\Users\jagger\.gemini\config\skills\` | `opencode-runner` | Antigravity 全域自訂技能目錄 |
| **Claude Code** | `C:\Users\jagger\.claude\skills\` | `opencode-runner` | Claude Code 全域技能目錄 |
| **OpenCode** | `C:\Users\jagger\.config\opencode\skills\` | `opencode-runner` | OpenCode 全域技能目錄 |

---

### 2. Antigravity 平台內建與已啟用外掛技能（Platform Built-in & Plugins）

由 Antigravity 系統與安裝之外掛插件自動載入的技能：

#### (1) 系統內建技能（Built-in Skills）
- **安裝路徑**：`C:\Users\jagger\.gemini\antigravity\builtin\skills\`
- **技能清冊**：
  1. `agy-customizations`：Antigravity Customization System 完整指引與客製化擴充規範。
  2. `antigravity_guide`：Antigravity (AGY) 2.0 / CLI / IDE 完整操作與設定手冊。
  3. `automation`：互動式設計與建立排程背景自動化任務。
  4. `generative_ui`：生成式 UI 與互動式 HTML 元件渲染。
  5. `migrate-workflows`：將舊版 Workflows 自動遷移至現代 SKILL.md 架構。
  6. `permissioned-github`：授權 GitHub 工作流程與操作。
  7. `plugin`：外掛模組管理（建立、安裝、啟用、停用）。
  8. `run-workflow`：執行工作流程腳本。
  9. `ui-plugin-navigation`：UI 外掛側邊欄面板快捷導航。

#### (2) 已啟用外掛技能（Active Plugins Skills）
- **安裝路徑**：`C:\Users\jagger\.gemini\config\plugins\<plugin-name>\skills\`
- **技能清冊**：
  1. `android-cli-plugin`：`android-cli`、`compose-preview`、`device-hub`。
  2. `chrome-devtools-plugin`：`chrome-devtools`、`a11y-debugging`、`cookie-debugging`、`debug-optimize-lcp`、`memory-leak-debugging`、`troubleshooting`。
  3. `gcalendar`：`gcalendar`。
  4. `gdrive`：`gdrive`。
  5. `gemini-api`：`gemini-api-dev`、`gemini-live-api-dev`、`gemini-omni-flash-api`。
  6. `google-antigravity-sdk`：`google-antigravity-sdk`。
  7. `google-cloud-developer`：`gcloud`、`finding-google-skills`、`google-cloud-recipe-auth`、`google-cloud-recipe-onboarding`、`retrieving-developer-knowledge`。
  8. `gsheets`：`gsheets`。

#### (3) Antigravity IDE 專用插件技能
- **安裝路徑**：`C:\Users\jagger\.gemini\antigravity-ide\plugins\Google.securecoder.securecoder\skills\`
- **技能清冊**：SecureCoder 系列（`create_security_implementation_plan`、`determine_threat_model`、`generate_security_audit_report`、`run_poc`、`run_security_scanner`、`scan_dependencies` 等）。

---

### 3. 共用技能母本庫（Shared Skills Repository）

| 倉庫路徑 | 技能名稱 | 來源 | 說明 |
|---|---|---|---|
| D:\AI_Workspace\ai.agent_skills\global\opencode-runner | opencode-runner | 自訂 | 調用 OpenCode CLI 唯讀審查與比對規範（全域技能母本，開發機與管制機通用） |
| D:\AI_Workspace\ai.agent_skills\project\frontend-suite | frontend-suite | Anthropic 官方 | 前端 GUI 排版與設計全功能四合一套件（涵蓋美學防套版、10款主題色票、React+shadcn單檔打包、Playwright截圖驗證） |
| D:\AI_Workspace\ai.agent_skills\project\document-skills | document-skills | Anthropic 官方 | Office 與 PDF 全功能處理套件（Word 排版、Excel recalc 重算、PPT 生成、PDF 提取填表） |
| D:\AI_Workspace\ai.agent_skills\project\skill-creator | skill-creator | Anthropic 官方 | 建立、優化、評測與除錯 Agent Skills 的標準指引與評估工具（專案備用母本） |
| D:\AI_Workspace\ai.agent_skills\project\cli-creator | cli-creator | OpenAI 官方 | 建立高品質、可由命令行直接調用、輸出穩定 JSON、具備良好錯誤代碼與伴生 Skill 的標準化 CLI 工具 |
| D:\AI_Workspace\ai.agent_skills\project\gh-fix-ci | gh-fix-ci | OpenAI 官方 | 排查並修復 GitHub Actions 失敗的 PR checks，自動提取錯誤日誌摘要、擬定修復計畫並驗證 |
| D:\AI_Workspace\ai.agent_skills\project\jupyter-notebook | jupyter-notebook | OpenAI 官方 | 建立、鷹架生成或編輯 Jupyter 筆記本（.ipynb），提供實驗分析與教學導向標準範本，避免手刻 JSON 損壞 |
| D:\AI_Workspace\ai.agent_skills\project\gemini-web-imagegen | gemini-web-imagegen | 自訂 | 免 API 金鑰 2K AI 生圖與圖生圖工具（專案備用母本，需要時放入特定專案） |
| D:\AI_Workspace\ai.agent_skills\project\google-flow-bridge | google-flow-bridge | 自訂 | 免 API 金鑰調用 Google Flow 生成 2K 圖片或 Veo 影片（專案備用母本，需要時放入特定專案） |

> 註：標示「Anthropic 官方」者引用自官方開源庫 [anthropics/skills](https://github.com/anthropics/skills)。
> 註：標示「OpenAI 官方」者引用自官方開源庫 [openai/skills](https://github.com/openai/skills)。

---

### 4. 業務專案自訂技能（Project-specific Skills）

在 `D:\AI_Workspace\` 各專案中，排除虛擬環境（`.venv` 第三方套件如 FastAPI、Playwright、Streamlit 自帶之技能）後，實際開發維護的自訂專案技能如下：

| 專案分類與路徑 | 技能名稱 | 說明 |
|---|---|---|
| **技能母本庫專案**<br>`D:\AI_Workspace\ai.agent_skills\.agents\skills\` | `skill-creator` | Agent Skills 製作、修改、描述詞最佳化與評測標準指引（本專案常駐技能） |
| **短片影音專案**<br>`D:\AI_Workspace\media.projects\short.video_studio\agent\skills\` | `blender-previs` | 山獅霸 AI 短劇的 Blender 3D 空間白模預演、鏡位契約、布置圖鎖定與提示詞素材打包 |
| 同上 | `shanshiba-drama` | AI 短劇編劇與雙軌執行導演（V2.5 雙軌模式：原創/改編/抽幀逆向，排鏡表與提示詞流） |
| **逆向工程專案**<br>`D:\AI_Workspace\reverse.projects\rea\.agents\skills\` | `reverse-engineer-anything` | 本機、二進制、韌體、Electron 與瀏覽器目標的逆向工程與反編譯分析工具 |
| 同上 | `rea-tool-design` | REA 逆向輔助工具設計規格與指引 |
| 同上 | `rea-ci-tests-audit` | REA 持續整合與測試審核規範 |
| 同上 | `rea-changelog-update` | REA 變更日誌自動化維護規範 |

---

## 五、試過但無效的做法（接手者不要重複）

- （尚無無效記錄）
- 最後一個正常運作的 commit：`7af538f`

## 六、下一步

1. **依專案需求複製技能**：未來當其他專案有辦公文檔（`xlsx`/`pdf`/`docx`/`pptx`）、多媒體生圖（`gemini-web-imagegen`/`google-flow-bridge`）需求時，自本母本庫 `project/` 複製對應技能至該專案的 `.agents/skills/` 內隨專案版控。
2. **技能開發與優化**：利用本專案已常駐安裝之 `.agents/skills/skill-creator`，為工作區自訂技能建立 Eval 評測、打磨 Trigger Description 並標準化輸出結構。
3. **新增共用技能**：若開發出新的跨專案共用技能，在此建立獨立目錄、撰寫 `SKILL.md`，若屬全域技能則同步加入 `deploy_global_skills.bat` / `.sh` 的部署清單。

## 七、接手須知（環境與工具）

- **全域技能部署**：本倉庫執行 `deploy_global_skills.bat`（Windows）或 `sh deploy_global_skills.sh`（Linux/macOS）即可同步至各大 Agent 全域目錄。
- **全域技能目錄對照**：
  - Antigravity: `~/.gemini/config/skills/`
  - Claude Code: `~/.claude/skills/`
  - OpenCode: `~/.config/opencode/skills/`
- **專案技能放置規範**：直接放該專案的 `<專案根目錄>/.agents/skills/<skill-name>/`，隨專案 Git 倉庫版本控管。

## 八、修訂紀錄

| 日期 | 電腦 | 內容 |
|---|---|---|
| 2026-11-08 | 住家開發機 | 建立 PROGRESS.md，完成本機全域、Antigravity 內建/外掛、共用技能庫與專案技能的完整盤點 |
| 2026-11-08 | 住家開發機 | 確立二分架構（全域唯一 opencode-runner；生圖/影音保留為專案備用庫，需要再放） |
| 2026-11-08 | 住家開發機 | 與 ai.agent_rules 徹底獨立解耦：建立 deploy_skills 部署腳本，通過三大全域目錄驗證，更新母本庫文檔 |
| 2026-11-09 | 公司開發機 | 建立 global/ 與 project/ 實體分類資料夾，全面更新部署腳本、專案規則、說明文件與驗證路徑 |
| 2026-11-10 | 住家開發機 | 收納 Anthropic 官方 frontend-design 至 global/，更新 deploy_global_skills 與文件，完成三大 Agent 部署（Anthropic 官方技能） |
| 2026-11-10 | 住家開發機 | 收納 Anthropic 官方文檔四件套（xlsx, pdf, docx, pptx）與 skill-creator 至 project/ 備用母本庫，通過 Python 腳本編譯與 frontmatter 驗證；清理根目錄殘留之快取目錄 |
| 2026-11-10 | 住家開發機 | 為 ai.agent_skills 安裝 .agents/skills/skill-creator 專案技能；全面檢核校正 PROGRESS.md 與 README.md，更新 commit 雜湊與業務專案技能清單 |
| 2026-11-10 | 住家開發機 | 依據 /skill-creator 標準完成三大自訂技能（google-flow-bridge、gemini-web-imagegen、opencode-runner）之安全去識別化、路徑泛化、觸發描述打磨，並將部署腳本更名為 deploy_global_skills 且通過全域同步部署驗證 |
| 2026-11-10 | 住家開發機 | 將辦公文檔四件套合併為單一聚合技能 project/document-skills，去重共用 office 模組並通過全數 26 個腳本編譯與驗證 |
| 2026-11-10 | 住家開發機 | 查證 Google 官方最新 Gems to Skills 轉型規範，於 README.md 增補上傳資料夾至 Gemini 官方網頁/App 之完整操作步驟 |
| 2026-11-10 | 公司開發機 | 依據 /skill-creator 標準將前端美學四件套合併為單一聚合技能 project/frontend-suite/，採四本柱 Router 架構；移除 global/frontend-design/ 並更新部署腳本為僅部署 opencode-runner |
| 2026-11-10 | 住家開發機 | 調研 OpenAI 官方技能庫 openai/skills，收納 cli-creator、gh-fix-ci 與 jupyter-notebook 至 project/ 專案備用庫，完成多 Agent 中立化改寫與自動化驗證 |
