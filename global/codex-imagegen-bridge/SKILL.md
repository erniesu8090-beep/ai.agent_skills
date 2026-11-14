---
name: codex-imagegen-bridge
description: Generate raster images from Antigravity, Claude Code, or OpenCode by delegating to the locally installed Codex CLI and its built-in $imagegen tool, using the existing ChatGPT login without an API key. Primary choice (Priority 1) whenever raster image generation is needed.
---

# Codex Image Generation Bridge (Priority 1)

Use the local Codex CLI as a helper agent when generating raster images from Antigravity, Claude Code, or OpenCode. Codex performs the image generation using its built-in `$imagegen` tool; the calling agent prepares the prompt, runs the command with closed/piped stdin, verifies the file, and reports its path.

## Preconditions

1. Confirm `codex` is available with `Get-Command codex` (or `command -v codex`).
2. Run `codex login status`. Continue only when the active login is ChatGPT, not API-key authentication.
3. If Codex is missing or not logged into ChatGPT, explain that the user needs to install Codex CLI or run `codex login` in a normal terminal, or fall back to Priority 2 (`agy-imagegen-bridge` / built-in `gemini-3.1-flash-image`). Do not ask for an API key and do not switch to `openai images`, `scripts/image_gen.py`, or another API fallback.
4. Never read, print, copy, or expose `%USERPROFILE%\.codex\auth.json`, access tokens, or other credential files.

## Generate an image

1. Resolve the project root and the exact output path. If the user did not give a path, use a new descriptive filename under `assets/generated/`. Do not overwrite an existing file; choose a versioned sibling name instead.
2. Create the destination directory if needed.
3. Build a concise image prompt that preserves the user's subject, style, framing, exact text, and exclusions. Include `$imagegen` literally at the very beginning so Codex selects its built-in image-generation skill. Include the absolute PNG destination and ask Codex to copy the finished image there.
4. **Always pipe the prompt via stdin using `-` (never pass positional `$prompt` with open stdin)** so `codex exec` receives immediate EOF and bypasses Windows `codex.cmd` (`%*`) argument quote-splitting:

   **Windows (PowerShell):**

   ```powershell
   $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
   $project = (Get-Location).Path
   $target = Join-Path $project 'assets\generated\image-name.png'
   New-Item -ItemType Directory -Force -Path (Split-Path -Parent $target) | Out-Null
   $prompt = '$imagegen Generate: [describe the requested image]. Save or copy the final PNG to ' + $target + '. Do not use an API key or API fallback.'
   $prompt | codex exec --skip-git-repo-check --sandbox workspace-write --cd $project -
   if ($LASTEXITCODE -ne 0) { throw 'Codex image generation failed.' }
   if (-not (Test-Path -LiteralPath $target)) { throw "Codex did not save the image to $target" }
   Get-Item -LiteralPath $target | Select-Object FullName, Length
   ```

   > Note: `[System.Text.UTF8Encoding]::new($false)` is required in Windows PowerShell 5.1 so non-ASCII prompts do not turn into `????` and no UTF-8 BOM (`\ufeff`) is prepended before `$imagegen`.

   **Linux / macOS (Bash / Zsh):**

   ```bash
   project="$(pwd)"
   target="$project/assets/generated/image-name.png"
   mkdir -p "$(dirname "$target")"
   prompt="\$imagegen Generate: [describe the requested image]. Save or copy the final PNG to $target. Do not use an API key or API fallback."
   printf '%s\n' "$prompt" | codex exec --skip-git-repo-check --sandbox workspace-write --cd "$project" -
   ```

   **Python (`subprocess.run`):**

   If invoking `codex` from Python, either pass `"-"` with `input=codex_prompt` (closed pipe EOF), or if passing `codex_prompt` as the final list argument, explicitly set `stdin=subprocess.DEVNULL`. Always use `--skip-git-repo-check --sandbox workspace-write --cd <project>` (never `--dangerously-skip-permissions`, which has been removed in newer Codex CLI versions).

5. Inspect the returned command result and verify the requested file exists and is a readable image. Codex may first save built-in image output under `%USERPROFILE%\.codex\generated_images` and then copy it to the requested project location; report only the verified project path.
6. Tell the user that generation uses their Codex/ChatGPT plan allowance. Do not promise a fixed number of images or a fixed quota cost.

## Permissions and troubleshooting

- **Prevent stdin hang (`Reading additional input from stdin...`)**: In non-interactive agent shells (`run_command`, CI, or background tasks), `codex exec` blocks indefinitely waiting for stdin EOF whenever stdin is an open pipe. Always use `$prompt | codex exec ... -` (or `stdin=subprocess.DEVNULL` / `< nul` if passing a positional prompt).
- **Prevent Windows `codex.cmd` quote-splitting**: `codex.cmd` forwards `%*`, so double quotes or multiline text in a positional PowerShell `$prompt` can split into `error: unexpected argument ...`. Piping via `-` eliminates this issue.
- `codex exec` must be able to use the user's existing Codex login and write its own session state. If the terminal sandbox blocks access to `%USERPROFILE%\.codex`, do not bypass the sandbox, copy credentials, or elevate permissions silently. Explain that the user can approve the specific command if the UI offers that option, or run the command from their normal PowerShell terminal.
- If `codex exec` says the directory is not trusted, retain `--skip-git-repo-check`; do not weaken the filesystem sandbox.
- Keep `--sandbox workspace-write`. Never use `--dangerously-bypass-approvals-and-sandbox` or `danger-full-access` for this workflow.
- If the built-in `$imagegen` tool is missing, stop and report that the installed Codex CLI/auth configuration does not expose it, or fall back to Priority 2 (`agy-imagegen-bridge` / `gemini-3.1-flash-image`). Do not silently switch to an API-backed image generator.
- If generation succeeds but the target is missing, inspect Codex's command output and generated-image path, then copy only the image created by this run. Do not guess filenames or overwrite user files.
