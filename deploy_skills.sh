#!/usr/bin/env sh
# Deploy global skills from ai.agent_skills to all agent global skill directories
# Supports Claude Code, Antigravity, and OpenCode.
set -e
cd "$(dirname "$0")"

ts=$(date +%Y%m%d_%H%M%S)

deploy_skill() {
    skill_name="$1"
    target_dir="$2"
    src_file="$(pwd)/$skill_name/SKILL.md"
    dst_file="$target_dir/SKILL.md"

    if [ ! -f "$src_file" ]; then
        echo "[ERROR] Source skill file not found: $src_file"
        exit 1
    fi

    mkdir -p "$target_dir"

    if [ -f "$dst_file" ]; then
        if cmp -s "$src_file" "$dst_file"; then
            echo "[SKIP] $dst_file 已是最新"
            return 0
        fi
        cp "$dst_file" "$dst_file.$ts.bak"
        echo "[BACKUP] $dst_file.$ts.bak"
    fi

    cp "$src_file" "$dst_file"
    echo "[OK] $dst_file"
}

echo "[DEPLOY] 正在部署全域技能 (opencode-runner)..."

deploy_skill "opencode-runner" "$HOME/.claude/skills/opencode-runner"
deploy_skill "opencode-runner" "$HOME/.gemini/config/skills/opencode-runner"
deploy_skill "opencode-runner" "$HOME/.config/opencode/skills/opencode-runner"

echo ""
echo "[DONE] 全域技能部署完成。"
