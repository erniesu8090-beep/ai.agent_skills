# ai.agent_skills

> 接手工作前先讀 `PROGRESS.md`。
> 寫給 AI 看的專案規則。全域通用規則（語言、.venv、編碼、機密）已在全域規則檔，這裡只寫本專案特有的內容。

## 專案用途

各 AI Agent（Claude Code、Antigravity、OpenCode）的技能母本庫（與 `ai.agent_rules` 規則母本庫對稱）。
集中維護全域技能母本（`opencode-runner`）與專案備用技能母本（生圖、影音等），供跨專案複用與部署。

## 目標執行環境

- 開發在：住家開發機／公司開發機
- 執行在：住家開發機／公司開發機／管制機（依技能性質分流）

## 業務規則

- 每個技能為獨立子資料夾，根目錄必須具備 `SKILL.md`（包含 YAML frontmatter：name、description）。
- 技能內容嚴禁硬編碼任何個人帳號、Cookie、API Key 或機密憑證。
- 所有腳本開檔與輸出均嚴格使用 UTF-8 編碼。
- 全域技能維護以本倉庫為單一真實來源（SSOT），全域部署一律透過本倉庫之 `deploy_skills.bat` / `deploy_skills.sh` 執行。

## 不可更動的部分

- 現有技能對外規範的呼叫參數與安全旗標（如 OpenCode 的 `--agent plan`、`--auto`、`< nul` 等防護規範）不可隨意刪改。

## 修改後的驗證方式

1. 確認各技能目錄結構完整，`SKILL.md` 格式符合標準 frontmatter。
2. 檢查 Python 腳本語法正確：`python -m py_compile gemini-web-imagegen/scripts/gemini_web_gen.py`。
3. 執行全域技能部署測試：`cmd /c "echo. | deploy_skills.bat"`，確認三大全域目錄複製正常且內容一致。
4. 確保無機密檔案（如 cookies.json、.env）被納入版控。
