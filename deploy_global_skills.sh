#!/usr/bin/env sh
# Deploy global skills from ai.agent_skills to all agent global skill directories
# Supports Claude Code, Antigravity, Codex, and OpenCode.
set -e
cd "$(dirname "$0")"

ts=$(date +%Y%m%d_%H%M%S)

deploy_skill() {
    skill_name="$1"
    target_dir="$2"
    src_file="$(pwd)/global/$skill_name/SKILL.md"
    dst_file="$target_dir/SKILL.md"

    if [ ! -f "$src_file" ]; then
        echo "[ERROR] Source skill file not found: $src_file"
        exit 1
    fi

    mkdir -p "$target_dir"

    if [ -f "$dst_file" ]; then
        if cmp -s "$src_file" "$dst_file"; then
            echo "[SKIP] $dst_file 已是最新"
        else
            cp "$dst_file" "$dst_file.$ts.bak"
            echo "[BACKUP] $dst_file.$ts.bak"
            cp "$src_file" "$dst_file"
            echo "[OK] $dst_file"
        fi
    else
        cp "$src_file" "$dst_file"
        echo "[OK] $dst_file"
    fi

    if [ -f "$(pwd)/global/$skill_name/LICENSE.txt" ]; then
        cp "$(pwd)/global/$skill_name/LICENSE.txt" "$target_dir/LICENSE.txt"
    fi
}

echo "[DEPLOY] 正在部署全域技能 (opencode-runner)..."

deploy_skill "opencode-runner" "$HOME/.claude/skills/opencode-runner"
deploy_skill "opencode-runner" "$HOME/.gemini/config/skills/opencode-runner"
deploy_skill "opencode-runner" "$HOME/.codex/skills/opencode-runner"
deploy_skill "opencode-runner" "$HOME/.config/opencode/skills/opencode-runner"

# 移除已下線的全域技能
for dep_dir in "$HOME/.claude/skills/frontend-design" "$HOME/.gemini/config/skills/frontend-design" "$HOME/.codex/skills/frontend-design" "$HOME/.config/opencode/skills/frontend-design"; do
    if [ -d "$dep_dir" ]; then
        rm -rf "$dep_dir"
        echo "[REMOVED] $dep_dir"
    fi
done

echo ""
echo "[DONE] 全域技能部署完成。"
