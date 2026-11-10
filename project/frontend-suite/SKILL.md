---
name: frontend-suite
description: Comprehensive frontend UI/UX design, theming, component engineering, and testing suite. Combines distinctive visual design principles (anti-AI slop), 10 curated color/typography themes (theme-factory), full-featured React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui component scaffolding with single-file HTML bundling (web-artifacts-builder), and Playwright-based browser visual testing and screenshot verification (webapp-testing). Use when designing, building, styling, beautifying, refactoring, or verifying web frontends, landing pages, dashboards, interactive artifacts, or GUI layouts.
license: Apache-2.0
---

# Frontend Suite (UI/UX Design, Theming, Scaffolding & Verification)

This skill provides a unified, production-grade toolkit for designing, styling, building, and verifying modern web user interfaces and interactive artifacts.

## Four Pillars Architecture

Depending on your task, refer to the corresponding sub-guide in `references/`:

| Pillar | Focus | Primary Sub-Guide | Key Assets / Scripts |
|---|---|---|---|
| **1. Visual Design & Aesthetic Direction** | Anti-AI slop, typography hierarchy, visual rhythm, copywriting | `references/design-principles.md` | Opinionated aesthetic guidelines |
| **2. Color Palettes & Font Pairing** | 10 curated themes, custom theme generation, hex codes | `references/theme-factory.md` | `themes/*.md`, `themes/theme-showcase.pdf` |
| **3. Component Engineering & Bundling** | React 18, TypeScript, Vite, Tailwind, 40+ shadcn/ui, single-file HTML | `references/web-artifacts.md` | `scripts/init-artifact.sh`, `scripts/bundle-artifact.sh`, `scripts/shadcn-components.tar.gz` |
| **4. Visual Testing & Verification** | Playwright browser automation, screenshots, RWD layout checks | `references/webapp-testing.md` | `scripts/with_server.py`, `examples/*.py` |

---

## Recommended Golden Workflow

Follow this 5-step workflow to build or revamp high-quality frontends:

### Step 1: Establish Visual Direction & Grounding
- **Anti-AI Slop**: Avoid excessive centered layouts, purple gradients, uniform rounded corners, and default Inter font.
- **Subject-matter Specificity**: Ground visual choices in the product's actual industry and audience before writing code.
- **Restraint**: "Spend your boldness in one place." Let one element be the memorable focal point while keeping the rest disciplined.
- **Typography & Structure**: Follow *The Elements of Typographic Style* (line length < 80 characters, deliberate weights, no random bold words in headings).
- *Details*: See `references/design-principles.md`.

### Step 2: Select Theme & Typography
- **Choose from 10 Curated Themes**: Inspect `themes/theme-showcase.pdf` or read `themes/<theme-name>.md` for specific hex palettes and font pairings:
  - `arctic-frost`: Cool, crisp winter-inspired theme.
  - `botanical-garden`: Fresh and organic garden palette.
  - `desert-rose`: Soft and sophisticated dusty tones.
  - `forest-canopy`: Natural and grounded earth tones.
  - `golden-hour`: Rich and warm autumnal palette.
  - `midnight-galaxy`: Dramatic and cosmic deep tones.
  - `modern-minimalist`: Clean and contemporary grayscale.
  - `ocean-depths`: Professional and calming maritime theme.
  - `sunset-boulevard`: Warm and vibrant sunset colors.
  - `tech-innovation`: Bold and modern tech aesthetic.
- **Generate Custom Theme**: If none fit, follow `references/theme-factory.md` to define semantic tokens with 4–6 cohesive hex values and matching display/body fonts.
- *Details*: See `references/theme-factory.md`.

### Step 3: Scaffold & Develop Components
- **Initialize Frontend Project**:
  ```bash
  bash scripts/init-artifact.sh <project-name>
  cd <project-name>
  ```
  Sets up React 18 + TypeScript + Vite + Tailwind CSS + 40+ pre-installed `shadcn/ui` components (Radix UI) with `@/` path aliases.
- **Develop Artifact**: Build clean, accessible, and responsive components following `references/web-artifacts.md`.
- **CSS Hygiene**: Watch out for selector specificity conflicts between structural tags and utility classes.

### Step 4: Bundle to Standalone HTML
- **Compile & Inline Everything**:
  ```bash
  bash scripts/bundle-artifact.sh
  ```
  Creates a self-contained `bundle.html` containing all inlined JavaScript, styles, and assets ready for distribution or iframe preview.
- *Details*: See `references/web-artifacts.md`.

### Step 5: Visual Verification & RWD Testing
- **Local Server & Headless Browser Automation**:
  Use `scripts/with_server.py` to launch the dev server and run Playwright scripts for visual validation:
  ```bash
  python scripts/with_server.py --server "npm run dev" --port 5173 -- python examples/element_discovery.py
  ```
- **Screenshot Checks**: Capture mobile/desktop viewports to verify that no text overflows, touch targets meet 44px minimums, and layouts adapt smoothly.
- *Details*: See `references/webapp-testing.md`.
