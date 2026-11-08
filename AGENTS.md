# ai.agent_skills

> 寫給 AI 看的專案規則。全域通用規則（語言、.venv、編碼、機密）已在全域規則檔，這裡只寫本專案特有的內容。

## 專案用途

收集與維護各 AI Agent（Antigravity、Claude Code、OpenCode）共用的客製化技能包（Skills），供跨專案複用與部署。

## 目標執行環境

- 開發在：住家開發機／公司開發機
- 執行在：住家開發機／公司開發機

## 業務規則

- 每個技能為獨立子資料夾，根目錄必須具備 `SKILL.md`（包含 YAML frontmatter：name、description）。
- 技能內容嚴禁硬編碼任何個人帳號、Cookie、API Key 或機密憑證。
- 所有腳本開檔與輸出均嚴格使用 UTF-8 編碼。

## 不可更動的部分

- 現有技能對外規範的呼叫參數與安全旗標（如 OpenCode 的 `--agent plan`、`--auto`、`< nul` 等防護規範）不可隨意刪改。

## 修改後的驗證方式

1. 確認各技能目錄結構完整，`SKILL.md` 格式符合標準 frontmatter。
2. 檢查 Python 腳本語法正確：`python -m py_compile gemini-web-imagegen/scripts/*.py`。
3. 確保無機密檔案（如 cookies.json、.env）被納入版控。
