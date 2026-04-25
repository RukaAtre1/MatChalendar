# 🍵 MatChalendar

**Local-first AI campus planner** — a calm, intelligent weekly planner for UCLA daily life.

> 計画　持続　均衡

MatChalendar is a one-screen demo of an AI planner-orchestrator that balances classes, meals, health, transportation, and carbon goals into one coherent weekly calendar. Designed around a matcha-latte washi aesthetic.

![MatChalendar Screenshot](https://img.shields.io/badge/status-demo-2c4a2e?style=flat-square)

---

## ✦ Quick Start

This is a **pure static site** — no build tools, no frameworks, no dependencies.

### Option 1: Just open it

Double-click `index.html` in your file explorer. Done.

### Option 2: Local dev server (live reload)

```bash
npx -y live-server --port=3000 --open=index.html
```

Then open [http://localhost:3000](http://localhost:3000).

---

## 📁 Project Structure

```
MatChalendar/
├── index.html            # App shell (single page)
├── styles.css            # Full design system (matcha-latte theme)
├── app.js                # Calendar logic, planner trace, drawer interaction
├── matcalendar-demo.html # Visual style reference (standalone landing page)
├── PRD_MatChalendar.md   # Product requirements document
└── README.md
```

## 🎨 Design

- **Color system**: washi · cream · matcha · muted gold
- **Typography**: Shippori Mincho B1 + Zen Kaku Gothic Antique + Noto Serif JP
- **Layout**: Three-panel (controls | calendar | explanation drawer), fits in one viewport
- **Interaction**: Click any calendar block → right drawer shows reason, impact, carbon delta, scores, and skills used

## ⚙️ How the Demo Works

1. Enter a natural-language goal in the left panel
2. Click **Run Planner** — a simulated planner trace animates through 7 steps
3. Calendar populates with class, meal, study, recovery, and wind-down blocks
4. Click any block → right drawer reveals the AI's reasoning, carbon impact, and skill attribution

## 🔧 Tech Stack

| Layer | Choice |
|-------|--------|
| Structure | Vanilla HTML |
| Styling | Vanilla CSS (no framework) |
| Logic | Vanilla JS (no framework) |
| Fonts | Google Fonts (loaded via CSS) |
| Server | Any static server or just open the file |

## 📄 License

Built for LA Hacks 2026.
