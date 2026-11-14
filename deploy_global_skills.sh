#!/usr/bin/env sh
# Deploy global skills from ai.agent_skills to all agent global skill directories
# Supports Claude Code, Antigravity, Codex, and OpenCode.
set -e
cd "$(dirname "$0")"

ts=$(date +%Y%m%d_%H%M%S)

sync_file() {
    src_file="$1"
    dst_file="$2"
    mkdir -p "$(dirname "$dst_file")"

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
}

deploy_skill() {
    skill_name="$1"
    target_dir="$2"
    src_dir="$(pwd)/global/$skill_name"
    src_file="$src_dir/SKILL.md"

    if [ ! -f "$src_file" ]; then
        echo "[ERROR] Source skill file not found: $src_file"
        exit 1
    fi

    sync_file "$src_file" "$target_dir/SKILL.md"

    if [ -f "$src_dir/LICENSE.txt" ]; then
        sync_file "$src_dir/LICENSE.txt" "$target_dir/LICENSE.txt"
    fi

    if [ -d "$src_dir/scripts" ]; then
        for f in "$src_dir/scripts/"*; do
            [ -f "$f" ] || continue
            case "$f" in
                *.pyc) continue ;;
            esac
            sync_file "$f" "$target_dir/scripts/$(basename "$f")"
        done
    fi
}

echo "[DEPLOY] 正在部署全域技能 (opencode-runner, system-remnant-audit)..."

for skill_name in opencode-runner system-remnant-audit; do
    deploy_skill "$skill_name" "$HOME/.claude/skills/$skill_name"
    deploy_skill "$skill_name" "$HOME/.gemini/config/skills/$skill_name"
    deploy_skill "$skill_name" "$HOME/.codex/skills/$skill_name"
    deploy_skill "$skill_name" "$HOME/.config/opencode/skills/$skill_name"
done

# 移除已下線的全域技能
for dep_dir in "$HOME/.claude/skills/frontend-design" "$HOME/.gemini/config/skills/frontend-design" "$HOME/.codex/skills/frontend-design" "$HOME/.config/opencode/skills/frontend-design"; do
    if [ -d "$dep_dir" ]; then
        rm -rf "$dep_dir"
        echo "[REMOVED] $dep_dir"
    fi
done

echo ""
echo "[DONE] 全域技能部署完成。"
