# Google Colab GPU 筆記本完整實作指南

以標準化、可重跑且深淺色主題皆清晰可讀的結構，快速建立或改造 Google Colab 雲端 GPU 筆記本（`.ipynb`）。

> **核心原則**：從內建骨架 [`assets/colab_notebook.ipynb`](../assets/colab_notebook.ipynb) 出發，避免手寫 `.ipynb` JSON 漏欄位或格式出錯；不同 GPU（L4 / A100 / G4）只影響推論耗時與顯存上限，相同模型與參數下的產出畫質與物理效果完全相同。

## 1. 適用情境

- 為專案在 `colab/` 建立新的 Google Colab GPU 試跑或運算筆記本（例如 `colab/layout_trial.ipynb`）。
- 將本機試驗腳本、模型推論流程或資料處理步驟包裝成非技術人員也能一鍵「全部執行」的 Colab 筆記本。
- 重構既有 `.ipynb`：套用標準卡片／進度表輸出、獨立 `/content/venv` 環境隔離、清除輸出與含執行痕跡的 `executionInfo`。
- 交付或提交 Git 前，對 `.ipynb` 執行結構、`ast.parse` 語法與乾淨度驗證。

## 2. 標準工作流

### 步驟 1：釐清目標、硬體與輸入輸出
開始動手前先確認三件事：
- **目標 GPU**：預設建議 **L4 GPU（24GB VRAM，最省點數）**；長篇大量運算建議 **A100（40/80GB）** 或 **G4（96GB）**；大型現代模型不建議 T4（16GB，不支援 BF16）。
- **輸入與輸出**：小檔案用 `files.upload()` / `files.download()`；大檔案或長時運算（防斷線中斷）改掛載 `drive.mount("/content/drive")` 並邊跑邊存。
- **程式碼與環境需求**：是否需要 `uv` 建立 `/content/venv` 避開 Colab 內建 PyTorch / NCCL 衝突，以及是否用到需要 Colab「🔑 密鑰」（`google.colab.userdata.get()`）的私人倉庫或 API Key。

### 步驟 2：用輔助腳本從骨架建檔（避免手寫 JSON）
執行本技能附帶的純標準函式庫腳本 [`scripts/colab_notebook.py`](../scripts/colab_notebook.py) 建立起點（預設寫入 `colab/` 或 `--out` 指定路徑）：

```bash
python "<本技能所在目錄>/scripts/colab_notebook.py" new --title "專案名稱：這本筆記本的用途" --out "colab/my_trial.ipynb" --gpu L4
```

若是整理既有筆記本、想先清乾淨輸出與執行痕跡 `metadata`，可使用 `clean` 子命令：

```bash
python "<本技能所在目錄>/scripts/colab_notebook.py" clean "colab/my_trial.ipynb" --in-place
```

### 步驟 3：依固定順序與規範填寫格子
填寫細節請參閱 [`references/colab-patterns.md`](./colab-patterns.md)，照這套結構編排能確保左側目錄完整、表單易讀且重跑安全：
- **固定格子順序**：`0. 說明` → `## ⚙️ 設定` → `1. ⚙️ 設定（只放 # @param）` → `## ▶️ 執行` → `2. 🧰 準備：載入顯示工具（原樣保留）` → `3. 1️⃣ 確認有分到 GPU` → `4. 2️⃣ 建立環境並安裝套件` → `5. 3️⃣ 準備輸入` → `6+. 4️⃣… 一格一件事` → `## 📦 結果` → `最後. N️⃣ 打包並下載結果`。
- **表單與摺疊**：每個程式格第一行用 `# @title N️⃣ 動詞開頭的步驟名稱 { display-mode: "form" }`（讓程式碼預設摺疊只看標題），第二行用 `# @markdown` 說明該格用途或操作提示；可調參數集中於「⚙️ 設定」，其餘格子只讀變數。
- **可重跑設計**：已建立環境或已存在檔案先偵測，存在時以 `info()` 提示並略過，避免重複安裝或報錯。
- **乾淨輸出與錯誤停止**：
  - 使用骨架內建的 `ok()`、`warn()`、`fail()`、`info()`、`table_html()`、`logbox()`，避免 `print` 傾倒大段文字淹沒重點。
  - 一般指令用 `sh(指令, "中文標題")`，不用 `!指令`（確保失敗時只顯示最後 40 行並停止）。
  - 需要中止後續執行時 `raise StopRun(...)`，避免整片 Python traceback 嚇到使用者。
  - 長時間任務以 `subprocess.Popen` 逐行讀取並解析 `@@` 進度標記（`@@TOTAL`、`@@STEP`、`@@PAGE` 等），用 `display(..., display_id=True)` ＋ `.update()` 原地更新進度表，完整 log 寫入 `result/_run_log.txt` 一起打包。

### 步驟 4：安全檢查與規範對照
在修改或編輯 JSON 時，請參閱 [`references/notebook-structure.md`](./notebook-structure.md)，確認：
- 頂層與 cell 層不含 `executionInfo`（會洩漏執行時間與使用者帳號資訊）。
- 所有 `code` cell 皆為 `execution_count: null` 且 `outputs: []`，避免把本機或雲端路徑、執行結果帶入 Git。
- 金鑰、Token 不寫進筆記本內。

### 步驟 5：執行自動驗證並交代實測步驟
每次產生或修改 `.ipynb` 後，執行腳本的 `validate` 子命令自我檢查：

```bash
python "<本技能所在目錄>/scripts/colab_notebook.py" validate "colab/my_trial.ipynb"
```

驗證通過後，明確告知使用者：**此筆記本尚未在 Colab 雲端實跑**，並附上操作步驟（上傳至 Google Colab → 確認執行階段為 L4/A100/G4 GPU → 選單「執行階段 → 全部執行」→ 預期每格出現 ✅ 卡片並在最後自動下載 `result.zip`）。
