# AI Agent Skills (ai.agent_skills)

個人與跨專案共用的 AI Agent Skills（技能包集合），支援 Antigravity、Claude Code、OpenCode 等 AI Coding Agent 載入與協作。

## 技能清單

| 技能目錄 | 名稱 | 說明 |
|---|---|---|
| `gemini-web-imagegen/` | Gemini Web Image Generator CLI | 沿用 gemini.google.com 網頁登入額度的免 API 金鑰生圖與 Cookie 提取工具 |
| `google-flow-bridge/` | Google Flow Bridge | 跨專案調用 Google Flow 自動化生成圖片（Nano Banana 2K）或影片（Veo MP4） |
| `opencode-runner/` | OpenCode CLI Runner | 提供 OpenCode 子代理唯讀審查與防卡死調用安全規範 |

## 使用方式

各技能包含符合規格的 `SKILL.md`，可複製或軟連結至各 Agent 的技能目錄：
- **Antigravity**: `~/.gemini/antigravity/skills/` 或工作區技能目錄
- **Claude Code**: 各專案技能目錄或全域設定
- **OpenCode**: 各專案技能目錄
