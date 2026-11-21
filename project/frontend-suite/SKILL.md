---
name: frontend-suite
description: Comprehensive frontend UI/UX design, theming, component engineering, anti-AI-slop polishing, and testing suite. Combines distinctive visual design principles (anti-AI slop), structured existing-UI unslop audit and 9-pass polishing workflow, 10 curated color/typography themes (theme-factory), React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui scaffolding with single-file HTML bundling (web-artifacts-builder), and Playwright visual testing (webapp-testing). Use when designing, building, unslopping, polishing, refactoring, or verifying web frontends, landing pages, dashboards, or GUI layouts.
license: Apache-2.0
---

# Frontend Suite (UI/UX Design, Unslop Polishing, Scaffolding & Verification)

This skill provides a unified, production-grade toolkit for designing, polishing, building, and verifying modern web user interfaces and interactive artifacts.

## Four Pillars Architecture

Depending on your task, refer to the corresponding sub-guide in `references/`:

| Pillar | Focus | Primary Sub-Guide | Key Assets / Scripts |
|---|---|---|---|
| **1. Visual Design & Unslop Polishing** | New-build anti-AI aesthetic principles + existing-UI slop audit & 9-pass polish | `references/design-principles.md`<br>`references/unslop-audit.md` | Opinionated design & redline checklist |
| **2. Color Palettes & Font Pairing** | 10 curated themes, custom theme generation, hex codes | `references/theme-factory.md` | `themes/*.md`, `themes/theme-showcase.pdf` |
| **3. Component Engineering & Bundling** | React 18, TypeScript, Vite, Tailwind, 40+ shadcn/ui, single-file HTML | `references/web-artifacts.md` | `scripts/init-artifact.sh`, `scripts/bundle-artifact.sh`, `scripts/shadcn-components.tar.gz` |
| **4. Visual Testing & Verification** | Playwright browser automation, screenshots, RWD layout checks | `references/webapp-testing.md` | `scripts/with_server.py`, `examples/*.py` |

---

## Workflow Router: Choose Your Mode

- **Mode A — New Build (0 → 1)**: Building a fresh app, dashboard, landing page, or interactive artifact → follow **Recommended Golden Workflow** below.
- **Mode B — Existing UI Unslop / Polish (Refurbish)**: Cleaning up an already-written, vibecoded, or AI-looking screen (purple gradients, glows, emoji labels, `transition-all`, arbitrary spacing, fake copy) → follow `references/unslop-audit.md`:
  1. **Audit & Classify**: Inspect the rendered screen/code against the slop tells table and classify as `Heavy slop` (full 9 passes), `Light slop` (Polish mode: fix only listed issues, keep brand), or `No slop` (report clean, propose at most 2–3 tiny tweaks).
  2. **5-Line Direction Gate**: Define `Product`, `Character`, `World`, `Moments`, and `Signature` and confirm with the user before editing.
  3. **9 Ordered Passes**: Execute across the whole screen in strict order: **1. Spacing (4px grid) → 2. Color (neutral ramp + 1 accent) → 3. Icons (no emoji, single line set) → 4. Copy → 5. Type (`tabular-nums`, weights 400–600) → 6. Layout → 7. Details (nested radius math, chart hierarchy, clean stat cards) → 8. Visuals → 9. Motion (no `transition-all` / `animate-pulse`)**.
  4. **Verify**: Run the checklist in `references/unslop-audit.md` and re-check rendered screenshots if available.

---

## Mode A: Recommended Golden Workflow (New Build)

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
