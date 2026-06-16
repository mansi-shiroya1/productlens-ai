# ProductLens AI
### Turn products into decisions.

> AI-powered PM analysis platform. 8 sections. Zero setup required with Demo Mode.

---

## Live Demo

Click **⚡ Load Demo** on the landing page — no API key needed. Loads a complete Spotify teardown instantly.

---

## What It Generates

| # | Section | What It Shows |
|---|---------|---------------|
| 1 | **Product Snapshot** | Summary, persona, user problem, value prop, north star metric, PM teardown insight |
| 2 | **KPI Framework** | Radar chart + Acquisition / Engagement / Retention / Business metrics with benchmarks |
| 3 | **Feature Opportunities** | Impact × Effort scatter matrix + priority table with PM scoring formula |
| 4 | **Competitive Analysis** | Multi-axis radar vs 2 competitors + strategic whitespace insights |
| 5 | **User Journey Map** | 6-stage lifecycle: user actions → pain points → PM opportunities |
| 6 | **Product Strategy** | Recommendations, risks, experiments, validation priorities, success metrics |
| 7 | **PRD Snippet** | Full Product Requirements Doc with P0/P1/P2 requirements + open questions |
| 8 | **Executive Memo** | CPO-level one-pager with downloadable .txt export |

---

## Quickstart

```bash
git clone https://github.com/yourusername/productlens-ai
cd productlens-ai
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501`. Hit **⚡ Load Demo** to see the full experience.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit 1.35+ with custom CSS (Apple × Notion × Stripe) |
| AI | OpenAI GPT-4o (JSON mode) |
| Charts | Plotly (radar, scatter matrix) |
| Data | Pandas |
| Fonts | Inter + Sora via Google Fonts |

---

## Deploy to Streamlit Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo → set `app.py` as main → Deploy
4. No secrets needed — API key is entered in-app per session

---

## Resume Bullet

```
ProductLens AI | AI Product Analytics Platform                              2024
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Built an 8-module AI product analysis platform (Streamlit + GPT-4o) that
  generates PM-quality teardowns — KPI frameworks, competitive radars, user
  journey maps, PRDs, and executive memos — from a single product name.

• Designed a zero-setup demo mode (pre-seeded Spotify analysis) enabling
  instant portfolio sharing without API key friction.

• Applied PM frameworks throughout: North Star Metric selection rationale,
  Impact × Effort prioritization scoring, hypothesis-driven experiment design,
  and P0/P1/P2 requirements structure.
```

---

## Project Decisions (Interview Talking Points)

**Why demo mode?** Recruiters and hiring managers need to see the output in under 10 seconds. Requiring an API key is a conversion killer. The Spotify teardown was chosen because it's a product every PM interviewer knows.

**Why 8 sections instead of 6?** Added Competitive Analysis and User Journey because those are the two frameworks most commonly asked about in PM interviews — and the two places where "AI wrapper" tools most often skip the real PM thinking.

**Why PRD?** It's the most PM-native artifact. A PM who can write a clean PRD spec — with goals, non-goals, prioritized requirements, and success metrics — signals actual PM competency, not just product awareness.

**What's the North Star Metric for this product?** Demo-to-live conversion rate. A user who runs a live analysis (not just demo) has found enough value to enter their API key — that's the signal.

---

*MIT License · Free to use and showcase*
