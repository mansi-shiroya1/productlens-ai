import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import datetime
from openai import OpenAI

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ProductLens AI — Turn products into decisions",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# DEMO DATA — Spotify (no API key needed)
# ─────────────────────────────────────────────
DEMO_PRODUCT = "Spotify"
DEMO_DATA = {
    "snapshot": {
        "summary": "Spotify is the world's largest audio streaming platform with 600M+ users across music, podcasts, and audiobooks. It operates a freemium model converting free listeners to Premium subscribers through personalized discovery and exclusive content.",
        "target_users": "18–34 year-old music enthusiasts who consume audio daily — commuters, gym-goers, students, and remote workers who want a personalized, ad-free listening experience across all their devices.",
        "user_problem": "Finding new music that matches your taste is overwhelming with millions of tracks available. Users also hate audio ads interrupting their flow state, and can't listen offline during commutes or travel.",
        "value_proposition": "Spotify makes every listening moment personal — it knows what you want to hear before you do, and it's available everywhere, always.",
        "north_star_metric": "Monthly Active Users (MAU)",
        "north_star_why": "MAU captures the full funnel — acquisition, activation, and retention — in a single number. Free users drive ad revenue and convert to Premium; Premium users drive subscription revenue. Both matter.",
        "category": "Entertainment / Audio",
        "stage": "Maturity",
        "confidence": "High",
        "teardown_insight": "Spotify's core moat is its recommendation engine, not its catalog. Apple Music has nearly the same songs. The question for any PM is: how do we deepen the taste graph faster than competitors can replicate it?"
    },
    "metrics": {
        "acquisition": [
            {"name": "Monthly Active Users", "value": "602M", "benchmark": "~300M (Apple Music)", "score": 9},
            {"name": "New User Growth (YoY)", "value": "14%", "benchmark": "Industry avg 8–10%", "score": 8},
            {"name": "App Store Rating", "value": "4.7 / 5.0", "benchmark": "4.5 category avg", "score": 9},
        ],
        "engagement": [
            {"name": "Daily Active Rate", "value": "~40% of MAU", "benchmark": "30% industry avg", "score": 8},
            {"name": "Avg Session Length", "value": "~30 min", "benchmark": "22 min (Pandora)", "score": 8},
            {"name": "Streams per DAU", "value": "~25 tracks/day", "benchmark": "18 (industry)", "score": 7},
        ],
        "retention": [
            {"name": "Premium Churn Rate", "value": "~4.8%/month", "benchmark": "5–6% SaaS median", "score": 7},
            {"name": "D30 Retention", "value": "~62%", "benchmark": "50% (streaming avg)", "score": 8},
            {"name": "Free→Premium Conversion", "value": "~26%", "benchmark": "15% freemium avg", "score": 9},
        ],
        "business": [
            {"name": "ARPU (Premium)", "value": "$4.97/month", "benchmark": "$10.99 (Apple Music)", "score": 5},
            {"name": "Gross Margin", "value": "~27%", "benchmark": "70%+ (Netflix)", "score": 4},
            {"name": "Revenue (2023)", "value": "€13.2B", "benchmark": "YoY +11%", "score": 7},
        ],
        "radar": {
            "Acquisition": 9, "Engagement": 8, "Retention": 7,
            "Monetization": 5, "Virality": 7, "NPS": 8
        }
    },
    "features": {
        "features": [
            {"feature": "Social Listening Rooms", "reason": "Gen Z users want shared listening experiences; Discord shows the demand for audio-social crossover", "impact": 8, "effort": 5, "priority_score": 6.4, "priority": "High"},
            {"feature": "AI Mood-Based Radio", "reason": "Users often don't know what they want to hear — an AI that reads context (time, weather, recent listens) removes decision fatigue", "impact": 9, "effort": 4, "priority_score": 8.1, "priority": "High"},
            {"feature": "Offline Podcast Highlights", "reason": "Podcast listeners want to save and share key moments, currently only possible with clunky workarounds", "impact": 7, "effort": 3, "priority_score": 7.0, "priority": "High"},
            {"feature": "Lyrics Karaoke Mode", "reason": "Existing lyrics feature is passive; interactive karaoke drives daily active use and differentiates vs Apple Music", "impact": 7, "effort": 5, "priority_score": 5.6, "priority": "Medium"},
            {"feature": "Artist Direct Merch Integration", "reason": "Closes the loop between fan discovery and purchase; adds a new high-margin revenue stream", "impact": 8, "effort": 7, "priority_score": 5.6, "priority": "Medium"},
            {"feature": "Cross-App Playlist Importer", "reason": "Reduces friction for Apple Music/YouTube switchers — removes the #1 barrier to switching", "impact": 9, "effort": 6, "priority_score": 7.2, "priority": "High"},
            {"feature": "Sleep Timer + Wind-Down Mode", "reason": "High-demand feature with 2M+ upvotes on community forum; low effort, high satisfaction win", "impact": 6, "effort": 2, "priority_score": 7.2, "priority": "High"},
            {"feature": "Fan Club Subscriptions", "reason": "Lets superfans pay artists directly; positions Spotify as the end-to-end artist economy platform", "impact": 9, "effort": 8, "priority_score": 6.3, "priority": "High"},
        ]
    },
    "strategy": {
        "recommendations": [
            {"title": "Double down on the social layer", "detail": "Spotify's taste graph is its moat but it's currently private. Making listening social — shared queues, listening parties, taste compatibility scores with friends — creates network effects that Apple Music and Tidal cannot replicate with catalog alone."},
            {"title": "Fix the monetization ceiling before growing users", "detail": "At $4.97 ARPU vs Apple Music's $10.99, Spotify leaves ~$6/user/month on the table. The priority should be a premium tier (Superfan / HiFi) with lossless audio and exclusive content, targeting the 26% of users who already pay — not the 74% who don't."},
            {"title": "Own the creator flywheel end-to-end", "detail": "Anchor.fm/Spotify for Podcasters gave Spotify distribution data. The next move is monetization tools — fan subscriptions, merch, live shows, tipping — turning Spotify from a consumption platform into a creator economy platform."},
        ],
        "risks": [
            {"title": "Label dependency is an existential risk", "detail": "~70% of Spotify's revenue goes to rights holders. Any label renegotiation can structurally compress margins. Mitigation: accelerate owned podcast and audiobook content to reduce licensed music's share of listening hours."},
            {"title": "AI music generation disrupts the catalog", "detail": "If AI-generated music becomes indistinguishable and royalty-free, the premium on licensed catalog collapses. Spotify should be testing AI music as a product feature, not waiting for it to happen to them."},
            {"title": "Platform concentration risk with Apple", "detail": "Apple can preference Apple Music on iOS through defaults, search placement, and Siri. Spotify's EU antitrust case is the right fight — but it's a long one. The hedge is deepening Android and smart speaker market share."},
        ],
        "validate_first": [
            {"title": "Will Premium users pay for a Superfan tier?", "detail": "Run a waitlist experiment for a $15.99/month HiFi + exclusive content tier. Measure conversion intent before building. Target: 5% of Premium base signals interest within 60 days."},
            {"title": "Does social listening increase retention?", "detail": "A/B test Shared Queue (co-listening) for 100K users. Primary metric: D30 retention delta. Hypothesis: users with ≥1 social listening session have 15% higher retention."},
            {"title": "Does cross-app import reduce churn at onboarding?", "detail": "Measure 7-day activation rate for new users who import a playlist vs those who don't. Hypothesis: playlist importers have 2x D7 retention because they have immediate value from day one."},
        ],
        "success_metrics": [
            {"metric": "Premium Subscriber ARPU", "target": "$6.50/month (+$1.53)", "timeframe": "12 months"},
            {"metric": "Free→Premium Conversion", "target": "30% (+4pp)", "timeframe": "6 months"},
            {"metric": "Social Feature DAU Adoption", "target": "15% of DAU using ≥1 social feature", "timeframe": "9 months"},
        ],
        "experiments": [
            {"title": "Social Queue A/B Test", "hypothesis": "If we enable shared listening queues for friend pairs, then D30 retention will increase by 12% because music becomes a coordination mechanism, not just a solo activity."},
            {"title": "Superfan Tier Waitlist", "hypothesis": "If we offer a $15.99 HiFi + exclusives tier to existing Premium users, then ≥5% will join the waitlist in 30 days because a meaningful subset of superfans are underserved by the current single Premium tier."},
            {"title": "Onboarding Playlist Import Prompt", "hypothesis": "If we surface an Apple Music / YouTube playlist importer at step 2 of onboarding, then D7 retention will increase by 18% because users with existing libraries activate faster."},
        ]
    },
    "memo": {
        "problem": "Spotify has 602M users but captures only $4.97/month ARPU from paying subscribers — less than half of Apple Music's $10.99. The platform has a user scale problem solved, and a monetization density problem that remains unsolved.",
        "user": "The underserved user is the Superfan: someone who streams 3+ hours daily, follows 50+ artists, and attends live shows. They exist within Spotify's current Premium base and are willing to pay more — they just haven't been given a reason to.",
        "solution": "Launch a Spotify Superfan tier at $15.99/month offering lossless HiFi audio, early access to concert tickets, exclusive artist content, and a social listening room feature. This targets the top 10–15% of current Premium subscribers without cannibalizing the base tier.",
        "metrics": "Primary: ARPU lift from $4.97 to $6.50 within 12 months. Secondary: Superfan tier adoption ≥8% of existing Premium base within 6 months. Guardrail: no increase in overall Premium churn rate.",
        "decision": "Prioritize the Superfan tier roadmap in H1 next year. Run a waitlist experiment in Q1 to validate price sensitivity. If ≥5% of Premium users join the waitlist, greenlight full development. This is a revenue density play, not a user growth play."
    },
    "competitive": {
        "products": ["Spotify", "Apple Music", "YouTube Music"],
        "dimensions": ["Catalog Size", "Personalization", "Social Features", "Podcast Library", "Price Value", "Offline Experience", "Artist Tools", "UX Quality"],
        "scores": {
            "Spotify":      [8, 9, 6, 9, 8, 8, 7, 8],
            "Apple Music":  [9, 7, 3, 5, 7, 9, 4, 9],
            "YouTube Music":[9, 7, 4, 4, 9, 6, 5, 7],
        },
        "insights": [
            "Spotify leads on personalization and podcast library — its clearest moats.",
            "Apple Music wins on catalog completeness and offline reliability (device integration advantage).",
            "YouTube Music's unlimited catalog and free tier makes it the price-sensitive user's choice.",
            "Social features are the biggest whitespace across all three — a greenfield opportunity.",
        ]
    },
    "user_journey": {
        "stages": ["Discover", "Onboard", "First Listen", "Habit Formation", "Upgrade Decision", "Long-Term Retention"],
        "actions": [
            "Sees Spotify ad or friend recommendation",
            "Downloads app, creates account, picks 3 artists",
            "Gets auto-generated playlist, starts listening",
            "Discovers Wrapped, Discover Weekly, Daily Mix",
            "Hits free-tier ad wall during gym session",
            "Subscribes; explores podcasts and audiobooks"
        ],
        "pain_points": [
            "Ad fatigue at low frequency — first ad can come within 10 min",
            "Onboarding asks for genre preferences but ignores mood context",
            "Shuffle-only on free tier frustrates users who want control",
            "No social proof for new music ('my friend loves this' is missing)",
            "Price anchoring — $9.99 feels steep without a trial comparison",
            "Library management is clunky; hard to find saved songs"
        ],
        "opportunities": [
            "Contextual first ad delay (first 30 min ad-free to build habit)",
            "Mood-first onboarding ('How are you feeling?') for better Day 1 recs",
            "Give free users 3 'song unlocks' per day to drive Premium aspiration",
            "Friend activity feed showing what your network is obsessed with",
            "Free trial default; show Premium value before asking for card",
            "Redesigned library with smart folders and pinned playlists"
        ]
    },
    "prd": {
        "feature": "Spotify Superfan Tier",
        "status": "Proposed — Awaiting Validation",
        "owner": "Growth & Monetization PM",
        "problem": "Spotify's single Premium tier leaves revenue on the table from its most engaged users. Superfans (top 15% by listening hours) are undermonetized and have no meaningful differentiation from casual Premium subscribers.",
        "goals": [
            "Increase ARPU from $4.97 to $6.50 within 12 months",
            "Achieve 8% adoption among existing Premium users in 6 months",
            "Maintain Premium churn at current 4.8% or below"
        ],
        "non_goals": [
            "This is not a free-tier conversion play — target is existing Premium subscribers only",
            "This is not a full rebrand of Premium — the base tier remains unchanged",
            "This does not include artist payouts restructuring in v1"
        ],
        "requirements": [
            {"priority": "P0", "requirement": "HiFi lossless audio (FLAC / 24-bit) on all devices"},
            {"priority": "P0", "requirement": "Superfan badge visible on profile and in social features"},
            {"priority": "P1", "requirement": "Early access window (48hrs) for concert ticket purchases"},
            {"priority": "P1", "requirement": "Shared listening rooms (co-listen with up to 5 friends simultaneously)"},
            {"priority": "P2", "requirement": "Exclusive artist content drops (acoustic sessions, demos, behind-the-scenes)"},
            {"priority": "P2", "requirement": "Extended download cache (10K songs vs 5K on standard Premium)"},
        ],
        "success_metrics": [
            "Superfan tier adoption rate among Premium base (target: 8% in 6mo)",
            "ARPU delta vs control group (target: +$6.02/month)",
            "D90 retention for Superfan subscribers vs standard Premium (target: +8pp)",
            "NPS delta for Superfan tier (target: ≥60 NPS)"
        ],
        "open_questions": [
            "Should we offer annual billing discount (e.g., $149.99/yr) from launch?",
            "How do we handle family plan users — per-seat upgrade or household?",
            "Do we announce HiFi publicly before launch to manage label negotiations?"
        ]
    }
}

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;1,14..32,400&family=Sora:wght@300;400;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #F7F9FF !important;
    font-family: 'Inter', sans-serif;
    color: #0F172A;
}
[data-testid="stAppViewContainer"] > .main { background: #F7F9FF !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid rgba(148,163,184,0.15) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

/* ── Nav ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 32px;
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(148,163,184,0.1);
    margin: -6rem -4rem 2.5rem -4rem;
    position: sticky;
    top: 0;
    z-index: 99;
}
.nav-logo {
    font-family: 'Sora', sans-serif;
    font-size: 16px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.4px;
}
.nav-logo .accent {
    background: linear-gradient(135deg, #3B82F6, #6366F1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.nav-pill {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 20px;
}
.pill-demo { background: #FEF3C7; color: #92400E; }
.pill-ai   { background: #EFF6FF; color: #1D4ED8; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 72px 24px 56px;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    font-weight: 700;
    color: #3B82F6;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    margin-bottom: 24px;
}
.hero-h1 {
    font-family: 'Sora', sans-serif;
    font-size: clamp(40px, 6vw, 68px);
    font-weight: 800;
    letter-spacing: -2.5px;
    line-height: 1.06;
    color: #0F172A;
    margin-bottom: 20px;
}
.hero-h1 .grad {
    background: linear-gradient(135deg, #3B82F6 0%, #6366F1 60%, #8B5CF6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 17px;
    font-weight: 400;
    color: #64748B;
    max-width: 500px;
    margin: 0 auto 44px;
    line-height: 1.7;
}
.hero-input-wrap {
    background: white;
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 20px;
    padding: 28px 28px 24px;
    max-width: 600px;
    margin: 0 auto;
    box-shadow: 0 4px 30px rgba(15,23,42,0.07);
}
.demo-notice {
    background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
    border: 1px solid #FDE68A;
    border-radius: 10px;
    padding: 11px 16px;
    font-size: 13px;
    color: #78350F;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    justify-content: center;
    margin-top: 20px;
}
.chip {
    font-size: 12.5px;
    font-weight: 500;
    color: #475569;
    background: #F1F5F9;
    border: 1px solid #E2E8F0;
    padding: 6px 13px;
    border-radius: 20px;
}

/* ── Confidence badge ── */
.conf-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 6px;
    margin-left: 8px;
    vertical-align: middle;
}
.conf-high   { background: #F0FDF4; color: #16A34A; }
.conf-medium { background: #FFF7ED; color: #EA580C; }
.conf-ai     { background: #F5F3FF; color: #7C3AED; }

/* ── Section header ── */
.sec-hdr {
    margin-bottom: 28px;
    padding-bottom: 14px;
    border-bottom: 1px solid #E2E8F0;
}
.sec-eye {
    font-size: 10.5px;
    font-weight: 700;
    color: #3B82F6;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.sec-title {
    font-family: 'Sora', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -0.4px;
}
.sec-sub {
    font-size: 13.5px;
    color: #64748B;
    margin-top: 4px;
    font-style: italic;
}

/* ── Premium card ── */
.pcard {
    background: white;
    border: 1px solid rgba(148,163,184,0.17);
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 1px 8px rgba(15,23,42,0.04);
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.18s, transform 0.18s;
}
.pcard:hover {
    box-shadow: 0 6px 24px rgba(15,23,42,0.08);
    transform: translateY(-1px);
}
.pcard::before {
    content:'';
    position:absolute;
    top:0;left:0;right:0;
    height:3px;
    background: linear-gradient(90deg,#3B82F6,#6366F1);
    opacity:0;
    transition: opacity 0.18s;
}
.pcard:hover::before { opacity:1; }
.pcard-icon  { font-size:26px; margin-bottom:10px; display:block; }
.pcard-label { font-size:10.5px; font-weight:700; color:#94A3B8; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:6px; }
.pcard-title { font-family:'Sora',sans-serif; font-size:15px; font-weight:700; color:#0F172A; margin-bottom:7px; letter-spacing:-0.2px; }
.pcard-body  { font-size:13.5px; color:#475569; line-height:1.65; }

/* ── Insight callout ── */
.insight-box {
    background: linear-gradient(135deg, #EFF6FF, #F5F3FF);
    border: 1px solid #C7D7FF;
    border-radius: 12px;
    padding: 18px 22px;
    margin-top: 6px;
}
.insight-label {
    font-size: 10.5px;
    font-weight: 700;
    color: #6366F1;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.insight-body {
    font-size: 13.5px;
    color: #3730A3;
    line-height: 1.6;
    font-style: italic;
}

/* ── Metric card ── */
.mcard {
    background: white;
    border: 1px solid rgba(148,163,184,0.17);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 1px 6px rgba(15,23,42,0.04);
}
.mcard-val   { font-family:'Sora',sans-serif; font-size:22px; font-weight:800; color:#0F172A; letter-spacing:-0.8px; line-height:1; margin-bottom:4px; }
.mcard-name  { font-size:11px; font-weight:600; color:#94A3B8; text-transform:uppercase; letter-spacing:0.7px; }
.mcard-bench { font-size:11.5px; color:#64748B; margin-top:6px; }
.prog-track  { background:#F1F5F9; border-radius:5px; height:6px; overflow:hidden; margin-top:10px; }
.prog-fill   { height:100%; border-radius:5px; background:linear-gradient(90deg,#3B82F6,#6366F1); }

/* ── Progress bar block ── */
.pbar-block  { background:white; border:1px solid rgba(148,163,184,0.17); border-radius:12px; padding:16px 20px; margin-bottom:10px; }
.pbar-row    { display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; }
.pbar-name   { font-size:13px; font-weight:600; color:#1E293B; }
.pbar-score  { font-size:13px; font-weight:700; color:#3B82F6; }

/* ── Strategy card ── */
.scard {
    background: white;
    border: 1px solid rgba(148,163,184,0.17);
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 12px;
    box-shadow: 0 1px 6px rgba(15,23,42,0.03);
}
.stag {
    display:inline-block;
    font-size:10.5px;
    font-weight:700;
    letter-spacing:0.7px;
    text-transform:uppercase;
    padding:3px 9px;
    border-radius:5px;
    margin-bottom:9px;
}
.t-rec    { background:#EFF6FF; color:#2563EB; }
.t-risk   { background:#FFF7ED; color:#C2410C; }
.t-valid  { background:#F0FDF4; color:#15803D; }
.t-metric { background:#FAF5FF; color:#7E22CE; }
.t-exp    { background:#FFFBEB; color:#B45309; }

/* ── Journey ── */
.journey-stage {
    background: white;
    border: 1px solid rgba(148,163,184,0.17);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 10px;
    box-shadow: 0 1px 6px rgba(15,23,42,0.03);
}
.journey-label { font-size:10px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:1px; margin-bottom:4px; }
.journey-stage-name { font-family:'Sora',sans-serif; font-size:15px; font-weight:700; color:#0F172A; margin-bottom:10px; }
.journey-action { font-size:13px; color:#475569; margin-bottom:8px; }
.pain-tag { display:inline-block; background:#FFF1F2; color:#BE123C; font-size:11.5px; font-weight:500; padding:4px 10px; border-radius:6px; margin-bottom:8px; }
.opp-tag  { display:inline-block; background:#F0FDF4; color:#15803D; font-size:11.5px; font-weight:500; padding:4px 10px; border-radius:6px; }

/* ── PRD ── */
.prd-wrap {
    background:white;
    border:1px solid rgba(148,163,184,0.17);
    border-radius:16px;
    padding:36px 42px;
    max-width:860px;
    margin:0 auto;
    box-shadow:0 4px 24px rgba(15,23,42,0.06);
}
.prd-header { border-bottom:2px solid #F1F5F9; padding-bottom:22px; margin-bottom:28px; }
.prd-stamp { font-size:10.5px; font-weight:700; color:#3B82F6; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:5px; }
.prd-title { font-family:'Sora',sans-serif; font-size:26px; font-weight:800; color:#0F172A; letter-spacing:-0.7px; }
.prd-meta  { font-size:12px; color:#94A3B8; margin-top:6px; }
.prd-sec-label { font-size:10.5px; font-weight:700; color:#3B82F6; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; margin-top:24px; }
.prd-body  { font-size:14px; color:#334155; line-height:1.7; }
.prd-req   { display:flex; align-items:flex-start; gap:12px; padding:10px 14px; border-radius:8px; margin-bottom:6px; background:#F8FAFF; border:1px solid #E2E8F0; }
.prd-p0    { font-size:11px; font-weight:700; color:white; background:#EF4444; padding:2px 7px; border-radius:4px; flex-shrink:0; margin-top:2px; }
.prd-p1    { font-size:11px; font-weight:700; color:white; background:#F59E0B; padding:2px 7px; border-radius:4px; flex-shrink:0; margin-top:2px; }
.prd-p2    { font-size:11px; font-weight:700; color:white; background:#3B82F6; padding:2px 7px; border-radius:4px; flex-shrink:0; margin-top:2px; }
.prd-req-text { font-size:13.5px; color:#334155; line-height:1.5; }
.prd-oq   { font-size:13.5px; color:#475569; padding:9px 14px; background:#FFFBEB; border:1px solid #FDE68A; border-radius:7px; margin-bottom:7px; }
.prd-decision {
    background:linear-gradient(135deg,#EFF6FF,#F5F3FF);
    border:1px solid #BFDBFE;
    border-radius:12px;
    padding:20px 24px;
    margin-top:28px;
}
.prd-dec-label { font-size:10.5px; font-weight:700; color:#6366F1; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:8px; }
.prd-dec-body  { font-size:14.5px; font-weight:500; color:#1E293B; line-height:1.6; }

/* ── Memo ── */
.memo-wrap {
    background:white;
    border:1px solid rgba(148,163,184,0.17);
    border-radius:18px;
    padding:38px 46px;
    max-width:800px;
    margin:0 auto;
    box-shadow:0 4px 24px rgba(15,23,42,0.06);
}
.memo-hdr { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:32px; padding-bottom:22px; border-bottom:2px solid #F1F5F9; }
.memo-stamp { font-size:10.5px; font-weight:700; color:#3B82F6; letter-spacing:1.5px; text-transform:uppercase; margin-bottom:5px; }
.memo-product { font-family:'Sora',sans-serif; font-size:26px; font-weight:800; color:#0F172A; letter-spacing:-0.7px; }
.memo-meta { text-align:right; font-size:11.5px; color:#94A3B8; line-height:1.9; }
.memo-sec { margin-bottom:26px; }
.memo-sec-label { font-size:10.5px; font-weight:700; color:#3B82F6; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:7px; }
.memo-sec-body  { font-size:14.5px; color:#334155; line-height:1.7; }
.memo-decision  { background:linear-gradient(135deg,#EFF6FF,#F5F3FF); border:1px solid #BFDBFE; border-radius:12px; padding:20px 24px; margin-top:26px; }
.memo-dec-label { font-size:10.5px; font-weight:700; color:#6366F1; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:7px; }
.memo-dec-body  { font-size:14.5px; font-weight:500; color:#1E293B; line-height:1.6; }

/* ── Complete banner ── */
.done-banner {
    background:linear-gradient(135deg,#EFF6FF,#F5F3FF);
    border:1px solid #BFDBFE;
    border-radius:12px;
    padding:16px 22px;
    display:flex;
    align-items:center;
    gap:12px;
    margin-bottom:28px;
}
.done-icon { font-size:22px; flex-shrink:0; }
.done-text strong { display:block; font-size:14px; font-weight:700; color:#1E40AF; margin-bottom:1px; }
.done-text span   { font-size:12.5px; color:#3B82F6; }

/* ── Divider ── */
.sec-div {
    height:1px;
    background:linear-gradient(90deg,transparent,#E2E8F0,transparent);
    margin: 52px 0;
}

/* ── Sidebar nav ── */
.sb-logo {
    padding: 22px 20px 10px;
    font-family:'Sora',sans-serif;
    font-size:15px;
    font-weight:800;
    color:#0F172A;
    letter-spacing:-0.3px;
    border-bottom:1px solid #F1F5F9;
    margin-bottom:8px;
}
.sb-logo .accent {
    background:linear-gradient(135deg,#3B82F6,#6366F1);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.sb-section { padding:6px 16px 2px; font-size:10px; font-weight:700; color:#94A3B8; letter-spacing:1.2px; text-transform:uppercase; }
.sb-link {
    display:flex;
    align-items:center;
    gap:9px;
    padding:9px 20px;
    font-size:13px;
    font-weight:500;
    color:#475569;
    border-radius:0;
    cursor:pointer;
    transition:all 0.12s;
    border-left:3px solid transparent;
    margin-bottom:1px;
}
.sb-link:hover { background:#F8FAFF; color:#0F172A; border-left-color:#CBD5E1; }
.sb-link.active { background:#EFF6FF; color:#2563EB; font-weight:600; border-left-color:#3B82F6; }
.sb-footer {
    padding:16px 20px;
    font-size:11px;
    color:#94A3B8;
    border-top:1px solid #F1F5F9;
    margin-top:auto;
    line-height:1.6;
}

/* ── Comp table ── */
.comp-winner { color:#16A34A; font-weight:700; }
.comp-loser  { color:#EF4444; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg,#3B82F6,#6366F1) !important;
    color:white !important;
    border:none !important;
    border-radius:11px !important;
    padding:13px 28px !important;
    font-family:'Inter',sans-serif !important;
    font-size:14.5px !important;
    font-weight:600 !important;
    width:100% !important;
    box-shadow:0 4px 14px rgba(99,102,241,0.28) !important;
    transition:all 0.18s !important;
    letter-spacing:-0.1px !important;
}
.stButton > button:hover {
    transform:translateY(-1px) !important;
    box-shadow:0 6px 20px rgba(99,102,241,0.38) !important;
}
.stTextInput > div > div > input {
    border:1.5px solid #E2E8F0 !important;
    border-radius:11px !important;
    padding:13px 17px !important;
    font-family:'Inter',sans-serif !important;
    font-size:14.5px !important;
    color:#0F172A !important;
    background:#FAFBFF !important;
}
.stTextInput > div > div > input:focus {
    border-color:#3B82F6 !important;
    box-shadow:0 0 0 3px rgba(59,130,246,0.1) !important;
    outline:none !important;
}
.stTextInput > div > div > input::placeholder { color:#94A3B8 !important; }
.stTabs [data-baseweb="tab-list"] {
    gap:3px; background:#F1F5F9; border-radius:11px; padding:4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius:8px; padding:7px 16px; font-size:12.5px; font-weight:600; color:#64748B;
}
.stTabs [aria-selected="true"] {
    background:white !important; color:#0F172A !important;
    box-shadow:0 1px 4px rgba(15,23,42,0.07);
}
.stSelectbox > div > div {
    border-radius:11px !important;
    border:1.5px solid #E2E8F0 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key": "",
        "product_input": "",
        "demo_mode": False,
        "analysis_done": False,
        "snapshot": None,
        "metrics": None,
        "features": None,
        "strategy": None,
        "memo": None,
        "competitive": None,
        "user_journey": None,
        "prd": None,
        "active_section": "snapshot",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# OPENAI HELPER
# ─────────────────────────────────────────────
def call_gpt(system_prompt: str, user_prompt: str) -> dict:
    client = OpenAI(api_key=st.session_state.api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.72,
        max_tokens=2200,
    )
    return json.loads(response.choices[0].message.content)


# ─────────────────────────────────────────────
# GENERATION FUNCTIONS
# ─────────────────────────────────────────────
def generate_snapshot(product: str) -> dict:
    sys = """You are a Senior Product Manager at a top-tier tech company doing a product teardown.
Return ONLY valid JSON:
{
  "summary": "2-3 sentence product description covering what it does, business model, and scale",
  "target_users": "Specific user persona with demographics, context, and key behaviors",
  "user_problem": "The core unmet need — be specific, not generic",
  "value_proposition": "Single sentence: clear, compelling, differentiated",
  "north_star_metric": "The ONE metric that captures product health",
  "north_star_why": "Why this metric, not others — include trade-offs considered",
  "category": "Product category",
  "stage": "Growth|Maturity|Decline|Launch",
  "confidence": "High|Medium",
  "teardown_insight": "The one contrarian or non-obvious PM insight about this product's real competitive moat or strategic risk"
}"""
    return call_gpt(sys, f"Analyze this product for a PM interview teardown: {product}")


def generate_metrics(product: str) -> dict:
    sys = """You are a product analytics lead. Return ONLY valid JSON with realistic, specific metrics:
{
  "acquisition": [{"name":"","value":"","benchmark":"","score":7}],
  "engagement":  [{"name":"","value":"","benchmark":"","score":8}],
  "retention":   [{"name":"","value":"","benchmark":"","score":6}],
  "business":    [{"name":"","value":"","benchmark":"","score":7}],
  "radar": {"Acquisition":7,"Engagement":8,"Retention":6,"Monetization":7,"Virality":5,"NPS":8}
}
- 3-4 metrics per category
- Values must be specific and realistic (not "varies")
- Benchmarks must name the comparison (competitor or industry)
- Scores 1-10"""
    return call_gpt(sys, f"Generate a rigorous KPI framework for: {product}")


def generate_features(product: str) -> dict:
    sys = """You are a product strategist running a feature prioritization sprint. Return ONLY valid JSON:
{
  "features": [
    {
      "feature": "Feature name",
      "reason": "User need + market signal that justifies this (cite a real pattern)",
      "impact": 8,
      "effort": 4,
      "priority_score": 8.4,
      "priority": "High"
    }
  ]
}
- Generate exactly 8 features
- Priority score = impact * (11 - effort) / 10, 1 decimal
- Priority: High>=6.5, Medium 4-6.4, Low<4
- Reason must reference a real user behavior or market signal"""
    return call_gpt(sys, f"Feature opportunities for: {product}")


def generate_strategy(product: str) -> dict:
    sys = """You are a VP of Product writing a board strategy brief. Return ONLY valid JSON:
{
  "recommendations": [{"title":"","detail":""}],
  "risks": [{"title":"","detail":""}],
  "validate_first": [{"title":"","detail":""}],
  "success_metrics": [{"metric":"","target":"","timeframe":""}],
  "experiments": [{"title":"","hypothesis":""}]
}
- 3 items per category
- Recommendations must be specific and opinionated, not generic
- Risks must name the mitigation strategy
- Experiments must follow: if [action], then [outcome], because [mechanism]"""
    return call_gpt(sys, f"Executive product strategy for: {product}")


def generate_memo(product: str, snapshot: dict, strategy: dict) -> dict:
    sys = """You are a Chief Product Officer writing a board-level product memo. Return ONLY valid JSON:
{
  "problem": "Crisp problem statement with quantification where possible",
  "user": "User description with the key insight about what they really need",
  "solution": "Recommended approach — specific, not vague",
  "metrics": "Primary KPI, secondary KPI, and guardrail metric",
  "decision": "Clear, confident, time-bound product decision"
}"""
    return call_gpt(sys, f"Product: {product}\nContext: {json.dumps(snapshot)}\nStrategy: {json.dumps(strategy)}\nWrite the executive memo.")


def generate_competitive(product: str) -> dict:
    sys = """You are a product strategist. Return ONLY valid JSON:
{
  "products": ["ProductA","Competitor1","Competitor2"],
  "dimensions": ["dim1","dim2","dim3","dim4","dim5","dim6","dim7","dim8"],
  "scores": {
    "ProductA": [7,8,6,9,7,8,7,8],
    "Competitor1": [8,6,5,7,8,9,5,9],
    "Competitor2": [7,6,4,5,9,6,5,7]
  },
  "insights": ["insight1","insight2","insight3","insight4"]
}
- dimensions must be relevant to this product category (not generic)
- scores 1-10, realistic based on actual product knowledge
- insights must identify clear whitespace or strategic opportunity"""
    return call_gpt(sys, f"Competitive landscape for: {product}")


def generate_user_journey(product: str) -> dict:
    sys = """You are a UX researcher and PM. Return ONLY valid JSON:
{
  "stages": ["Stage1","Stage2","Stage3","Stage4","Stage5","Stage6"],
  "actions": ["what user does at each stage"],
  "pain_points": ["specific pain at each stage"],
  "opportunities": ["PM opportunity to fix each pain"]
}
- Exactly 6 stages covering the full user lifecycle
- Pain points must be specific and real (not generic)
- Opportunities must be concrete and actionable"""
    return call_gpt(sys, f"User journey map for: {product}")


def generate_prd(product: str, snapshot: dict, features: dict) -> dict:
    sys = """You are a Senior PM writing a PRD. Return ONLY valid JSON:
{
  "feature": "Feature or initiative name",
  "status": "Proposed|In Discovery|Spec Review",
  "owner": "PM role",
  "problem": "Problem statement with quantification",
  "goals": ["goal1","goal2","goal3"],
  "non_goals": ["non-goal1","non-goal2","non-goal3"],
  "requirements": [
    {"priority":"P0","requirement":"description"},
    {"priority":"P1","requirement":"description"},
    {"priority":"P2","requirement":"description"}
  ],
  "success_metrics": ["metric1","metric2","metric3","metric4"],
  "open_questions": ["question1","question2","question3"]
}
- Feature should be the highest-priority opportunity
- Requirements: 2x P0, 2x P1, 2x P2
- Questions must be real open decisions the team would face"""
    top_feature = features.get("features", [{}])[0].get("feature", "top feature")
    return call_gpt(sys, f"Write a PRD for {product}, focusing on: {top_feature}")


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def build_radar(radar_data: dict) -> go.Figure:
    cats = list(radar_data.keys())
    vals = list(radar_data.values())
    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats + [cats[0]],
        fill='toself',
        fillcolor='rgba(99,102,241,0.09)',
        line=dict(color='#6366F1', width=2.5),
        marker=dict(size=7, color='#6366F1', line=dict(color='white', width=2)),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,10],
                tickfont=dict(size=10, color='#94A3B8', family='Inter'),
                gridcolor='rgba(148,163,184,0.18)', linecolor='rgba(148,163,184,0.18)'),
            angularaxis=dict(
                tickfont=dict(size=12, color='#374151', family='Inter'),
                gridcolor='rgba(148,163,184,0.18)', linecolor='rgba(148,163,184,0.18)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, margin=dict(t=28,b=28,l=60,r=60), height=380,
    )
    return fig


def build_scatter(features: list) -> go.Figure:
    df = pd.DataFrame(features)
    color_map = {'High':'#EF4444','Medium':'#F59E0B','Low':'#22C55E'}
    fig = go.Figure()
    for pri, col in color_map.items():
        sub = df[df['priority'] == pri]
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub['effort'], y=sub['impact'],
            mode='markers+text',
            name=pri,
            marker=dict(size=14, color=col, opacity=0.85, line=dict(color='white',width=2)),
            text=sub['feature'],
            textposition='top center',
            textfont=dict(size=9.5, family='Inter', color='#374151'),
            hovertemplate='<b>%{text}</b><br>Impact: %{y}/10<br>Effort: %{x}/10<extra></extra>',
        ))
    fig.add_shape(type='line', x0=5,x1=5,y0=0,y1=11, line=dict(color='#CBD5E1',dash='dot',width=1.5))
    fig.add_shape(type='line', x0=0,x1=11,y0=5,y1=5, line=dict(color='#CBD5E1',dash='dot',width=1.5))
    fig.add_annotation(x=2.5, y=10.5, text="Quick Wins ✓", font=dict(size=10,color='#16A34A',family='Inter'), showarrow=False)
    fig.add_annotation(x=8.5, y=10.5, text="Big Bets", font=dict(size=10,color='#D97706',family='Inter'), showarrow=False)
    fig.add_annotation(x=2.5, y=0.5, text="Fill-ins", font=dict(size=10,color='#94A3B8',family='Inter'), showarrow=False)
    fig.add_annotation(x=8.5, y=0.5, text="Avoid", font=dict(size=10,color='#EF4444',family='Inter'), showarrow=False)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(248,250,255,0.7)',
        xaxis=dict(title='Effort →', range=[0,11], tickfont=dict(family='Inter',size=11,color='#94A3B8'), gridcolor='rgba(148,163,184,0.12)', showline=True, linecolor='#E2E8F0'),
        yaxis=dict(title='Impact →', range=[0,11], tickfont=dict(family='Inter',size=11,color='#94A3B8'), gridcolor='rgba(148,163,184,0.12)', showline=True, linecolor='#E2E8F0'),
        legend=dict(font=dict(family='Inter',size=12), bgcolor='rgba(255,255,255,0.9)', bordercolor='#E2E8F0', borderwidth=1),
        margin=dict(t=24,b=48,l=56,r=20), height=420,
    )
    return fig


def build_competitive_radar(comp_data: dict) -> go.Figure:
    products = comp_data.get('products', [])
    dims = comp_data.get('dimensions', [])
    scores = comp_data.get('scores', {})
    color_list = [
        ('rgba(99,102,241,0.12)',  '#6366F1'),
        ('rgba(245,158,11,0.12)',  '#F59E0B'),
        ('rgba(34,197,94,0.12)',   '#22C55E'),
    ]
    fig = go.Figure()
    for i, prod in enumerate(products):
        vals = scores.get(prod, [])
        if not vals: continue
        fill_col, line_col = color_list[i % len(color_list)]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=dims + [dims[0]],
            fill='toself',
            fillcolor=fill_col,
            line=dict(color=line_col, width=2),
            name=prod,
            marker=dict(size=5),
        ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,10],
                tickfont=dict(size=10,color='#94A3B8',family='Inter'),
                gridcolor='rgba(148,163,184,0.18)', linecolor='rgba(148,163,184,0.18)'),
            angularaxis=dict(
                tickfont=dict(size=11,color='#374151',family='Inter'),
                gridcolor='rgba(148,163,184,0.18)', linecolor='rgba(148,163,184,0.18)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(font=dict(family='Inter',size=12), bgcolor='rgba(255,255,255,0.9)', bordercolor='#E2E8F0', borderwidth=1),
        margin=dict(t=28,b=28,l=60,r=60), height=420,
    )
    return fig


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sb-logo">Product<span class="accent">Lens</span> AI</div>
        """, unsafe_allow_html=True)

        if st.session_state.analysis_done:
            product = st.session_state.product_input or DEMO_PRODUCT
            mode_tag = "🟡 Demo" if st.session_state.demo_mode else "🟢 Live"
            st.markdown(f"""
            <div style="padding:10px 20px 16px;border-bottom:1px solid #F1F5F9;">
                <div style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;">{mode_tag} Analysis</div>
                <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:700;color:#0F172A;">{product}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="sb-section">Analysis</div>', unsafe_allow_html=True)

            sections = [
                ("snapshot",    "📋", "Product Snapshot"),
                ("metrics",     "📊", "KPI Framework"),
                ("features",    "🧩", "Feature Opportunities"),
                ("competitive", "⚔️", "Competitive Analysis"),
                ("journey",     "🗺️", "User Journey"),
                ("strategy",    "🎯", "Product Strategy"),
                ("prd",         "📄", "PRD Snippet"),
                ("memo",        "✍️", "Executive Memo"),
            ]

            for key, icon, label in sections:
                active = "active" if st.session_state.active_section == key else ""
                if st.button(f"{icon}  {label}", key=f"nav_{key}"):
                    st.session_state.active_section = key
                    st.rerun()

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="sb-section" style="margin-top:8px;">Actions</div>', unsafe_allow_html=True)

            if st.button("↩  New Analysis"):
                for key in ["analysis_done","snapshot","metrics","features","strategy","memo","competitive","user_journey","prd"]:
                    st.session_state[key] = None if key != "analysis_done" else False
                st.session_state.product_input = ""
                st.session_state.demo_mode = False
                st.session_state.active_section = "snapshot"
                st.rerun()

        else:
            st.markdown("""
            <div style="padding:16px 20px;">
                <div style="font-size:12px;color:#64748B;line-height:1.7;">
                    Enter a product name to generate a full PM analysis — or try the
                    <strong>Demo Mode</strong> for an instant Spotify teardown, no API key needed.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="sb-footer">
            Built for AI PM recruiting<br>
            Powered by GPT-4o
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# COMPONENT HELPERS
# ─────────────────────────────────────────────
def sec_header(eye, title, sub=None):
    sub_html = f'<div class="sec-sub">{sub}</div>' if sub else ''
    st.markdown(f"""
    <div class="sec-hdr">
        <div class="sec-eye">{eye}</div>
        <div class="sec-title">{title}</div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def pcard(icon, label, title, body):
    st.markdown(f"""
    <div class="pcard">
        <span class="pcard-icon">{icon}</span>
        <div class="pcard-label">{label}</div>
        <div class="pcard-title">{title}</div>
        <div class="pcard-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def scard(tag_cls, tag_txt, title, body):
    st.markdown(f"""
    <div class="scard">
        <div class="stag {tag_cls}">{tag_txt}</div>
        <div class="pcard-title" style="margin-bottom:5px;">{title}</div>
        <div class="pcard-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def pbar(name, score):
    pct = score * 10
    st.markdown(f"""
    <div class="pbar-block">
        <div class="pbar-row">
            <span class="pbar-name">{name}</span>
            <span class="pbar-score">{score}/10</span>
        </div>
        <div class="prog-track"><div class="prog-fill" style="width:{pct}%"></div></div>
    </div>
    """, unsafe_allow_html=True)


def conf_badge(level):
    cls = 'conf-high' if level == 'High' else 'conf-medium'
    dot = '●'
    return f'<span class="conf-badge {cls}">{dot} {level} confidence</span>'


# ─────────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────────
def screen_landing():
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">✦ AI Product Intelligence Platform</div>
        <h1 class="hero-h1">Turn products into<br><span class="grad">decisions.</span></h1>
        <p class="hero-sub">PM-quality product analysis in seconds. Built to show how a product thinker thinks.</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="demo-notice">
            💡 <strong>No API key?</strong> Click "Load Demo" below for a full Spotify teardown — no setup needed.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<span style="font-size:12px;font-weight:600;color:#64748B;letter-spacing:0.3px;">OpenAI API Key</span>', unsafe_allow_html=True)
        api_val = st.text_input("api", value=st.session_state.api_key, placeholder="sk-... (optional if using demo)", type="password", label_visibility="collapsed")
        if api_val: st.session_state.api_key = api_val

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:12px;font-weight:600;color:#64748B;letter-spacing:0.3px;">Product or App Name</span>', unsafe_allow_html=True)
        prod_val = st.text_input("product", value=st.session_state.product_input, placeholder="e.g. Spotify, Duolingo, Uber Eats, AI meal planner...", label_visibility="collapsed")
        if prod_val: st.session_state.product_input = prod_val

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

        b1, b2 = st.columns([2, 1])
        with b1:
            if st.button("✨ Generate Product Insights"):
                if not st.session_state.api_key:
                    st.error("Enter your OpenAI API key, or use Demo Mode →")
                elif not st.session_state.product_input.strip():
                    st.error("Enter a product name first.")
                else:
                    run_analysis(demo=False)
        with b2:
            if st.button("⚡ Load Demo"):
                run_analysis(demo=True)

        st.markdown("""
        <div style="margin-top:20px;text-align:center;">
            <p style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px;">Example products</p>
            <div class="chip-row">
                <span class="chip">📸 Instagram</span>
                <span class="chip">🍔 Uber Eats</span>
                <span class="chip">🎵 Spotify</span>
                <span class="chip">🦆 Duolingo</span>
                <span class="chip">📝 Notion</span>
                <span class="chip">🥗 AI Meal Planner</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def run_analysis(demo: bool):
    if demo:
        st.session_state.demo_mode = True
        st.session_state.product_input = DEMO_PRODUCT
        st.session_state.snapshot = DEMO_DATA["snapshot"]
        st.session_state.metrics = DEMO_DATA["metrics"]
        st.session_state.features = DEMO_DATA["features"]
        st.session_state.strategy = DEMO_DATA["strategy"]
        st.session_state.memo = DEMO_DATA["memo"]
        st.session_state.competitive = DEMO_DATA["competitive"]
        st.session_state.user_journey = DEMO_DATA["user_journey"]
        st.session_state.prd = DEMO_DATA["prd"]
        st.session_state.analysis_done = True
        st.session_state.active_section = "snapshot"
        st.rerun()
        return

    product = st.session_state.product_input.strip()
    with st.spinner("Analyzing product..."):
        bar = st.progress(0)
        try:
            bar.progress(8,  "Building product snapshot...")
            st.session_state.snapshot = generate_snapshot(product)
            bar.progress(22, "Generating KPI framework...")
            st.session_state.metrics = generate_metrics(product)
            bar.progress(38, "Mapping feature opportunities...")
            st.session_state.features = generate_features(product)
            bar.progress(52, "Running competitive analysis...")
            st.session_state.competitive = generate_competitive(product)
            bar.progress(64, "Mapping user journey...")
            st.session_state.user_journey = generate_user_journey(product)
            bar.progress(76, "Formulating strategy...")
            st.session_state.strategy = generate_strategy(product)
            bar.progress(88, "Writing PRD and executive memo...")
            st.session_state.prd = generate_prd(product, st.session_state.snapshot, st.session_state.features)
            st.session_state.memo = generate_memo(product, st.session_state.snapshot, st.session_state.strategy)
            bar.progress(100, "Done!")
            st.session_state.demo_mode = False
            st.session_state.analysis_done = True
            st.session_state.active_section = "snapshot"
        except Exception as e:
            st.error(f"Error: {e}")
            return
    st.rerun()


def screen_snapshot():
    snap = st.session_state.snapshot
    product = st.session_state.product_input
    confidence = snap.get("confidence", "High")

    sec_header("01 — Product Snapshot", f"{product} Teardown",
               "Summary · Users · Problem · Value Prop · North Star")

    col1, col2 = st.columns(2)
    with col1:
        pcard("📋", "Product Summary", "Overview", snap.get("summary",""))
        pcard("👤", "Target Users", "Primary Persona", snap.get("target_users",""))
        pcard("🔥", "Core User Problem", "Pain Point", snap.get("user_problem",""))
    with col2:
        pcard("💡", "Value Proposition", "Why Users Choose It", snap.get("value_proposition",""))

        nsm = snap.get("north_star_metric","")
        nsw = snap.get("north_star_why","")
        st.markdown(f"""
        <div class="pcard">
            <span class="pcard-icon">⭐</span>
            <div class="pcard-label">North Star Metric</div>
            <div class="pcard-title" style="font-size:18px;">{nsm}</div>
            <div class="pcard-body">{nsw}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="mcard" style="text-align:left;">
                <div class="mcard-name">Category</div>
                <div style="font-family:'Sora',sans-serif;font-size:15px;font-weight:700;color:#0F172A;margin-top:5px;">{snap.get("category","—")}</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            stage = snap.get("stage","—")
            stage_c = {"Growth":"#16A34A","Maturity":"#3B82F6","Decline":"#EF4444","Launch":"#8B5CF6"}.get(stage,"#64748B")
            st.markdown(f"""
            <div class="mcard" style="text-align:left;">
                <div class="mcard-name">Stage</div>
                <div style="font-family:'Sora',sans-serif;font-size:15px;font-weight:700;color:{stage_c};margin-top:5px;">{stage}</div>
            </div>""", unsafe_allow_html=True)

    # PM Teardown Insight
    insight = snap.get("teardown_insight","")
    if insight:
        st.markdown(f"""
        <div class="insight-box" style="margin-top:8px;">
            <div class="insight-label">🔍 PM Teardown Insight {conf_badge(confidence)}</div>
            <div class="insight-body">{insight}</div>
        </div>
        """, unsafe_allow_html=True)


def screen_metrics():
    metrics = st.session_state.metrics
    product = st.session_state.product_input

    sec_header("02 — KPI Framework", f"Product Metrics for {product}",
               "Acquisition · Engagement · Retention · Business")

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        radar_data = metrics.get("radar", {})
        if radar_data:
            st.plotly_chart(build_radar(radar_data), use_container_width=True)
    with c2:
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;">Dimension Scores</div>', unsafe_allow_html=True)
        for dim, score in metrics.get("radar",{}).items():
            pbar(dim, score)

    cats = [
        ("acquisition", "🚀", "Acquisition"),
        ("engagement",  "💬", "Engagement"),
        ("retention",   "🔄", "Retention"),
        ("business",    "💰", "Business"),
    ]
    for cat_key, icon, label in cats:
        data = metrics.get(cat_key, [])
        if not data: continue
        st.markdown(f'<div style="display:flex;align-items:center;gap:7px;margin:22px 0 10px;"><span style="font-size:17px;">{icon}</span><span style="font-family:Sora,sans-serif;font-size:14px;font-weight:700;color:#1E293B;">{label} Metrics</span></div>', unsafe_allow_html=True)
        cols = st.columns(len(data))
        for col, m in zip(cols, data):
            with col:
                st.markdown(f"""
                <div class="mcard">
                    <div class="mcard-val">{m.get("value","—")}</div>
                    <div class="mcard-name">{m.get("name","")}</div>
                    <div class="mcard-bench">vs {m.get("benchmark","—")}</div>
                    <div class="prog-track" style="margin-top:10px;"><div class="prog-fill" style="width:{m.get('score',5)*10}%"></div></div>
                    <div style="text-align:right;font-size:10.5px;color:#94A3B8;margin-top:3px;">{m.get('score',5)}/10</div>
                </div>""", unsafe_allow_html=True)


def screen_features():
    features_data = st.session_state.features.get("features", [])
    product = st.session_state.product_input

    sec_header("03 — Feature Opportunities", f"Prioritized Roadmap for {product}",
               "Impact × Effort matrix with PM-native prioritization scoring")

    if features_data:
        st.plotly_chart(build_scatter(features_data), use_container_width=True)

    df = pd.DataFrame(features_data)
    if not df.empty:
        df_d = df[["feature","reason","impact","effort","priority_score","priority"]].copy()
        df_d.columns = ["Feature","Reason","Impact","Effort","Score","Priority"]
        df_d = df_d.sort_values("Score", ascending=False).reset_index(drop=True)
        st.dataframe(df_d, use_container_width=True, hide_index=True,
            column_config={
                "Feature":   st.column_config.TextColumn("Feature", width="medium"),
                "Reason":    st.column_config.TextColumn("Reason", width="large"),
                "Impact":    st.column_config.ProgressColumn("Impact",  min_value=0, max_value=10, format="%d"),
                "Effort":    st.column_config.ProgressColumn("Effort",  min_value=0, max_value=10, format="%d"),
                "Score":     st.column_config.NumberColumn("Score", format="%.1f"),
                "Priority":  st.column_config.TextColumn("Priority"),
            })


def screen_competitive():
    comp = st.session_state.competitive
    product = st.session_state.product_input

    sec_header("04 — Competitive Analysis", f"Market Positioning for {product}",
               "Side-by-side comparison across dimensions that actually matter")

    if not comp:
        st.info("Competitive data unavailable.")
        return

    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        st.plotly_chart(build_competitive_radar(comp), use_container_width=True)

    with c2:
        products = comp.get("products", [])
        dims     = comp.get("dimensions", [])
        scores   = comp.get("scores", {})

        st.markdown('<div style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;margin-top:16px;">Score Breakdown</div>', unsafe_allow_html=True)

        if dims and products and scores:
            table_data = {"Dimension": dims}
            for p in products:
                table_data[p] = scores.get(p, [0]*len(dims))
            df_comp = pd.DataFrame(table_data)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    insights = comp.get("insights", [])
    if insights:
        st.markdown('<div style="font-size:11px;font-weight:700;color:#94A3B8;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;">Strategic Insights</div>', unsafe_allow_html=True)
        for i, ins in enumerate(insights):
            icon = ["🥇","⚔️","🎯","💡"][i % 4]
            st.markdown(f"""
            <div class="scard" style="padding:16px 20px;">
                <div style="font-size:13.5px;color:#334155;line-height:1.6;">{icon} {ins}</div>
            </div>
            """, unsafe_allow_html=True)


def screen_journey():
    jd = st.session_state.user_journey
    product = st.session_state.product_input

    sec_header("05 — User Journey Map", f"End-to-End Experience for {product}",
               "What users do · Where they struggle · What PMs should fix")

    if not jd:
        st.info("User journey data unavailable.")
        return

    stages      = jd.get("stages", [])
    actions     = jd.get("actions", [])
    pain_points = jd.get("pain_points", [])
    opps        = jd.get("opportunities", [])

    for i, stage in enumerate(stages):
        action = actions[i] if i < len(actions) else ""
        pain   = pain_points[i] if i < len(pain_points) else ""
        opp    = opps[i] if i < len(opps) else ""
        st.markdown(f"""
        <div class="journey-stage">
            <div class="journey-label">Stage {i+1} of {len(stages)}</div>
            <div class="journey-stage-name">{stage}</div>
            <div class="journey-action">👤 <strong>User Action:</strong> {action}</div>
            <div><span class="pain-tag">⚠️ Pain: {pain}</span></div>
            <div style="margin-top:8px;"><span class="opp-tag">✓ PM Opportunity: {opp}</span></div>
        </div>
        """, unsafe_allow_html=True)


def screen_strategy():
    strategy = st.session_state.strategy
    product = st.session_state.product_input

    sec_header("06 — Product Strategy", f"Executive Playbook for {product}",
               "Recommendations · Risks · Experiments · Metrics")

    tabs = st.tabs(["🎯 Recommendations", "⚠️ Risks", "🔬 Validate First", "📊 Success Metrics", "🧪 Experiments"])

    with tabs[0]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("recommendations", []):
            scard("t-rec", "Recommendation", item.get("title",""), item.get("detail",""))

    with tabs[1]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("risks", []):
            scard("t-risk", "Risk", item.get("title",""), item.get("detail",""))

    with tabs[2]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("validate_first", []):
            scard("t-valid", "Validate", item.get("title",""), item.get("detail",""))

    with tabs[3]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("success_metrics", []):
            st.markdown(f"""
            <div class="scard">
                <div class="stag t-metric">Success Metric</div>
                <div class="pcard-title" style="margin-bottom:5px;">{item.get("metric","")}</div>
                <div class="pcard-body"><strong>Target:</strong> {item.get("target","")} &nbsp;·&nbsp; <strong>Timeframe:</strong> {item.get("timeframe","")}</div>
            </div>""", unsafe_allow_html=True)

    with tabs[4]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("experiments", []):
            scard("t-exp", "Experiment", item.get("title",""), item.get("hypothesis",""))


def screen_prd():
    prd = st.session_state.prd
    product = st.session_state.product_input

    sec_header("07 — PRD Snippet", "Product Requirements Document",
               "The PM artifact that turns strategy into a buildable spec")

    if not prd:
        st.info("PRD data unavailable.")
        return

    prd_status_colors = {"Proposed":"#F59E0B","In Discovery":"#3B82F6","Spec Review":"#8B5CF6"}
    status = prd.get("status","Proposed")
    status_color = prd_status_colors.get(status, "#64748B")
    today = datetime.date.today().strftime("%B %d, %Y")

    goals_html     = "".join([f'<li style="margin-bottom:5px;">{g}</li>' for g in prd.get("goals",[])])
    non_goals_html = "".join([f'<li style="margin-bottom:5px;color:#94A3B8;">{g}</li>' for g in prd.get("non_goals",[])])

    reqs_html = ""
    for r in prd.get("requirements", []):
        p = r.get("priority","P2")
        cls = "prd-p0" if p=="P0" else ("prd-p1" if p=="P1" else "prd-p2")
        reqs_html += f'<div class="prd-req"><span class="{cls}">{p}</span><span class="prd-req-text">{r.get("requirement","")}</span></div>'

    metrics_html = "".join([f'<li style="margin-bottom:5px;">{m}</li>' for m in prd.get("success_metrics",[])])
    oqs_html = "".join([f'<div class="prd-oq">❓ {q}</div>' for q in prd.get("open_questions",[])])
    memo_data = st.session_state.memo or {}

    st.markdown(f"""
    <div class="prd-wrap">
        <div class="prd-header">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div class="prd-stamp">Product Requirements Document</div>
                    <div class="prd-title">{prd.get("feature","")}</div>
                    <div class="prd-meta">{product} · Owner: {prd.get("owner","")} · {today}</div>
                </div>
                <div style="background:{status_color}18;color:{status_color};font-size:11.5px;font-weight:700;padding:5px 12px;border-radius:6px;letter-spacing:0.5px;flex-shrink:0;">{status}</div>
            </div>
        </div>

        <div class="prd-sec-label">Problem Statement</div>
        <div class="prd-body">{prd.get("problem","")}</div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:4px;">
            <div>
                <div class="prd-sec-label">Goals</div>
                <ul style="list-style:none;padding:0;">{goals_html}</ul>
            </div>
            <div>
                <div class="prd-sec-label">Non-Goals</div>
                <ul style="list-style:none;padding:0;">{non_goals_html}</ul>
            </div>
        </div>

        <div class="prd-sec-label">Requirements</div>
        {reqs_html}

        <div class="prd-sec-label">Success Metrics</div>
        <ul style="list-style:none;padding:0;">{metrics_html}</ul>

        <div class="prd-sec-label">Open Questions</div>
        {oqs_html}

        <div class="prd-decision">
            <div class="prd-dec-label">✦ Decision Framework</div>
            <div class="prd-dec-body">{memo_data.get("decision","Awaiting executive alignment.")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    prd_text = f"""PRODUCT REQUIREMENTS DOCUMENT
{prd.get("feature","")} — {product}
Status: {status} | Owner: {prd.get("owner","")} | Date: {today}
{'='*60}

PROBLEM
{prd.get("problem","")}

GOALS
{chr(10).join(['• ' + g for g in prd.get("goals",[])])}

NON-GOALS
{chr(10).join(['• ' + g for g in prd.get("non_goals",[])])}

REQUIREMENTS
{chr(10).join([f"[{r.get('priority','')}] {r.get('requirement','')}" for r in prd.get("requirements",[])])}

SUCCESS METRICS
{chr(10).join(['• ' + m for m in prd.get("success_metrics",[])])}

OPEN QUESTIONS
{chr(10).join(['? ' + q for q in prd.get("open_questions",[])])}
"""
    _, dc, _ = st.columns([1,1,1])
    with dc:
        st.download_button("⬇ Download PRD", prd_text,
            file_name=f"prd_{product.lower().replace(' ','_')}.txt", mime="text/plain")


def screen_memo():
    memo = st.session_state.memo
    product = st.session_state.product_input
    today = datetime.date.today().strftime("%B %d, %Y")

    sec_header("08 — Executive Memo", "CPO-Level Product Brief",
               "The one-pager a PM would bring to a product review")

    st.markdown(f"""
    <div class="memo-wrap">
        <div class="memo-hdr">
            <div>
                <div class="memo-stamp">Product Memo · Confidential</div>
                <div class="memo-product">{product}</div>
            </div>
            <div class="memo-meta">
                ProductLens AI<br>
                {today}<br>
                <span style="color:#3B82F6;font-weight:600;">GPT-4o</span>
            </div>
        </div>
        <div class="memo-sec">
            <div class="memo-sec-label">01 · Problem</div>
            <div class="memo-sec-body">{memo.get("problem","")}</div>
        </div>
        <div class="memo-sec">
            <div class="memo-sec-label">02 · User</div>
            <div class="memo-sec-body">{memo.get("user","")}</div>
        </div>
        <div class="memo-sec">
            <div class="memo-sec-label">03 · Solution</div>
            <div class="memo-sec-body">{memo.get("solution","")}</div>
        </div>
        <div class="memo-sec">
            <div class="memo-sec-label">04 · Metrics</div>
            <div class="memo-sec-body">{memo.get("metrics","")}</div>
        </div>
        <div class="memo-decision">
            <div class="memo-dec-label">✦ Decision</div>
            <div class="memo-dec-body">{memo.get("decision","")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    memo_text = f"""PRODUCT MEMO — {product.upper()}
ProductLens AI | {today}
{'='*60}

PROBLEM
{memo.get('problem','')}

USER
{memo.get('user','')}

SOLUTION
{memo.get('solution','')}

METRICS
{memo.get('metrics','')}

DECISION
{memo.get('decision','')}
"""
    _, dc, _ = st.columns([1,1,1])
    with dc:
        st.download_button("⬇ Download Memo", memo_text,
            file_name=f"memo_{product.lower().replace(' ','_')}.txt", mime="text/plain")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    render_sidebar()

    st.markdown("""
    <div class="top-nav">
        <div class="nav-logo">Product<span class="accent">Lens</span> AI</div>
        <div class="nav-right">
            <span class="nav-pill pill-ai">GPT-4o</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.analysis_done:
        screen_landing()
        return

    product = st.session_state.product_input
    mode_label = "🟡 Demo Mode — Spotify" if st.session_state.demo_mode else f"🟢 Live Analysis — {product}"

    st.markdown(f"""
    <div class="done-banner">
        <div class="done-icon">✅</div>
        <div class="done-text">
            <strong>{mode_label}</strong>
            <span>8 sections generated · Use the sidebar to navigate · Download outputs below</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    section = st.session_state.active_section
    dispatch = {
        "snapshot":    screen_snapshot,
        "metrics":     screen_metrics,
        "features":    screen_features,
        "competitive": screen_competitive,
        "journey":     screen_journey,
        "strategy":    screen_strategy,
        "prd":         screen_prd,
        "memo":        screen_memo,
    }
    screen_fn = dispatch.get(section, screen_snapshot)
    screen_fn()

    st.markdown("""
    <div style="text-align:center;padding:48px 0 20px;border-top:1px solid #E2E8F0;margin-top:52px;">
        <div style="font-family:'Sora',sans-serif;font-size:15px;font-weight:700;color:#0F172A;margin-bottom:4px;">
            Product<span style="background:linear-gradient(135deg,#3B82F6,#6366F1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Lens</span> AI
        </div>
        <div style="font-size:11.5px;color:#94A3B8;">Turn products into decisions. · Built with GPT-4o + Streamlit</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
