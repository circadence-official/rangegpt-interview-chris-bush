# LLM Leaderboard — Take-Home Interview

Welcome! This is a take-home coding exercise. You'll extend an existing full-stack application that tracks and compares AI language models.

## Time Expectation

This is a **1-hour** take-home exercise. Work at your own pace, but **do not spend more than 1 hour** on the coding portion. Afterward, we'll schedule a **10-minute live presentation** where you walk us through your work and answer a few questions.

## Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- OR: Node.js 22 + Python 3.12 + PostgreSQL 16 (see `SETUP_LOCAL.md`)

### Getting Started (Docker)

1. Clone this repo
2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
3. Start all services:
   ```bash
   docker compose up
   ```
4. Open [http://localhost:5173](http://localhost:5173) — the app should be running with sample data

**If setup takes more than 5 minutes or something isn't working, contact us. Setup time does NOT count toward your 1 hour.**

## Your Task

Open `tasks/FRONTEND.md` or `tasks/BACKEND.md` for your assignment.

## Technology

This project uses React 19, TypeScript, Vite, shadcn/ui, Tailwind CSS, SCSS, TanStack Query, Django 5, and DRF. Both Tailwind CSS and SCSS are available — use whichever you prefer or mix them.

**You are free to swap or add technologies as you see fit.** If you prefer a different state management library, component framework, or styling approach, go for it. Be ready to explain your choices in the presentation.

**You are welcome to use any AI tools** (Copilot, Cursor, ChatGPT, Claude, etc.). We evaluate your understanding of the code and decisions you make, not whether you typed every character. The presentation is where we assess ownership.

## How to Work

- **Commit incrementally** as you go (don't save everything for one big commit at the end)
- Use descriptive commit messages
- Prioritize what you think matters most — finishing everything is not the expectation

## Submission

1. Push your work to this repo
2. Fill in `RESPONSES.md` with your cross-stack answers and any notes
3. We'll reach out to schedule your 10-minute presentation

## About the Presentation

- **10 minutes total:** ~3 minutes for your walkthrough, ~5 minutes for our questions, ~2 minutes for your questions
- Be ready to share your screen and walk through the code you wrote
- We'll ask about your decisions, tradeoffs, and what you'd do differently — this is a conversation, not a test

## Accommodations

If you need accommodations (extra time, alternative format, accessibility needs), contact us before starting. We're happy to adjust.

## FAQ

**Can I install additional packages?**
Yes.

**What if I can't finish everything?**
That's expected. Prioritize what you think matters most.

**Can I restructure the existing code?**
Yes, if you think it's the right call. Be ready to explain why in your presentation.

**Does setup time count?**
No. Your 1 hour starts when you open the task file.

**What will you ask in the presentation?**
We'll ask you to walk through your code and explain your decisions. We may ask you to make a small change or explain how you'd approach something differently. It's a conversation, not a gotcha.
