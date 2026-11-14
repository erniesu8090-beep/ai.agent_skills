# Local Jupyter Notebook Guide (Experiment & Tutorial)

Create clean, reproducible local Jupyter notebooks for two primary modes:

- **Experiments and exploratory analysis** (`experiment`)
- **Tutorials and teaching-oriented walkthroughs** (`tutorial`)

Prefer the bundled templates and the helper script (`scripts/new_notebook.py`) for consistent structure and fewer JSON mistakes.

## 1. Decision Tree
- If the request is exploratory, analytical, or hypothesis-driven, choose `experiment`.
- If the request is instructional, step-by-step, or audience-specific, choose `tutorial`.
- If editing an existing notebook, treat it as a refactor: preserve intent and improve structure.

## 2. Quick Start / Script Path

Call the bundled helper script directly relative to the skill path:

```bash
# Scaffold an experiment notebook
python "<path-to-skill>/scripts/new_notebook.py" \
  --kind experiment \
  --title "Compare prompt variants" \
  --out output/jupyter-notebook/compare-prompt-variants.ipynb

# Scaffold a tutorial notebook
python "<path-to-skill>/scripts/new_notebook.py" \
  --kind tutorial \
  --title "Intro to embeddings" \
  --out output/jupyter-notebook/intro-to-embeddings.ipynb
```

## 3. Standard Workflow

1. **Lock the intent**: Identify the notebook kind (`experiment` or `tutorial`). Capture the objective, audience, and what "done" looks like.
2. **Scaffold from the template**: Use `scripts/new_notebook.py` to avoid hand-authoring raw notebook JSON.
3. **Fill the notebook with small, runnable steps**:
   - Keep each code cell focused on one step.
   - Add short markdown cells that explain the purpose and expected result.
   - Avoid large, noisy outputs when a short summary works.
4. **Apply the right pattern**:
   - For experiments, follow `references/experiment-patterns.md`.
   - For tutorials, follow `references/tutorial-patterns.md`.
5. **Edit safely when working with existing notebooks**:
   - Preserve the notebook structure; avoid reordering cells unless it improves the top-to-bottom story.
   - Prefer targeted edits over full rewrites.
   - If you must edit raw JSON, review `references/notebook-structure.md` first.
6. **Validate the result**:
   - Run the notebook top-to-bottom when the environment allows, or run `scripts/colab_notebook.py validate <file.ipynb>` for JSON & Python AST syntax checks.
   - Use the final pass checklist in `references/quality-checklist.md`.

## 4. Templates & Dependencies
- Templates live in `assets/experiment-template.ipynb` and `assets/tutorial-template.ipynb`.
- The bundled scaffold script uses only the Python standard library.
- Optional Python packages for local notebook execution (prefer `uv`):
  ```bash
  uv pip install jupyterlab ipykernel
  ```
