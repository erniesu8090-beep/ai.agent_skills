---
name: skill-creator
description: "Create, edit, initialize, validate, and package Agent Skills following the agentskills.io standard across Antigravity, Claude Code, Codex, OpenCode, and Gemini App. Use when users want to create a skill from scratch, turn a workflow into a skill, refactor or slim down an existing SKILL.md, refine a skill's trigger description, validate SKILL.md frontmatter, or package a clean .zip/.skill archive."
---

# Skill Creator（跨平台極簡強化版）

將重複性工作流、領域規範與確定性腳本封裝為符合 `agentskills.io` 標準的跨平台 Agent Skill，同時相容本機開發工具（Antigravity、Claude Code、Codex、OpenCode）與雲端 Gemini App。

## 核心原則

### 1. 極簡與漸進式載入（Progressive Disclosure）
- **三層載入**：① `name` + `description`（常駐上下文）→ ② `SKILL.md` 本體（觸發後載入，建議 `< 500` 行，Antigravity 硬上限 `24,000 bytes`）→ ③ `scripts/`、`references/`、`assets/`（按需讀取或直接執行）。
- **只放模型不知道的事**：省略語言常識與冗長背景；需要多案例、變體分支或詳細規格時移入 `references/`（與 `SKILL.md` 維持一層深度，超過 100 行加目錄），採 Router 分流避免重複敘述。
- **解釋原因勝過全大寫禁令**：說明為什麼某件事重要，讓模型理解脈絡而非死記硬性口號；並遵守無驚訝原則，嚴禁夾帶惡意指令或隱藏行為。
- **禁止技能內附帶冗餘說明檔**：不要在技能資料夾內建立 `README.md`、`CHANGELOG.md`、`INSTALLATION_GUIDE.md` 等給人看的文件，避免浪費 Token 或干擾上傳。

### 2. 依任務脆弱性設定自由度
- **高自由度（純文字指引）**：步驟彈性大、依情境判斷（例如文案風格、架構討論）。
- **中自由度（帶參數腳本或虛擬碼）**：有固定偏好流程但允許微調參數。
- **低自由度（固定腳本）**：步驟脆弱易錯或需確定性結果（例如格式驗證、檔案解析、打包）。

### 3. 跨平台最嚴格交集規範
- **Frontmatter 僅用標準欄位**：`name`（`kebab-case`、小寫英數與連字號、`<= 64` 字元）與 `description`（`<= 1024` 字元、不可含角括號）；必要時才加 `license`、`allowed-tools`、`metadata`、`compatibility`。
- **`description` 必須寫成單行字串**：不要使用 YAML 多行折行（`>-`、`|`），以同時相容 Google Gemini CLI／Gemini App 與純文字解析器；所有「做什麼」與「何時觸發」的關鍵字都放這裡，不要寫進內文觸發段。

---

## 製作與迭代流程

### Step 1：釐清用途與具體範例
先確認這項技能要解決什麼任務、使用者會如何提問觸發、預期產出格式，以及目標平台。若目前對話已經示範過一次流程（例如「把剛剛這套做成技能」），直接從對話脈絡萃取步驟、糾正與輸入輸出格式；**避免連環追問**，先提出具體草案與 2–3 個範例讓使用者一次確認。

### Step 2：規劃可複用資源
檢視每個範例，判斷是否需要拆出資源資料夾：
- `scripts/`：重複撰寫或要求零失誤的操作（一律用 Python 3 標準庫 + UTF-8、`pathlib.Path` 推算路徑）。
- `references/`：細部規格、API 說明或領域清單。
- `assets/`：最終輸出要複製或套用的範本、資料檔或圖示。

### Step 3：初始化技能骨架
從本技能所在目錄呼叫 [init_skill.py](./scripts/init_skill.py) 建立標準目錄（不寫死使用者目錄或磁碟代號）：

```bash
python "<本技能所在目錄>/scripts/init_skill.py" <skill-name> --path <output-dir> --resources scripts,references
```

需要參考範本檔時加上 `--examples`；完成後刪掉未用到的範例檔或空目錄。

### Step 4：撰寫與實測資源
1. 先實作並實際執行 `scripts/` 內所有腳本，確認跨平台路徑與 UTF-8 讀寫無誤。
2. 填寫 `SKILL.md`：使用祈使語氣描述步驟、以相對路徑連結附帶資源、清除所有待辦佔位標記。

### Step 5：跨平台嚴格驗證與潔淨打包
完成編輯後，執行 [quick_validate.py](./scripts/quick_validate.py)（零第三方依賴）驗證格式、單行 `description`、24,000 bytes 上限與未完成標記：

```bash
python "<本技能所在目錄>/scripts/quick_validate.py" "<目標技能目錄>" --strict
```

需要分發給同事或上傳 **Gemini App** 時，執行 [package_skill.py](./scripts/package_skill.py) 打包為潔淨壓縮檔（預設根目錄直含 `SKILL.md`）：

```bash
# 一般潔淨打包（.zip，自動排除 __pycache__、.git、.venv、.env、evals 等）
python "<本技能所在目錄>/scripts/package_skill.py" "<目標技能目錄>" "<輸出目錄>"

# Gemini App 專用（僅保留 .pdf / .csv / .py / .txt / .md 白名單檔型）
python "<本技能所在目錄>/scripts/package_skill.py" "<目標技能目錄>" "<輸出目錄>" --gemini

# 傳統外包一層 <skill-name>/ 目錄的 .skill 封裝
python "<本技能所在目錄>/scripts/package_skill.py" "<目標技能目錄>" "<輸出目錄>" --wrap-dir --ext .skill
```

---

## 跨平台部署速查

| 平台 | 專案／全域路徑 | 實務注意事項 |
|---|---|---|
| **Antigravity** | 專案 `.agents/skills/<name>/`<br>全域 `~/.gemini/config/skills/` | `SKILL.md` 單檔上限 **24,000 bytes**；全域與 `always_on` 共享 **20,000 tokens** 預算。 |
| **Claude Code** | 專案 `.agents/skills/`（或 `.claude/skills/`）<br>全域 `~/.claude/skills/` | 避免與專案層級重複放置；本倉庫全域技能統一由部署腳本鏡像同步。 |
| **Codex** | 專案 `.agents/skills/<name>/`<br>全域 `~/.codex/skills/` | 若技能是跨工具橋接 Codex（如 `codex-imagegen-bridge`），勿同步進 Codex 自身全域目錄。 |
| **OpenCode** | 專案 `.opencode/skills/<name>/`（亦相容 `.agents/skills/`）<br>全域 `~/.config/opencode/skills/` | 可作為跨引擎唯讀審查者驗證技能與產出品質。 |
| **Gemini App** | `gemini.google.com` 側欄「自訂 > 技能 > 上傳」 | 僅接受白名單檔型：**`.pdf`、`.csv`、`.py`、`.txt`、`.md`**；`description` 必為單行，壓縮檔根目錄必直含 `SKILL.md`，建議用 `--gemini` 打包。 |
