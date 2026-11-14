---
name: notebook-suite
description: "建立、鷹架生成、重構、清理與驗證 Jupyter 筆記本與 Google Colab 雲端 GPU 筆記本（.ipynb）的全功能套件。涵蓋：(1) Google Colab 雲端 GPU 筆記本（L4、A100、G4、T4 算力試跑、# @title 摺疊表單與 # @param 參數、uv 獨立環境隔離、HTML 狀態卡片與 @@ 進度表、輸出與 executionInfo 清理、AST 語法檢查）；(2) 本機 Jupyter 實驗分析型（experiment）與教學導向型（tutorial）筆記本鷹架生成。當使用者需要建立或編輯 .ipynb、把本機腳本或模型推論搬上 Colab 雲端 GPU 試跑、整理研究探索筆記、清理筆記本執行痕跡或驗證 .ipynb 結構與語法時皆可使用。"
license: Apache-2.0
---

# Notebook Suite (Jupyter & Google Colab GPU 全功能套件)

本技能整合了 **Google Colab 雲端 GPU 互動筆記本** 與 **本機 Jupyter 實驗／教學筆記本** 兩大工作流，提供標準化範本、建檔腳本、執行痕跡清理與 AST 語法驗證工具，徹底避免手刻 `.ipynb` JSON 造成的格式損壞與個資殘留。

## 雙支柱導覽（Two Pillars Router）

請依任務目標選擇對應的支柱與子指南（位於 `references/`）：

| 支柱 (Pillar) | 適用情境 | 核心子指南 | 範本與輔助腳本 |
|---|---|---|---|
| **1. Google Colab 雲端 GPU 筆記本** | 雲端 GPU（L4 / A100 / G4 / T4）模型推論與試跑、`colab/*.ipynb`、非技術人員一鍵「全部執行」摺疊表單（`# @title` / `# @param`）、`/content/venv` 環境隔離 | [`references/colab-guide.md`](./references/colab-guide.md)<br>[`references/colab-patterns.md`](./references/colab-patterns.md) | • 範本：`assets/colab_notebook.ipynb`<br>• 腳本：`scripts/colab_notebook.py`（支援 `new`、`clean`、`validate`） |
| **2. 本機 Jupyter 實驗與教學筆記本** | 本機資料探索、假說驗證實驗（`experiment`）、分步教學講義（`tutorial`）、研究筆記重構 | [`references/jupyter-guide.md`](./references/jupyter-guide.md)<br>[`references/experiment-patterns.md`](./references/experiment-patterns.md)<br>[`references/tutorial-patterns.md`](./references/tutorial-patterns.md) | • 範本：`assets/experiment-template.ipynb`、`assets/tutorial-template.ipynb`<br>• 腳本：`scripts/new_notebook.py` |
| **共用規範：JSON 結構與安全交付** | `.ipynb` 底層 JSON 結構、Colab `metadata` 白名單、清除 `outputs` 與 `executionInfo`、交付前品質檢查 | [`references/notebook-structure.md`](./references/notebook-structure.md)<br>[`references/quality-checklist.md`](./references/quality-checklist.md) | • 驗證與清理：`scripts/colab_notebook.py validate / clean` |

---

## 快速決策樹（Decision Tree）

1. **要在 Google Colab 雲端跑 GPU、給使用者一鍵「全部執行」、或放在專案 `colab/` 資料夾？**
   👉 走 **支柱 1（Google Colab GPU）**：使用 `scripts/colab_notebook.py new` 建立骨架，並閱讀 [`references/colab-patterns.md`](./references/colab-patterns.md)。
2. **要在平時本機做資料分析／實驗對照（Experiment），或撰寫教學演練講義（Tutorial）？**
   👉 走 **支柱 2（本機 Jupyter）**：使用 `scripts/new_notebook.py --kind <experiment|tutorial>` 建立骨架，並閱讀 [`references/jupyter-guide.md`](./references/jupyter-guide.md)。
3. **要清理既有 `.ipynb` 的輸出與帳號痕跡（`executionInfo`），或檢查 `.ipynb` 是否有 Python 語法錯誤？**
   👉 直接執行 `scripts/colab_notebook.py clean` 與 `scripts/colab_notebook.py validate`。

---

## 支柱 1：Google Colab 雲端 GPU 筆記本工作流

### 1. 從標準骨架建立 Colab 筆記本
```bash
python "<本技能所在目錄>/scripts/colab_notebook.py" new \
  --title "專案名稱：這本筆記本的用途" \
  --out "colab/my_trial.ipynb" \
  --gpu L4
```
- **GPU 選型原則**：預設首選 **L4 GPU（24GB VRAM，CP 值最高最省點數）**；長篇大量運算選 **A100（40/80GB）** 或 **G4（96GB）**；大型現代模型不建議 T4。相同模型與參數下各 GPU 畫質與物理效果完全相同，僅影響推論速度與顯存上限。

### 2. 固定格子順序與互動表單規範
詳見 [`references/colab-patterns.md`](./references/colab-patterns.md)：
- **固定順序**：`0. 說明（唯一 # 大標題）` → `## ⚙️ 設定` → `1. ⚙️ 設定（集中放 # @param）` → `## ▶️ 執行` → `2. 🧰 準備：載入顯示工具（原樣保留）` → `3. 1️⃣ 確認有分到 GPU` → `4. 2️⃣ 建立獨立環境（/content/venv）` → `5. 3️⃣ 準備輸入` → `6+. 4️⃣… 執行（一格一件事）` → `## 📦 結果` → `最後. N️⃣ 打包並下載結果`。
- **程式碼摺疊**：每個程式格首行必加 `# @title N️⃣ 動詞開頭的步驟名稱 { display-mode: "form" }`，第二行用 `# @markdown` 說明用途。
- **乾淨輸出与錯誤攔截**：使用骨架內建 `ok()`、`warn()`、`fail()`、`info()`、`table_html()`、`logbox()` 與 `sh(cmd, "標題")`，中止時 `raise StopRun(...)`；長任務以 `@@TOTAL` / `@@STEP` 原地更新進度表，完整日誌寫入 `result/_run_log.txt`。

---

## 支柱 2：本機 Jupyter 實驗與教學筆記本工作流

### 1. 從範本鷹架生成本機筆記本
```bash
# 建立實驗分析型筆記本 (Experiment)
python "<本技能所在目錄>/scripts/new_notebook.py" \
  --kind experiment \
  --title "Compare prompt variants" \
  --out "output/jupyter-notebook/compare-prompt-variants.ipynb"

# 建立教學導向型筆記本 (Tutorial)
python "<本技能所在目錄>/scripts/new_notebook.py" \
  --kind tutorial \
  --title "Intro to embeddings" \
  --out "output/jupyter-notebook/intro-to-embeddings.ipynb"
```

### 2. 撰寫與重構原則
詳見 [`references/jupyter-guide.md`](./references/jupyter-guide.md)、[`references/experiment-patterns.md`](./references/experiment-patterns.md) 與 [`references/tutorial-patterns.md`](./references/tutorial-patterns.md)：
- 每格聚焦單一可執行步驟，搭配簡短 Markdown 說明目的與預期結果。
- 避免傾倒巨量輸出，優先以摘要小表或關鍵指標呈現。

---

## 共用工具：清理與自動化驗證（交付前必跑）

無論是 Colab 或本機 Jupyter 筆記本，提交 Git 或交付給使用者前，均可使用 `scripts/colab_notebook.py` 執行清理與驗證：

```bash
# 1. 清除所有輸出 (outputs: [])、execution_count 與 executionInfo 個資痕跡
python "<本技能所在目錄>/scripts/colab_notebook.py" clean "path/to/notebook.ipynb" --in-place

# 2. 自動驗證 JSON 結構、各格與內嵌 script 字串之 Python AST 語法、以及乾淨度
python "<本技能所在目錄>/scripts/colab_notebook.py" validate "path/to/notebook.ipynb"
```

- **Colab 筆記本嚴格檢查**：對 Colab 筆記本可加上 `--strict`（強制檢查 `# @title ... { display-mode: "form" }`、`toc_visible` 與單一 H1 標題）。
- **交付回報規範**：若未在雲端或本機實際跑過所有格子，回報時必須明確告知使用者，並附上驗證步驟與預期結果。
