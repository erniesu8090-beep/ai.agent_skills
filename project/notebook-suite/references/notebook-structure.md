# Notebook JSON 結構與安全交付檢查

## 1. `.ipynb` JSON 基本結構

Jupyter / Colab 筆記本是結構嚴謹的 JSON 文件，頂層包含：

- `nbformat`: `4`、`nbformat_minor`: `0`（沿用骨架版本）
- `metadata`: 筆記本層級設定
- `cells`: 有序的 Markdown 與 Code 格子陣列

修改既有 `.ipynb` 時應遵守：
- 保留 `nbformat`、`nbformat_minor` 與格子順序，非必要不隨意重新排序。
- Markdown 格固定維持 `cell_type: "markdown"` 與 `metadata: {}`。
- Code 格於編輯或提交前維持 `execution_count: null` 與 `outputs: []`。
- 建議一律透過 `scripts/colab_notebook.py` 建立骨架、清理與驗證，避免手寫 JSON 造成跳脫字元遺漏或格式毀損。

## 2. Colab `metadata` 白名單與隱私安全

提交至 Git 前，**頂層 `metadata`** 只保留骨架內建的乾淨欄位：
- `accelerator`: `"GPU"`
- `colab`:
  - `provenance`: `[]`
  - `gpuType`: `"L4"`（或 `"A100"`、`"G4"`、`"T4"`）
  - `toc_visible`: `true`（讓 Colab 左側目錄自動展開）
- `kernelspec`: `{"display_name": "Python 3", "name": "python3"}`
- `language_info`: `{"name": "python"}`

注意事項：
- **禁止殘留執行痕跡**：Colab 執行後常會在各 cell 的 `metadata` 寫入 `executionInfo`（包含執行時間與使用者帳號資訊）或 `outputId`，以及在 `outputs` 殘留本機路徑／檔名。提交版控前務必清除。
- **金鑰與敏感資料**：不得在筆記本內硬編碼任何 API Key、GitHub Token、密碼或公司內部機密資料；私人憑證統一改由 Colab「🔑 密鑰」（`google.colab.userdata.get()`）讀取。

## 3. 交付前品質檢查清單

交付給使用者前，確認以下項目全數通過（可先執行 `scripts/colab_notebook.py validate` 自動檢查）：

1. **JSON 與語法**：`.ipynb` 可被 `json.load` 正常解析，所有程式格及內嵌 `script = r"""..."""` 皆通過 `ast.parse`。
2. **無殘留輸出與個資**：所有程式格 `outputs == []`、`execution_count is None`，且無 `executionInfo` 欄位。
3. **格子與目錄結構**：僅第 0 格有一個 `# ` 一級標題，其餘使用 `## ` / `### `；`metadata.colab.toc_visible` 為 `true`。
4. **表單與參數集中**：所有可調參數集中於「⚙️ 設定」格（`# @param`），後續程式格皆以 `# @title ... { display-mode: "form" }` 摺疊。
5. **可重跑與友善提示**：重複執行同一格不會因環境或檔案已存在而失敗；錯誤時使用 `fail()` ＋ `StopRun`。
6. **明確說明雲端實測步驟**：提醒使用者於 Colab 設定目標 GPU 後執行「全部執行」，並說明預期出現的 ✅ 狀態與最終下載檔案及本機存放路徑。
