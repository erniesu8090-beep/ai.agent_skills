---
name: frontend-suite
description: Comprehensive frontend UI/UX design, anti-AI-slop quality gates (Floor/Reflex/Finish), Audit/Redesign/Study modes, theming, React+shadcn bundling, and static/Playwright verification suite. Use when designing, building, auditing, redesigning, styling, or verifying web frontends, landing pages, dashboards, and interactive HTML artifacts.
license: Apache-2.0
---

# Frontend Suite (UI/UX Design, Anti-Slop Gates, Theming & Verification)

This skill provides a unified, production-grade toolkit for designing, auditing, redesigning, building, and verifying modern web user interfaces and interactive artifacts—integrating Anthropic frontend engineering patterns with `Nutlope/hallmark` v2 anti-AI-slop methodology and our warm-minimalist default aesthetic.

## Five Pillars Architecture

Depending on your task, refer to the corresponding sub-guide in `references/`:

| Pillar | Focus | Primary Sub-Guide | Key Assets / Scripts |
|---|---|---|---|
| **1. Visual Design & Aesthetic Direction** | Anti-AI slop philosophy, typography hierarchy, visual rhythm, copywriting | `references/design-principles.md` | Opinionated aesthetic guidelines |
| **2. Anti-Slop Gates & Operation Modes** | Pre-flight, Hero-first isolation, Floor/Reflex/Finish gates, Audit/Redesign/Study | `references/anti-slop-gates.md` | `scripts/slop_lint.py` |
| **3. Color Palettes & Font Pairing** | 10 curated themes, custom theme generation, hex codes | `references/theme-factory.md` | `themes/*.md`, `themes/theme-showcase.pdf` |
| **4. Component Engineering & Bundling** | React 18, TypeScript, Vite, Tailwind, 40+ shadcn/ui, single-file HTML | `references/web-artifacts.md` | `scripts/init-artifact.sh`, `scripts/bundle-artifact.sh`, `scripts/shadcn-components.tar.gz` |
| **5. Static & Browser Verification** | Static slop linting, Playwright browser automation, multi-viewport RWD checks | `references/webapp-testing.md` | `scripts/slop_lint.py`, `scripts/with_server.py`, `examples/*.py` |

---

## Mode Selection (Choose Before Writing Code)

| Mode | When to Use | Core Rule |
|---|---|---|
| **Build (新建)** | Building a new page, dashboard, or HTML tool from scratch | Follow the 5-step Golden Workflow below (Pre-flight → Theme → Hero-first → Build → Verify). |
| **Audit (唯讀體檢)** | Inspecting an existing UI for AI slop, accessibility, or layout flaws | Run `scripts/slop_lint.py` + `references/anti-slop-gates.md`; output Floor/Reflex/Finish report **without modifying source files**. |
| **Redesign (安全翻新)** | Overhauling an existing AI-slop UI while keeping logic intact | Follow Redesign Invariants in `references/anti-slop-gates.md`: preserve all `<a href>`, `<form>`, input names/IDs, handlers, and real data. |
| **Study (DNA 萃取)** | User supplies a reference site or screenshot | Extract color ratios, type scale, spacing rhythm, and focal restraint—never clone templates verbatim. |

---

## Recommended Golden Workflow (Build Mode)

### Step 1: Pre-flight & Aesthetic Grounding
- **Inventory & Truthfulness**: Read existing project tokens/styles first; ask the user for missing real copy, metrics, or images—never invent fake testimonials or placeholder stats.
- **Anti-AI Slop**: Avoid generic purple gradients, tech slate dark (`#0F172A`), pure white `#FFFFFF` glare, excessive centered cards, ALL-CAPS eyebrows above headings, middle-dot tags, and `transition: all`.
- **Subject-matter Specificity**: Ground choices in the product's actual job. For data/workplace dashboards, prefer warm off-white (`#FAF7F2`/`#F6F4EE`), graphite charcoal (`#1E2022`), crisp `1px` borders, and disciplined `rounded-md` corners.
- *Details*: See `references/design-principles.md` and `references/anti-slop-gates.md`.

### Step 2: Select Theme & Typography
- **Choose from 10 Curated Themes** (or use project/global palette): Inspect `themes/theme-showcase.pdf` or `themes/<theme-name>.md` (`arctic-frost`, `botanical-garden`, `desert-rose`, `forest-canopy`, `golden-hour`, `midnight-galaxy`, `modern-minimalist`, `ocean-depths`, `sunset-boulevard`, `tech-innovation`).
- **Custom Theme**: Follow `references/theme-factory.md` to define `:root` semantic tokens with 4–6 cohesive hex values and distinct display/body fonts.

### Step 3: Hero-First Isolation & Component Scaffolding
- **Hero-First Gate**: Build and inspect the Hero section in isolation first; expand into secondary sections only after visual hierarchy and tone pass review.
- **Full Stack Scaffolding (when React+shadcn is needed)**:
  ```bash
  bash scripts/init-artifact.sh <project-name>
  cd <project-name>
  ```
  Sets up React 18 + TypeScript + Vite + Tailwind CSS + 40+ pre-installed `shadcn/ui` components (Radix UI) with `@/` path aliases. For lightweight tools or controlled environments, single-file HTML + vanilla JS/Tailwind is equally supported.
- *Details*: See `references/web-artifacts.md`.

### Step 4: Bundle to Standalone HTML (Optional)
- **Compile & Inline Everything** (for React artifact projects):
  ```bash
  bash scripts/bundle-artifact.sh
  ```
  Creates a self-contained `bundle.html` ready for distribution or preview.

### Step 5: Static Linting & Multi-Viewport Verification
1. **Static Anti-Slop Check** (zero Node.js dependency, runs anywhere with Python 3):
   ```bash
   python scripts/slop_lint.py <html_or_dir>
   ```
   Resolve all **FLOOR** failures (`:focus-visible`, `prefers-reduced-motion`, viewport meta, `transition: all`, fake placeholder copy) and review **REFLEX** flags.
2. **Dynamic Browser & RWD Testing**:
   Use `scripts/with_server.py` to run Playwright checks across desktop (`1440px`), tablet (`768px`), and mobile (`375px`) viewports to verify zero horizontal overflow, >=44px touch targets, and live screenshots.
- *Details*: See `references/webapp-testing.md`.
