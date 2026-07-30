import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import datetime
import requests
from openai import OpenAI

st.set_page_config(
    page_title="ProductLens AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# APP STORE API
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_app_store_data(product_name: str) -> dict:
    """Fetch logo + screenshots from iTunes Search API"""
    try:
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(product_name)}&entity=software&limit=1"
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("resultCount", 0) > 0:
            app = data["results"][0]
            return {
                "found": True,
                "name": app.get("trackName", product_name),
                "icon": app.get("artworkUrl512") or app.get("artworkUrl100", ""),
                "screenshots": app.get("screenshotUrls", [])[:3],
                "rating": round(app.get("averageUserRating", 0), 1),
                "rating_count": app.get("userRatingCount", 0),
                "genre": app.get("primaryGenreName", ""),
                "developer": app.get("artistName", ""),
                "description": app.get("description", "")[:200] + "..." if app.get("description") else "",
                "price": "Free" if app.get("price", 0) == 0 else f"${app.get('price')}",
            }
    except Exception:
        pass
    return {"found": False}

@st.cache_data(ttl=3600)
def fetch_logo(product_name: str) -> str:
    """Clearbit logo fallback"""
    domain_map = {
        "spotify": "spotify.com", "uber eats": "ubereats.com", "uber": "uber.com",
        "instagram": "instagram.com", "duolingo": "duolingo.com", "notion": "notion.so",
        "airbnb": "airbnb.com", "netflix": "netflix.com", "tiktok": "tiktok.com",
        "snapchat": "snapchat.com", "twitter": "twitter.com", "x": "x.com",
        "linkedin": "linkedin.com", "youtube": "youtube.com", "google": "google.com",
        "apple": "apple.com", "amazon": "amazon.com", "meta": "meta.com",
        "facebook": "facebook.com", "whatsapp": "whatsapp.com", "discord": "discord.com",
        "slack": "slack.com", "zoom": "zoom.us", "dropbox": "dropbox.com",
        "figma": "figma.com", "canva": "canva.com", "shopify": "shopify.com",
        "stripe": "stripe.com", "robinhood": "robinhood.com", "coinbase": "coinbase.com",
        "doordash": "doordash.com", "grubhub": "grubhub.com", "lyft": "lyft.com",
        "peloton": "peloton.com", "headspace": "headspace.com", "calm": "calm.com",
        "strava": "strava.com", "myfitnesspal": "myfitnesspal.com",
    }
    key = product_name.lower().strip()
    domain = domain_map.get(key, f"{key.replace(' ', '')}.com")
    return f"https://logo.clearbit.com/{domain}"

# ─────────────────────────────────────────────
# DEMO DATA
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
        "radar": {"Acquisition": 9, "Engagement": 8, "Retention": 7, "Monetization": 5, "Virality": 7, "NPS": 8}
    },
    "features": {
        "features": [
            {"feature": "Social Listening Rooms", "reason": "Gen Z users want shared listening experiences; Discord shows demand for audio-social crossover", "impact": 8, "effort": 5, "priority_score": 6.4, "priority": "High"},
            {"feature": "AI Mood-Based Radio", "reason": "Users don't know what to hear — AI reading context removes decision fatigue", "impact": 9, "effort": 4, "priority_score": 8.1, "priority": "High"},
            {"feature": "Offline Podcast Highlights", "reason": "Podcast listeners want to save key moments; current workarounds are clunky", "impact": 7, "effort": 3, "priority_score": 7.0, "priority": "High"},
            {"feature": "Lyrics Karaoke Mode", "reason": "Interactive karaoke drives daily use and differentiates vs Apple Music", "impact": 7, "effort": 5, "priority_score": 5.6, "priority": "Medium"},
            {"feature": "Artist Direct Merch", "reason": "Closes loop between fan discovery and purchase; adds high-margin revenue", "impact": 8, "effort": 7, "priority_score": 5.6, "priority": "Medium"},
            {"feature": "Cross-App Playlist Import", "reason": "Removes #1 barrier to switching from Apple Music/YouTube", "impact": 9, "effort": 6, "priority_score": 7.2, "priority": "High"},
            {"feature": "Sleep Timer + Wind-Down", "reason": "2M+ community upvotes; low effort, high satisfaction win", "impact": 6, "effort": 2, "priority_score": 7.2, "priority": "High"},
            {"feature": "Fan Club Subscriptions", "reason": "Positions Spotify as end-to-end artist economy platform", "impact": 9, "effort": 8, "priority_score": 6.3, "priority": "High"},
        ]
    },
    "strategy": {
        "recommendations": [
            {"title": "Double down on the social layer", "detail": "Spotify's taste graph is its moat but it's private. Making listening social — shared queues, listening parties, taste compatibility — creates network effects Apple Music cannot replicate with catalog alone."},
            {"title": "Fix the monetization ceiling before growing users", "detail": "At $4.97 ARPU vs Apple Music's $10.99, Spotify leaves ~$6/user/month on the table. A Superfan tier at $15.99 with lossless audio and exclusives targets the 26% already paying."},
            {"title": "Own the creator flywheel end-to-end", "detail": "Spotify for Podcasters gave Spotify distribution data. The next move is monetization tools — fan subscriptions, merch, live shows — turning Spotify into a creator economy platform."},
        ],
        "risks": [
            {"title": "Label dependency is existential", "detail": "~70% of revenue goes to rights holders. Mitigation: accelerate owned podcast and audiobook content to reduce licensed music's share of listening hours."},
            {"title": "AI music generation disrupts the catalog", "detail": "If AI-generated music becomes royalty-free and indistinguishable, the premium on licensed catalog collapses. Spotify should be testing AI music as a feature, not waiting for it."},
            {"title": "Platform concentration risk with Apple", "detail": "Apple can preference Apple Music on iOS. The hedge is deepening Android and smart speaker share while the EU antitrust case plays out."},
        ],
        "validate_first": [
            {"title": "Will Premium users pay for a Superfan tier?", "detail": "Run a waitlist for $15.99/month HiFi + exclusives. Target: 5% of Premium base signals interest within 60 days."},
            {"title": "Does social listening increase retention?", "detail": "A/B test Shared Queue for 100K users. Hypothesis: users with ≥1 social session have 15% higher D30 retention."},
            {"title": "Does cross-app import reduce onboarding churn?", "detail": "Measure 7-day activation for users who import a playlist vs those who don't. Hypothesis: 2x D7 retention."},
        ],
        "success_metrics": [
            {"metric": "Premium Subscriber ARPU", "target": "$6.50/month (+$1.53)", "timeframe": "12 months"},
            {"metric": "Free→Premium Conversion", "target": "30% (+4pp)", "timeframe": "6 months"},
            {"metric": "Social Feature DAU Adoption", "target": "15% of DAU", "timeframe": "9 months"},
        ],
        "experiments": [
            {"title": "Social Queue A/B Test", "hypothesis": "If we enable shared listening queues, then D30 retention will increase 12% because music becomes a coordination mechanism, not just solo activity."},
            {"title": "Superfan Tier Waitlist", "hypothesis": "If we offer a $15.99 HiFi + exclusives tier, then ≥5% of Premium users join the waitlist in 30 days because superfans are underserved."},
            {"title": "Onboarding Playlist Import", "hypothesis": "If we surface Apple Music import at step 2 of onboarding, D7 retention increases 18% because users with existing libraries activate faster."},
        ]
    },
    "memo": {
        "problem": "Spotify has 602M users but captures only $4.97/month ARPU — less than half of Apple Music's $10.99. The platform has solved user scale; the monetization density problem remains.",
        "user": "The underserved user is the Superfan: someone who streams 3+ hours daily, follows 50+ artists, and attends live shows. They're willing to pay more — they just haven't been given a reason.",
        "solution": "Launch a Spotify Superfan tier at $15.99/month offering lossless HiFi audio, early concert access, exclusive artist content, and social listening rooms. Targets the top 10–15% of Premium subscribers.",
        "metrics": "Primary: ARPU lift to $6.50 in 12 months. Secondary: Superfan adoption ≥8% of Premium base in 6 months. Guardrail: no increase in overall Premium churn rate.",
        "decision": "Prioritize Superfan tier in H1. Run waitlist experiment in Q1 — if ≥5% of Premium users join, greenlight full development. This is a revenue density play, not user growth."
    },
    "competitive": {
        "products": ["Spotify", "Apple Music", "YouTube Music"],
        "dimensions": ["Catalog Size", "Personalization", "Social Features", "Podcast Library", "Price Value", "Offline Experience", "Artist Tools", "UX Quality"],
        "scores": {
            "Spotify":       [8, 9, 6, 9, 8, 8, 7, 8],
            "Apple Music":   [9, 7, 3, 5, 7, 9, 4, 9],
            "YouTube Music": [9, 7, 4, 4, 9, 6, 5, 7],
        },
        "insights": [
            "Spotify leads on personalization and podcast library — its clearest moats.",
            "Apple Music wins on catalog completeness and offline reliability via device integration.",
            "YouTube Music's unlimited catalog and free tier makes it the price-sensitive user's choice.",
            "Social features are the biggest whitespace across all three — a greenfield PM opportunity.",
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
            "Ad fatigue — first ad can come within 10 min of first session",
            "Onboarding asks for genre preferences but ignores mood context",
            "Shuffle-only on free tier frustrates users who want control",
            "No social proof for new music — missing friend activity signal",
            "Price anchoring — $9.99 feels steep without a trial comparison",
            "Library management is clunky; hard to find saved songs"
        ],
        "opportunities": [
            "Delay first ad 30 min to build habit before monetizing",
            "Mood-first onboarding ('How are you feeling?') for better Day 1 recs",
            "Give free users 3 'song unlocks' per day to drive Premium aspiration",
            "Friend activity feed showing what your network is obsessed with",
            "Free trial default with payment after value is demonstrated",
            "Redesigned library with smart folders and pinned playlists"
        ]
    },
    "prd": {
        "feature": "Spotify Superfan Tier",
        "status": "Proposed",
        "owner": "Growth & Monetization PM",
        "problem": "Spotify's single Premium tier undermonetizes its most engaged users. Superfans (top 15% by listening hours) pay the same $9.99 as casual subscribers.",
        "goals": [
            "Increase ARPU from $4.97 to $6.50 within 12 months",
            "Achieve 8% adoption among existing Premium users in 6 months",
            "Maintain Premium churn at current 4.8% or below"
        ],
        "non_goals": [
            "This is not a free-tier conversion play — target is existing Premium only",
            "This is not a full rebrand of Premium — base tier remains unchanged",
            "Artist payouts restructuring is not in scope for v1"
        ],
        "requirements": [
            {"priority": "P0", "requirement": "HiFi lossless audio (FLAC / 24-bit) on all devices"},
            {"priority": "P0", "requirement": "Superfan badge visible on profile and in social features"},
            {"priority": "P1", "requirement": "Early access window (48hrs) for concert ticket purchases"},
            {"priority": "P1", "requirement": "Shared listening rooms (co-listen with up to 5 friends)"},
            {"priority": "P2", "requirement": "Exclusive artist content drops (acoustic sessions, demos)"},
            {"priority": "P2", "requirement": "Extended download cache (10K songs vs 5K on standard Premium)"},
        ],
        "success_metrics": [
            "Superfan tier adoption rate among Premium base (target: 8% in 6mo)",
            "ARPU delta vs control group (target: +$6.02/month)",
            "D90 retention for Superfan vs standard Premium (target: +8pp)",
            "NPS delta for Superfan tier (target: ≥60 NPS)"
        ],
        "open_questions": [
            "Should we offer annual billing discount ($149.99/yr) from launch?",
            "How do we handle family plan users — per-seat upgrade or household?",
            "Do we announce HiFi publicly before launch to manage label negotiations?"
        ]
    }
}

# ─────────────────────────────────────────────
# CSS — Apple-inspired: pure white, black type,
# iridescent hero gradient, borderless cards
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #fafafa !important;
    background-image:
        radial-gradient(ellipse at 15% 15%, rgba(199,172,255,0.45) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 10%, rgba(150,210,255,0.38) 0%, transparent 45%),
        radial-gradient(ellipse at 80% 85%, rgba(255,180,165,0.42) 0%, transparent 50%),
        radial-gradient(ellipse at 10% 80%, rgba(160,240,200,0.35) 0%, transparent 45%),
        radial-gradient(ellipse at 50% 50%, rgba(255,220,180,0.2) 0%, transparent 60%) !important;
    background-attachment: fixed !important;
    font-family: -apple-system, 'SF Pro Display', 'Inter', sans-serif;
    color: #1D1D1F;
    -webkit-font-smoothing: antialiased;
}
[data-testid="stAppViewContainer"] > .main { background: transparent !important; }
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(250,250,252,0.95) !important;
    border-right: 1px solid rgba(0,0,0,0.08) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.12); border-radius: 2px; }

/* ── Nav ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 40px;
    background: rgba(255,255,255,0.85);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid rgba(0,0,0,0.08);
    margin: -6rem -4rem 3rem -4rem;
    position: sticky;
    top: 0;
    z-index: 99;
}
.nav-logo {
    font-size: 17px;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.5px;
}
.nav-logo .iridescent {
    background: linear-gradient(90deg, #FF6B6B, #FFD93D, #6BCB77, #4D96FF, #C77DFF);
    background-size: 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.nav-tag {
    font-size: 11px;
    font-weight: 600;
    color: #6E6E73;
    letter-spacing: 0.3px;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 52px 24px 36px;
    background: transparent;
}
.hero-eyebrow {
    font-size: 11px;
    font-weight: 600;
    color: #6E6E73;
    letter-spacing: 1px;
    margin-bottom: 18px;
    text-transform: uppercase;
    display: block;
}
.hero-h1 {
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 800;
    letter-spacing: -2.5px;
    line-height: 1.06;
    color: #1D1D1F;
    margin-bottom: 16px;
    text-transform: none !important;
}
.hero-h1 .iridescent {
    background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 25%, #6BCB77 50%, #4D96FF 75%, #C77DFF 100%);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 17px;
    font-weight: 400;
    color: #424245;
    max-width: 600px;
    margin: 0 auto 20px;
    line-height: 1.5;
    letter-spacing: -0.1px;
    text-align: center !important;
    text-transform: none !important;
    display: block;
    width: 100%;
}
.demo-notice {
    background: #F5F5F7;
    border-radius: 12px;
    padding: 12px 18px;
    font-size: 13px;
    color: #6E6E73;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 22px;
}
.chip {
    font-size: 13px;
    font-weight: 500;
    color: #1D1D1F;
    background: #F5F5F7;
    border: none;
    padding: 7px 16px;
    border-radius: 20px;
}

/* ── Product hero banner ── */
.product-hero {
    background: #F5F5F7;
    border-radius: 20px;
    padding: 40px 40px 32px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    gap: 32px;
}
.product-logo {
    width: 100px;
    height: 100px;
    border-radius: 22px;
    object-fit: cover;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    flex-shrink: 0;
}
.product-logo-placeholder {
    width: 100px;
    height: 100px;
    border-radius: 22px;
    background: linear-gradient(135deg, #1D1D1F, #424245);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    flex-shrink: 0;
}
.product-hero-info {}
.product-hero-name {
    font-size: 36px;
    font-weight: 800;
    color: #1D1D1F;
    letter-spacing: -1.5px;
    margin-bottom: 4px;
}
.product-hero-dev {
    font-size: 14px;
    color: #6E6E73;
    margin-bottom: 12px;
}
.product-hero-tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
.hero-tag {
    font-size: 12px;
    font-weight: 500;
    color: #1D1D1F;
    background: white;
    border: 1px solid rgba(0,0,0,0.1);
    padding: 4px 12px;
    border-radius: 20px;
}
.screenshots-row {
    display: flex;
    gap: 12px;
    margin-bottom: 32px;
    overflow-x: auto;
    padding-bottom: 4px;
}
.screenshot-img {
    height: 200px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    flex-shrink: 0;
    object-fit: cover;
}

/* ── Section header ── */
.sec-hdr {
    margin-bottom: 32px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(0,0,0,0.08);
}
.sec-eye {
    font-size: 11px;
    font-weight: 600;
    color: #6E6E73;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.sec-title {
    font-size: 28px;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.8px;
}
.sec-sub {
    font-size: 14px;
    color: #6E6E73;
    margin-top: 5px;
}

/* ── Cards — borderless Apple style ── */
.pcard {
    background: #F5F5F7;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 12px;
    transition: background 0.15s;
}
.pcard:hover { background: #EBEBED; }
.pcard-icon  { font-size: 24px; margin-bottom: 10px; display: block; }
.pcard-label { font-size: 11px; font-weight: 600; color: #6E6E73; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px; }
.pcard-title { font-size: 17px; font-weight: 700; color: #1D1D1F; margin-bottom: 8px; letter-spacing: -0.3px; }
.pcard-body  { font-size: 14px; color: #424245; line-height: 1.65; }

/* ── Insight callout ── */
.insight-box {
    background: #F5F5F7;
    border-radius: 16px;
    padding: 20px 24px;
    margin-top: 8px;
    border-left: 3px solid #1D1D1F;
}
.insight-label { font-size: 11px; font-weight: 700; color: #1D1D1F; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 6px; }
.insight-body  { font-size: 14px; color: #424245; line-height: 1.65; font-style: italic; }

/* ── Metric card ── */
.mcard {
    background: #F5F5F7;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.mcard-val   { font-size: 24px; font-weight: 800; color: #1D1D1F; letter-spacing: -1px; line-height: 1; margin-bottom: 4px; }
.mcard-name  { font-size: 11px; font-weight: 600; color: #6E6E73; text-transform: uppercase; letter-spacing: 0.6px; }
.mcard-bench { font-size: 12px; color: #6E6E73; margin-top: 6px; }
.prog-track  { background: rgba(0,0,0,0.08); border-radius: 4px; height: 5px; overflow: hidden; margin-top: 12px; }
.prog-fill   { height: 100%; border-radius: 4px; background: #1D1D1F; }

/* ── Progress bar ── */
.pbar-block  { background: #F5F5F7; border-radius: 12px; padding: 16px 20px; margin-bottom: 8px; }
.pbar-row    { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.pbar-name   { font-size: 13px; font-weight: 600; color: #1D1D1F; }
.pbar-score  { font-size: 13px; font-weight: 700; color: #1D1D1F; }

/* ── Strategy card ── */
.scard { background: #F5F5F7; border-radius: 16px; padding: 22px 26px; margin-bottom: 10px; }
.scard:hover { background: #EBEBED; }
.stag {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 10px;
}
.t-rec    { background: #E8F4FD; color: #0071E3; }
.t-risk   { background: #FFF0EB; color: #FF3B30; }
.t-valid  { background: #EAFAF1; color: #34C759; }
.t-metric { background: #F5F0FF; color: #AF52DE; }
.t-exp    { background: #FFF8E7; color: #FF9500; }

/* ── Journey ── */
.journey-stage { background: #F5F5F7; border-radius: 14px; padding: 20px 22px; margin-bottom: 10px; }
.journey-label { font-size: 10px; font-weight: 700; color: #6E6E73; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }
.journey-stage-name { font-size: 17px; font-weight: 700; color: #1D1D1F; margin-bottom: 10px; letter-spacing: -0.3px; }
.journey-action { font-size: 13.5px; color: #424245; margin-bottom: 10px; }
.pain-tag { display: inline-block; background: #FFE5E5; color: #FF3B30; font-size: 12px; font-weight: 500; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px; }
.opp-tag  { display: inline-block; background: #E5F8EC; color: #34C759; font-size: 12px; font-weight: 500; padding: 4px 12px; border-radius: 20px; }

/* ── PRD ── */
.prd-wrap { background: #F5F5F7; border-radius: 20px; padding: 40px 44px; max-width: 860px; margin: 0 auto; }
.prd-stamp { font-size: 11px; font-weight: 600; color: #6E6E73; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
.prd-title { font-size: 28px; font-weight: 800; color: #1D1D1F; letter-spacing: -1px; }
.prd-meta  { font-size: 12px; color: #6E6E73; margin-top: 5px; }
.prd-sec-label { font-size: 11px; font-weight: 700; color: #6E6E73; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 8px; margin-top: 24px; }
.prd-body  { font-size: 14.5px; color: #424245; line-height: 1.7; }
.prd-req   { display: flex; align-items: flex-start; gap: 12px; padding: 10px 14px; border-radius: 10px; margin-bottom: 6px; background: white; }
.prd-p0    { font-size: 11px; font-weight: 700; color: white; background: #FF3B30; padding: 2px 8px; border-radius: 5px; flex-shrink: 0; margin-top: 2px; }
.prd-p1    { font-size: 11px; font-weight: 700; color: white; background: #FF9500; padding: 2px 8px; border-radius: 5px; flex-shrink: 0; margin-top: 2px; }
.prd-p2    { font-size: 11px; font-weight: 700; color: white; background: #34C759; padding: 2px 8px; border-radius: 5px; flex-shrink: 0; margin-top: 2px; }
.prd-req-text { font-size: 13.5px; color: #424245; line-height: 1.5; }
.prd-oq   { font-size: 13.5px; color: #424245; padding: 10px 14px; background: white; border-radius: 10px; margin-bottom: 7px; }
.prd-decision { background: #1D1D1F; border-radius: 14px; padding: 22px 26px; margin-top: 28px; }
.prd-dec-label { font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.5); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
.prd-dec-body  { font-size: 15px; font-weight: 500; color: white; line-height: 1.6; }

/* ── Memo ── */
.memo-wrap { background: #F5F5F7; border-radius: 20px; padding: 40px 44px; max-width: 800px; margin: 0 auto; }
.memo-stamp { font-size: 11px; font-weight: 600; color: #6E6E73; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
.memo-product { font-size: 28px; font-weight: 800; color: #1D1D1F; letter-spacing: -1px; }
.memo-meta { text-align: right; font-size: 12px; color: #6E6E73; line-height: 1.9; }
.memo-hdr  { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; padding-bottom: 22px; border-bottom: 1px solid rgba(0,0,0,0.08); }
.memo-sec  { margin-bottom: 24px; }
.memo-sec-label { font-size: 11px; font-weight: 700; color: #6E6E73; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 7px; }
.memo-sec-body  { font-size: 15px; color: #424245; line-height: 1.7; }
.memo-decision  { background: #1D1D1F; border-radius: 14px; padding: 22px 26px; margin-top: 28px; }
.memo-dec-label { font-size: 11px; font-weight: 700; color: rgba(255,255,255,0.5); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 7px; }
.memo-dec-body  { font-size: 15px; font-weight: 500; color: white; line-height: 1.6; }

/* ── Done banner ── */
.done-banner {
    background: #F5F5F7;
    border-radius: 14px;
    padding: 16px 22px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 28px;
}
.done-text strong { display: block; font-size: 14px; font-weight: 700; color: #1D1D1F; margin-bottom: 1px; }
.done-text span   { font-size: 12.5px; color: #6E6E73; }

/* ── Divider ── */
.sec-div { height: 1px; background: rgba(0,0,0,0.06); margin: 56px 0; }

/* ── Sidebar ── */
.sb-logo { padding: 22px 20px 14px; font-size: 16px; font-weight: 700; color: #1D1D1F; letter-spacing: -0.4px; border-bottom: 1px solid rgba(0,0,0,0.06); margin-bottom: 6px; }
.sb-logo .iridescent {
    background: linear-gradient(90deg, #FF6B6B, #FFD93D, #6BCB77, #4D96FF, #C77DFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sb-section { padding: 8px 20px 4px; font-size: 10px; font-weight: 700; color: #6E6E73; letter-spacing: 1px; text-transform: uppercase; }
.sb-footer { padding: 16px 20px; font-size: 11px; color: #6E6E73; border-top: 1px solid rgba(0,0,0,0.06); margin-top: auto; line-height: 1.6; }

/* ── Buttons ── */
.stButton > button {
    background: #1D1D1F !important;
    color: white !important;
    border: none !important;
    border-radius: 980px !important;
    padding: 12px 28px !important;
    font-family: -apple-system, 'SF Pro Display', 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    width: 100% !important;
    letter-spacing: -0.1px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover { background: #424245 !important; transform: none !important; }

.stTextInput > div > div > input {
    border: 1.5px solid rgba(0,0,0,0.12) !important;
    border-radius: 12px !important;
    padding: 13px 17px !important;
    font-family: -apple-system, 'SF Pro Display', 'Inter', sans-serif !important;
    font-size: 15px !important;
    color: #1D1D1F !important;
    background: #F5F5F7 !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1D1D1F !important;
    box-shadow: none !important;
    outline: none !important;
    background: white !important;
}
.stTextInput > div > div > input::placeholder { color: #6E6E73 !important; }

.stTabs [data-baseweb="tab-list"] { gap: 2px; background: #F5F5F7; border-radius: 10px; padding: 3px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 7px 16px; font-size: 13px; font-weight: 500; color: #6E6E73; }
.stTabs [aria-selected="true"] { background: white !important; color: #1D1D1F !important; font-weight: 600 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }

/* ── Example chip buttons ── */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(255,255,255,0.75) !important;
    color: #1D1D1F !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 20px !important;
    padding: 5px 12px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    width: 100% !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(255,255,255,0.95) !important;
    transform: none !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "api_key": "", "product_input": "", "demo_mode": False,
        "analysis_done": False, "snapshot": None, "metrics": None,
        "features": None, "strategy": None, "memo": None,
        "competitive": None, "user_journey": None, "prd": None,
        "active_section": "snapshot", "app_store_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
# OPENAI
# ─────────────────────────────────────────────
def call_gpt(system_prompt: str, user_prompt: str) -> dict:
    client = OpenAI(api_key=st.session_state.api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        response_format={"type": "json_object"},
        temperature=0.72, max_tokens=2200,
    )
    return json.loads(response.choices[0].message.content)


# ─────────────────────────────────────────────
# GENERATION FUNCTIONS
# ─────────────────────────────────────────────
def generate_snapshot(product):
    sys = """Senior PM doing a product teardown. Return ONLY valid JSON:
{"summary":"","target_users":"","user_problem":"","value_proposition":"","north_star_metric":"","north_star_why":"","category":"","stage":"Growth|Maturity|Decline|Launch","confidence":"High|Medium","teardown_insight":""}"""
    return call_gpt(sys, f"Analyze: {product}")

def generate_metrics(product):
    sys = """Product analytics lead. Return ONLY valid JSON:
{"acquisition":[{"name":"","value":"","benchmark":"","score":7}],"engagement":[{"name":"","value":"","benchmark":"","score":8}],"retention":[{"name":"","value":"","benchmark":"","score":6}],"business":[{"name":"","value":"","benchmark":"","score":7}],"radar":{"Acquisition":7,"Engagement":8,"Retention":6,"Monetization":7,"Virality":5,"NPS":8}}
3-4 metrics per category. Scores 1-10."""
    return call_gpt(sys, f"KPI framework for: {product}")

def generate_features(product):
    sys = """Product strategist. Return ONLY valid JSON:
{"features":[{"feature":"","reason":"","impact":8,"effort":4,"priority_score":8.4,"priority":"High"}]}
8 features. Priority score = impact*(11-effort)/10. High>=6.5, Medium 4-6.4, Low<4."""
    return call_gpt(sys, f"Feature opportunities for: {product}")

def generate_strategy(product):
    sys = """VP of Product. Return ONLY valid JSON:
{"recommendations":[{"title":"","detail":""}],"risks":[{"title":"","detail":""}],"validate_first":[{"title":"","detail":""}],"success_metrics":[{"metric":"","target":"","timeframe":""}],"experiments":[{"title":"","hypothesis":""}]}
3 items each. Be specific."""
    return call_gpt(sys, f"Product strategy for: {product}")

def generate_memo(product, snapshot, strategy):
    sys = """CPO writing board memo. Return ONLY valid JSON:
{"problem":"","user":"","solution":"","metrics":"","decision":""}"""
    return call_gpt(sys, f"Product: {product}\n{json.dumps(snapshot)}\n{json.dumps(strategy)}")

def generate_competitive(product):
    sys = """Product strategist. Return ONLY valid JSON:
{"products":["A","B","C"],"dimensions":["d1","d2","d3","d4","d5","d6","d7","d8"],"scores":{"A":[7,8,6,9,7,8,7,8],"B":[8,6,5,7,8,9,5,9],"C":[7,6,4,5,9,6,5,7]},"insights":["i1","i2","i3","i4"]}"""
    return call_gpt(sys, f"Competitive landscape for: {product}")

def generate_user_journey(product):
    sys = """UX researcher. Return ONLY valid JSON:
{"stages":["s1","s2","s3","s4","s5","s6"],"actions":["a1","a2","a3","a4","a5","a6"],"pain_points":["p1","p2","p3","p4","p5","p6"],"opportunities":["o1","o2","o3","o4","o5","o6"]}
Exactly 6 stages."""
    return call_gpt(sys, f"User journey for: {product}")

def generate_prd(product, snapshot, features):
    sys = """Senior PM writing PRD. Return ONLY valid JSON:
{"feature":"","status":"Proposed","owner":"","problem":"","goals":["g1","g2","g3"],"non_goals":["n1","n2","n3"],"requirements":[{"priority":"P0","requirement":""},{"priority":"P1","requirement":""},{"priority":"P2","requirement":""}],"success_metrics":["m1","m2","m3","m4"],"open_questions":["q1","q2","q3"]}
2x P0, 2x P1, 2x P2."""
    top = features.get("features", [{}])[0].get("feature", "top feature")
    return call_gpt(sys, f"PRD for {product}, feature: {top}")


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────
def build_radar(radar_data):
    cats = list(radar_data.keys())
    vals = list(radar_data.values())
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill='toself', fillcolor='rgba(29,29,31,0.06)',
        line=dict(color='#1D1D1F', width=2),
        marker=dict(size=6, color='#1D1D1F', line=dict(color='white', width=2)),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,10], tickfont=dict(size=10,color='#6E6E73',family='Inter'), gridcolor='rgba(0,0,0,0.06)', linecolor='rgba(0,0,0,0.06)'),
            angularaxis=dict(tickfont=dict(size=12,color='#1D1D1F',family='Inter'), gridcolor='rgba(0,0,0,0.06)', linecolor='rgba(0,0,0,0.06)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, margin=dict(t=28,b=28,l=60,r=60), height=380,
    )
    return fig

def build_scatter(features):
    df = pd.DataFrame(features)
    color_map = {'High':'#FF3B30','Medium':'#FF9500','Low':'#34C759'}
    fig = go.Figure()
    for pri, col in color_map.items():
        sub = df[df['priority']==pri]
        if sub.empty: continue
        fig.add_trace(go.Scatter(
            x=sub['effort'], y=sub['impact'], mode='markers+text', name=pri,
            marker=dict(size=13, color=col, opacity=0.9, line=dict(color='white',width=2)),
            text=sub['feature'], textposition='top center',
            textfont=dict(size=9.5, family='Inter', color='#424245'),
            hovertemplate='<b>%{text}</b><br>Impact: %{y}/10<br>Effort: %{x}/10<extra></extra>',
        ))
    fig.add_shape(type='line',x0=5,x1=5,y0=0,y1=11,line=dict(color='rgba(0,0,0,0.12)',dash='dot',width=1.5))
    fig.add_shape(type='line',x0=0,x1=11,y0=5,y1=5,line=dict(color='rgba(0,0,0,0.12)',dash='dot',width=1.5))
    fig.add_annotation(x=2.5,y=10.5,text="Quick Wins ✓",font=dict(size=10,color='#34C759',family='Inter'),showarrow=False)
    fig.add_annotation(x=8.5,y=10.5,text="Big Bets",font=dict(size=10,color='#FF9500',family='Inter'),showarrow=False)
    fig.add_annotation(x=2.5,y=0.5,text="Fill-ins",font=dict(size=10,color='#6E6E73',family='Inter'),showarrow=False)
    fig.add_annotation(x=8.5,y=0.5,text="Avoid",font=dict(size=10,color='#FF3B30',family='Inter'),showarrow=False)
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(245,245,247,0.6)',
        xaxis=dict(title='Effort →',range=[0,11],tickfont=dict(family='Inter',size=11,color='#6E6E73'),gridcolor='rgba(0,0,0,0.05)',showline=True,linecolor='rgba(0,0,0,0.08)'),
        yaxis=dict(title='Impact →',range=[0,11],tickfont=dict(family='Inter',size=11,color='#6E6E73'),gridcolor='rgba(0,0,0,0.05)',showline=True,linecolor='rgba(0,0,0,0.08)'),
        legend=dict(font=dict(family='Inter',size=12),bgcolor='rgba(255,255,255,0.9)',bordercolor='rgba(0,0,0,0.08)',borderwidth=1),
        margin=dict(t=24,b=48,l=56,r=20),height=420,
    )
    return fig

def build_competitive_radar(comp_data):
    products = comp_data.get('products',[])
    dims = comp_data.get('dimensions',[])
    scores = comp_data.get('scores',{})
    colors = [('rgba(29,29,31,0.1)','#1D1D1F'),('rgba(255,59,48,0.1)','#FF3B30'),('rgba(52,199,89,0.1)','#34C759')]
    fig = go.Figure()
    for i, prod in enumerate(products):
        vals = scores.get(prod,[])
        if not vals: continue
        fc, lc = colors[i % len(colors)]
        fig.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=dims+[dims[0]],
            fill='toself', fillcolor=fc,
            line=dict(color=lc,width=2), name=prod, marker=dict(size=5),
        ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True,range=[0,10],tickfont=dict(size=10,color='#6E6E73',family='Inter'),gridcolor='rgba(0,0,0,0.06)',linecolor='rgba(0,0,0,0.06)'),
            angularaxis=dict(tickfont=dict(size=11,color='#1D1D1F',family='Inter'),gridcolor='rgba(0,0,0,0.06)',linecolor='rgba(0,0,0,0.06)'),
        ),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(font=dict(family='Inter',size=12),bgcolor='rgba(255,255,255,0.9)',bordercolor='rgba(0,0,0,0.08)',borderwidth=1),
        margin=dict(t=28,b=28,l=60,r=60), height=420,
    )
    return fig


# ─────────────────────────────────────────────
# PRODUCT HERO BANNER
# ─────────────────────────────────────────────
def render_product_hero(product: str):
    app_data = st.session_state.get("app_store_data") or {}
    icon_url = app_data.get("icon","")
    screenshots = app_data.get("screenshots",[])
    developer = app_data.get("developer","")
    genre = app_data.get("genre","")
    rating = app_data.get("rating",0)
    price = app_data.get("price","")
    stage = ""
    category = ""
    if st.session_state.snapshot:
        stage = st.session_state.snapshot.get("stage","")
        category = st.session_state.snapshot.get("category","")

    logo_html = f'<img src="{icon_url}" class="product-logo" onerror="this.style.display=\'none\'" />' if icon_url else f'<div class="product-logo-placeholder">📱</div>'

    tags = []
    if category: tags.append(category)
    if stage: tags.append(stage)
    if rating: tags.append(f"⭐ {rating}")
    if price: tags.append(price)
    tags_html = "".join([f'<span class="hero-tag">{t}</span>' for t in tags])

    st.markdown(f"""
    <div class="product-hero">
        {logo_html}
        <div class="product-hero-info">
            <div class="product-hero-name">{product}</div>
            <div class="product-hero-dev">{developer if developer else "Product Analysis"}</div>
            <div class="product-hero-tags">{tags_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if screenshots:
        imgs_html = "".join([f'<img src="{s}" class="screenshot-img" />' for s in screenshots])
        st.markdown(f'<div class="screenshots-row">{imgs_html}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="sb-logo">Product<span class="iridescent">Lens</span> AI</div>', unsafe_allow_html=True)

        if st.session_state.analysis_done:
            product = st.session_state.product_input or DEMO_PRODUCT
            mode = "🟡 Demo" if st.session_state.demo_mode else "🟢 Live"
            st.markdown(f"""
            <div style="padding:10px 20px 16px;border-bottom:1px solid rgba(0,0,0,0.06);">
                <div style="font-size:11px;color:#6E6E73;font-weight:600;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:3px;">{mode}</div>
                <div style="font-size:16px;font-weight:700;color:#1D1D1F;">{product}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="sb-section">Analysis</div>', unsafe_allow_html=True)
            sections = [
                ("snapshot","📋","Product Snapshot"),
                ("metrics","📊","KPI Framework"),
                ("features","🧩","Feature Opportunities"),
                ("competitive","⚔️","Competitive Analysis"),
                ("journey","🗺️","User Journey"),
                ("strategy","🎯","Product Strategy"),
                ("prd","📄","PRD Snippet"),
                ("memo","✍️","Executive Memo"),
            ]
            for key, icon, label in sections:
                if st.button(f"{icon}  {label}", key=f"nav_{key}"):
                    st.session_state.active_section = key
                    st.rerun()

            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sb-section" style="margin-top:4px;">Actions</div>', unsafe_allow_html=True)
            if st.button("↩  New Analysis"):
                for k in ["analysis_done","snapshot","metrics","features","strategy","memo","competitive","user_journey","prd","app_store_data"]:
                    st.session_state[k] = None if k != "analysis_done" else False
                st.session_state.product_input = ""
                st.session_state.demo_mode = False
                st.session_state.active_section = "snapshot"
                st.rerun()
        else:
            st.markdown("""
            <div style="padding:16px 20px;">
                <div style="font-size:13px;color:#6E6E73;line-height:1.7;">
                    Enter any product name for a full PM teardown — or click <strong>Load Demo</strong> for an instant Spotify analysis.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sb-footer">Built for AI PM recruiting<br>Product Intelligence Platform</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def sec_header(eye, title, sub=None):
    sub_html = f'<div class="sec-sub">{sub}</div>' if sub else ''
    st.markdown(f'<div class="sec-hdr"><div class="sec-eye">{eye}</div><div class="sec-title">{title}</div>{sub_html}</div>', unsafe_allow_html=True)

def pcard(icon, label, title, body):
    st.markdown(f'<div class="pcard"><span class="pcard-icon">{icon}</span><div class="pcard-label">{label}</div><div class="pcard-title">{title}</div><div class="pcard-body">{body}</div></div>', unsafe_allow_html=True)

def scard(tag_cls, tag_txt, title, body):
    st.markdown(f'<div class="scard"><div class="stag {tag_cls}">{tag_txt}</div><div class="pcard-title" style="margin-bottom:5px;">{title}</div><div class="pcard-body">{body}</div></div>', unsafe_allow_html=True)

def pbar(name, score):
    st.markdown(f'<div class="pbar-block"><div class="pbar-row"><span class="pbar-name">{name}</span><span class="pbar-score">{score}/10</span></div><div class="prog-track"><div class="prog-fill" style="width:{score*10}%"></div></div></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SCREENS
# ─────────────────────────────────────────────
def screen_landing():
    st.markdown("""
    <div class="hero">
        <span class="hero-eyebrow">AI Product Intelligence</span>
        <h1 class="hero-h1">Turn products into<br><span class="iridescent">decisions.</span></h1>
        <p class="hero-sub" style="display:block;width:100%;max-width:600px;margin-left:auto;margin-right:auto;text-align:center;">PM-quality product analysis in seconds. Built to show how a product thinker thinks.</p>
    </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown('<div class="demo-notice" style="background:rgba(255,255,255,0.6);backdrop-filter:blur(10px);">💡 <strong>No API key?</strong> Click Load Demo for an instant Spotify teardown — no setup needed.</div>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:12px;font-weight:600;color:#6E6E73;">OpenAI API Key</span>', unsafe_allow_html=True)
        api_val = st.text_input("api", value=st.session_state.api_key, placeholder="sk-... (optional if using demo)", type="password", label_visibility="collapsed")
        if api_val: st.session_state.api_key = api_val
        st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:12px;font-weight:600;color:#6E6E73;">Product or App Name</span>', unsafe_allow_html=True)
        prod_val = st.text_input("product", value=st.session_state.product_input, placeholder="e.g. Spotify, Duolingo, Uber Eats...", label_visibility="collapsed")
        if prod_val: st.session_state.product_input = prod_val
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        b1, b2 = st.columns([2,1])
        with b1:
            if st.button("✨ Generate Product Insights"):
                if not st.session_state.api_key: st.error("Enter your OpenAI API key, or use Load Demo →")
                elif not st.session_state.product_input.strip(): st.error("Enter a product name first.")
                else: run_analysis(demo=False)
        with b2:
            if st.button("⚡ Load Demo"): run_analysis(demo=True)
        st.markdown('<div style="margin-top:20px;text-align:center;"><p style="font-size:11px;color:#6E6E73;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:10px;">Try these</p></div>', unsafe_allow_html=True)

        examples = [
            ("📸", "Instagram"), ("🍔", "Uber Eats"), ("🎵", "Spotify"),
            ("🦆", "Duolingo"), ("📝", "Notion"), ("🥗", "AI Meal Planner"),
        ]
        row1 = st.columns(3)
        row2 = st.columns(3)
        rows = row1 + row2
        for col, (icon, name) in zip(rows, examples):
            with col:
                if st.button(f"{icon} {name}", key=f"chip_{name}"):
                    st.session_state.product_input = name
                    if not st.session_state.api_key:
                        st.warning("Enter your OpenAI API key above, or click ⚡ Load Demo for a free Spotify teardown.")
                    else:
                        run_analysis(demo=False)
                    st.rerun()

        st.markdown('<p style="font-size:11px;color:#6E6E73;text-align:center;margin-top:16px;">Need an API key? Get one free at <strong>platform.openai.com/api-keys</strong></p>', unsafe_allow_html=True)


def run_analysis(demo: bool):
    if demo:
        st.session_state.demo_mode = True
        st.session_state.product_input = DEMO_PRODUCT
        for k, v in DEMO_DATA.items():
            st.session_state[k] = v
        st.session_state.app_store_data = fetch_app_store_data(DEMO_PRODUCT)
        st.session_state.analysis_done = True
        st.session_state.active_section = "snapshot"
        st.rerun()
        return

    product = st.session_state.product_input.strip()
    with st.spinner("Analyzing..."):
        bar = st.progress(0)
        try:
            bar.progress(5,  "Fetching app data...")
            st.session_state.app_store_data = fetch_app_store_data(product)
            bar.progress(12, "Building product snapshot...")
            st.session_state.snapshot = generate_snapshot(product)
            bar.progress(26, "Generating KPI framework...")
            st.session_state.metrics = generate_metrics(product)
            bar.progress(40, "Mapping feature opportunities...")
            st.session_state.features = generate_features(product)
            bar.progress(54, "Running competitive analysis...")
            st.session_state.competitive = generate_competitive(product)
            bar.progress(66, "Mapping user journey...")
            st.session_state.user_journey = generate_user_journey(product)
            bar.progress(78, "Formulating strategy...")
            st.session_state.strategy = generate_strategy(product)
            bar.progress(90, "Writing PRD and memo...")
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
    sec_header("01 — Product Snapshot", f"{product} Teardown", "Summary · Users · Problem · Value Prop · North Star")
    render_product_hero(product)
    col1, col2 = st.columns(2)
    with col1:
        pcard("📋","Product Summary","Overview", snap.get("summary",""))
        pcard("👤","Target Users","Primary Persona", snap.get("target_users",""))
        pcard("🔥","Core User Problem","Pain Point", snap.get("user_problem",""))
    with col2:
        pcard("💡","Value Proposition","Why Users Choose It", snap.get("value_proposition",""))
        st.markdown(f"""
        <div class="pcard">
            <span class="pcard-icon">⭐</span>
            <div class="pcard-label">North Star Metric</div>
            <div class="pcard-title" style="font-size:20px;">{snap.get("north_star_metric","")}</div>
            <div class="pcard-body">{snap.get("north_star_why","")}</div>
        </div>""", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        stage = snap.get("stage","—")
        with c1:
            st.markdown(f'<div class="mcard" style="text-align:left;"><div class="mcard-name">Category</div><div style="font-size:16px;font-weight:700;color:#1D1D1F;margin-top:5px;">{snap.get("category","—")}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="mcard" style="text-align:left;"><div class="mcard-name">Stage</div><div style="font-size:16px;font-weight:700;color:#1D1D1F;margin-top:5px;">{stage}</div></div>', unsafe_allow_html=True)
    insight = snap.get("teardown_insight","")
    if insight:
        st.markdown(f'<div class="insight-box" style="margin-top:8px;"><div class="insight-label">🔍 PM Teardown Insight</div><div class="insight-body">{insight}</div></div>', unsafe_allow_html=True)


def screen_metrics():
    metrics = st.session_state.metrics
    product = st.session_state.product_input
    sec_header("02 — KPI Framework", f"Product Metrics for {product}", "Acquisition · Engagement · Retention · Business")
    c1, c2 = st.columns([1.2,0.8])
    with c1:
        if metrics.get("radar"): st.plotly_chart(build_radar(metrics["radar"]), use_container_width=True)
    with c2:
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:11px;font-weight:700;color:#6E6E73;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;">Scores</div>', unsafe_allow_html=True)
        for dim, score in metrics.get("radar",{}).items():
            pbar(dim, score)
    for cat_key, icon, label in [("acquisition","🚀","Acquisition"),("engagement","💬","Engagement"),("retention","🔄","Retention"),("business","💰","Business")]:
        data = metrics.get(cat_key,[])
        if not data: continue
        st.markdown(f'<div style="display:flex;align-items:center;gap:7px;margin:22px 0 10px;"><span style="font-size:16px;">{icon}</span><span style="font-size:14px;font-weight:700;color:#1D1D1F;">{label} Metrics</span></div>', unsafe_allow_html=True)
        cols = st.columns(len(data))
        for col, m in zip(cols, data):
            with col:
                st.markdown(f'<div class="mcard"><div class="mcard-val">{m.get("value","—")}</div><div class="mcard-name">{m.get("name","")}</div><div class="mcard-bench">vs {m.get("benchmark","—")}</div><div class="prog-track"><div class="prog-fill" style="width:{m.get("score",5)*10}%"></div></div><div style="text-align:right;font-size:10px;color:#6E6E73;margin-top:3px;">{m.get("score",5)}/10</div></div>', unsafe_allow_html=True)


def screen_features():
    features_data = st.session_state.features.get("features",[])
    product = st.session_state.product_input
    sec_header("03 — Feature Opportunities", f"Prioritized Roadmap for {product}", "Impact × Effort matrix with PM prioritization scoring")
    if features_data: st.plotly_chart(build_scatter(features_data), use_container_width=True)
    df = pd.DataFrame(features_data)
    if not df.empty:
        df_d = df[["feature","reason","impact","effort","priority_score","priority"]].copy()
        df_d.columns = ["Feature","Reason","Impact","Effort","Score","Priority"]
        df_d = df_d.sort_values("Score", ascending=False).reset_index(drop=True)
        st.dataframe(df_d, use_container_width=True, hide_index=True,
            column_config={
                "Feature": st.column_config.TextColumn("Feature", width="medium"),
                "Reason":  st.column_config.TextColumn("Reason", width="large"),
                "Impact":  st.column_config.ProgressColumn("Impact", min_value=0, max_value=10, format="%d"),
                "Effort":  st.column_config.ProgressColumn("Effort", min_value=0, max_value=10, format="%d"),
                "Score":   st.column_config.NumberColumn("Score", format="%.1f"),
                "Priority":st.column_config.TextColumn("Priority"),
            })


def screen_competitive():
    comp = st.session_state.competitive
    product = st.session_state.product_input
    sec_header("04 — Competitive Analysis", f"Market Positioning for {product}", "Side-by-side comparison across dimensions that matter")
    if not comp: st.info("Competitive data unavailable."); return
    c1, c2 = st.columns([1.2,0.8])
    with c1:
        st.plotly_chart(build_competitive_radar(comp), use_container_width=True)
    with c2:
        products = comp.get('products',[])
        dims = comp.get('dimensions',[])
        scores = comp.get('scores',{})
        if dims and products and scores:
            st.markdown('<div style="font-size:11px;font-weight:700;color:#6E6E73;letter-spacing:1px;text-transform:uppercase;margin-bottom:12px;margin-top:16px;">Score Breakdown</div>', unsafe_allow_html=True)
            df_comp = pd.DataFrame({"Dimension": dims, **{p: scores.get(p,[0]*len(dims)) for p in products}})
            st.dataframe(df_comp, use_container_width=True, hide_index=True)
    for i, ins in enumerate(comp.get("insights",[])):
        icons = ["🥇","⚔️","🎯","💡"]
        st.markdown(f'<div class="scard" style="padding:16px 20px;"><div style="font-size:13.5px;color:#424245;line-height:1.6;">{icons[i%4]} {ins}</div></div>', unsafe_allow_html=True)


def screen_journey():
    jd = st.session_state.user_journey
    product = st.session_state.product_input
    sec_header("05 — User Journey Map", f"End-to-End Experience for {product}", "What users do · Where they struggle · PM opportunities")
    if not jd: st.info("User journey data unavailable."); return
    stages = jd.get("stages",[])
    for i, stage in enumerate(stages):
        action = jd.get("actions",[])[i] if i < len(jd.get("actions",[])) else ""
        pain   = jd.get("pain_points",[])[i] if i < len(jd.get("pain_points",[])) else ""
        opp    = jd.get("opportunities",[])[i] if i < len(jd.get("opportunities",[])) else ""
        st.markdown(f'<div class="journey-stage"><div class="journey-label">Stage {i+1} of {len(stages)}</div><div class="journey-stage-name">{stage}</div><div class="journey-action">👤 {action}</div><div><span class="pain-tag">⚠️ {pain}</span></div><div style="margin-top:8px;"><span class="opp-tag">✓ {opp}</span></div></div>', unsafe_allow_html=True)


def screen_strategy():
    strategy = st.session_state.strategy
    product = st.session_state.product_input
    sec_header("06 — Product Strategy", f"Executive Playbook for {product}", "Recommendations · Risks · Experiments · Metrics")
    tabs = st.tabs(["🎯 Recommendations","⚠️ Risks","🔬 Validate First","📊 Success Metrics","🧪 Experiments"])
    with tabs[0]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("recommendations",[]): scard("t-rec","Recommendation",item.get("title",""),item.get("detail",""))
    with tabs[1]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("risks",[]): scard("t-risk","Risk",item.get("title",""),item.get("detail",""))
    with tabs[2]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("validate_first",[]): scard("t-valid","Validate",item.get("title",""),item.get("detail",""))
    with tabs[3]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("success_metrics",[]):
            st.markdown(f'<div class="scard"><div class="stag t-metric">Success Metric</div><div class="pcard-title" style="margin-bottom:5px;">{item.get("metric","")}</div><div class="pcard-body"><strong>Target:</strong> {item.get("target","")} · <strong>Timeframe:</strong> {item.get("timeframe","")}</div></div>', unsafe_allow_html=True)
    with tabs[4]:
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        for item in strategy.get("experiments",[]): scard("t-exp","Experiment",item.get("title",""),item.get("hypothesis",""))


def screen_prd():
    prd = st.session_state.prd
    product = st.session_state.product_input
    sec_header("07 — PRD Snippet","Product Requirements Document","The PM artifact that turns strategy into a buildable spec")
    if not prd: st.info("PRD data unavailable."); return
    today = datetime.date.today().strftime("%B %d, %Y")
    status = prd.get("status","Proposed")
    goals_html     = "".join([f'<li style="margin-bottom:5px;font-size:14px;color:#424245;">{g}</li>' for g in prd.get("goals",[])])
    non_goals_html = "".join([f'<li style="margin-bottom:5px;font-size:14px;color:#6E6E73;">{g}</li>' for g in prd.get("non_goals",[])])
    reqs_html = ""
    for r in prd.get("requirements",[]):
        p = r.get("priority","P2")
        cls = "prd-p0" if p=="P0" else ("prd-p1" if p=="P1" else "prd-p2")
        reqs_html += f'<div class="prd-req"><span class="{cls}">{p}</span><span class="prd-req-text">{r.get("requirement","")}</span></div>'
    metrics_html = "".join([f'<li style="margin-bottom:5px;font-size:14px;color:#424245;">{m}</li>' for m in prd.get("success_metrics",[])])
    oqs_html = "".join([f'<div class="prd-oq">❓ {q}</div>' for q in prd.get("open_questions",[])])
    memo_decision = (st.session_state.memo or {}).get("decision","Awaiting executive alignment.")
    st.markdown(f"""
    <div class="prd-wrap">
        <div class="prd-header" style="border-bottom:1px solid rgba(0,0,0,0.08);padding-bottom:22px;margin-bottom:24px;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div class="prd-stamp">Product Requirements Document</div>
                    <div class="prd-title">{prd.get("feature","")}</div>
                    <div class="prd-meta">{product} · {prd.get("owner","")} · {today}</div>
                </div>
                <div style="background:#F5F5F7;color:#1D1D1F;font-size:11.5px;font-weight:600;padding:5px 14px;border-radius:20px;flex-shrink:0;">{status}</div>
            </div>
        </div>
        <div class="prd-sec-label">Problem Statement</div>
        <div class="prd-body">{prd.get("problem","")}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:4px;">
            <div><div class="prd-sec-label">Goals</div><ul style="list-style:none;padding:0;">{goals_html}</ul></div>
            <div><div class="prd-sec-label">Non-Goals</div><ul style="list-style:none;padding:0;">{non_goals_html}</ul></div>
        </div>
        <div class="prd-sec-label">Requirements</div>{reqs_html}
        <div class="prd-sec-label">Success Metrics</div>
        <ul style="list-style:none;padding:0;">{metrics_html}</ul>
        <div class="prd-sec-label">Open Questions</div>{oqs_html}
        <div class="prd-decision">
            <div class="prd-dec-label">✦ Decision</div>
            <div class="prd-dec-body">{memo_decision}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    prd_text = f"PRD: {prd.get('feature','')} — {product}\n{'='*60}\n\nPROBLEM\n{prd.get('problem','')}\n\nGOALS\n" + "\n".join([f"• {g}" for g in prd.get("goals",[])]) + "\n\nNON-GOALS\n" + "\n".join([f"• {g}" for g in prd.get("non_goals",[])]) + "\n\nREQUIREMENTS\n" + "\n".join([f"[{r.get('priority','')}] {r.get('requirement','')}" for r in prd.get("requirements",[])]) + "\n\nSUCCESS METRICS\n" + "\n".join([f"• {m}" for m in prd.get("success_metrics",[])]) + "\n\nOPEN QUESTIONS\n" + "\n".join([f"? {q}" for q in prd.get("open_questions",[])])
    _, dc, _ = st.columns([1,1,1])
    with dc:
        st.download_button("⬇ Download PRD", prd_text, file_name=f"prd_{product.lower().replace(' ','_')}.txt", mime="text/plain")


def screen_memo():
    memo = st.session_state.memo
    product = st.session_state.product_input
    today = datetime.date.today().strftime("%B %d, %Y")
    sec_header("08 — Executive Memo","CPO-Level Product Brief","The one-pager a PM would bring to a product review")
    st.markdown(f"""
    <div class="memo-wrap">
        <div class="memo-hdr">
            <div><div class="memo-stamp">Product Memo · Confidential</div><div class="memo-product">{product}</div></div>
            <div class="memo-meta">ProductLens AI<br>{today}<br><span style="color:#1D1D1F;font-weight:600;">AI Analysis</span></div>
        </div>
        <div class="memo-sec"><div class="memo-sec-label">01 · Problem</div><div class="memo-sec-body">{memo.get("problem","")}</div></div>
        <div class="memo-sec"><div class="memo-sec-label">02 · User</div><div class="memo-sec-body">{memo.get("user","")}</div></div>
        <div class="memo-sec"><div class="memo-sec-label">03 · Solution</div><div class="memo-sec-body">{memo.get("solution","")}</div></div>
        <div class="memo-sec"><div class="memo-sec-label">04 · Metrics</div><div class="memo-sec-body">{memo.get("metrics","")}</div></div>
        <div class="memo-decision"><div class="memo-dec-label">✦ Decision</div><div class="memo-dec-body">{memo.get("decision","")}</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
    memo_text = f"PRODUCT MEMO — {product.upper()}\n{today}\n{'='*60}\n\nPROBLEM\n{memo.get('problem','')}\n\nUSER\n{memo.get('user','')}\n\nSOLUTION\n{memo.get('solution','')}\n\nMETRICS\n{memo.get('metrics','')}\n\nDECISION\n{memo.get('decision','')}"
    _, dc, _ = st.columns([1,1,1])
    with dc:
        st.download_button("⬇ Download Memo", memo_text, file_name=f"memo_{product.lower().replace(' ','_')}.txt", mime="text/plain")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    render_sidebar()
    st.markdown("""
    <div class="top-nav">
        <div class="nav-logo">Product<span class="iridescent">Lens</span> AI</div>
        <div class="nav-tag">AI Product Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.analysis_done:
        screen_landing()
        return

    product = st.session_state.product_input
    mode_label = "🟡 Demo Mode — Spotify" if st.session_state.demo_mode else f"🟢 Live — {product}"
    st.markdown(f'<div class="done-banner"><div style="font-size:20px;">✅</div><div class="done-text"><strong>{mode_label}</strong><span>8 sections generated · Navigate with the sidebar · Download outputs below</span></div></div>', unsafe_allow_html=True)

    dispatch = {
        "snapshot": screen_snapshot, "metrics": screen_metrics,
        "features": screen_features, "competitive": screen_competitive,
        "journey": screen_journey, "strategy": screen_strategy,
        "prd": screen_prd, "memo": screen_memo,
    }
    dispatch.get(st.session_state.active_section, screen_snapshot)()

    st.markdown("""
    <div style="text-align:center;padding:48px 0 20px;border-top:1px solid rgba(0,0,0,0.06);margin-top:52px;">
        <div style="font-size:15px;font-weight:700;color:#1D1D1F;margin-bottom:4px;">ProductLens AI</div>
        <div style="font-size:12px;color:#6E6E73;">Turn products into decisions. · ProductLens AI</div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
