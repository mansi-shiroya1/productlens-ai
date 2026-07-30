# Pre-seeded Spotify demo — zero API key required
SPOTIFY_DEMO = {
    "product_input": "Spotify",
    "snapshot": {
        "summary": "Spotify is the world's leading audio streaming platform with 600M+ users across 180+ markets. It offers on-demand music, podcasts, and audiobooks through a freemium model that converts free listeners into paid subscribers via personalized discovery and exclusive content.",
        "target_users": "Primarily 18–34 year-old digital natives who use music as a constant companion — commuting, working out, studying, or socializing. Secondary: podcast listeners 25–45 seeking on-demand audio content. Power users are playlist curators and music discovery enthusiasts.",
        "user_problem": "Music is deeply personal but discovery is broken — listeners get stuck in taste bubbles, struggle to find new artists aligned to their mood, and lose music context when switching between devices or social contexts.",
        "value_proposition": "The only platform that knows you well enough to be your personal DJ — surfacing the right track at the right moment, across every device, with zero friction.",
        "north_star_metric": "Monthly Active Users (MAU) × Average Stream Minutes per User",
        "north_star_why": "MAU alone misses depth of engagement. The compound metric captures both breadth of reach and depth of habit — the two levers that drive subscriber conversion and retention simultaneously.",
        "category": "Audio Streaming",
        "stage": "Maturity"
    },
    "metrics": {
        "acquisition": [
            {"name": "Monthly Active Users", "value": "602M", "benchmark": "Apple Music: ~90M", "score": 10},
            {"name": "New User Growth (YoY)", "value": "+14%", "benchmark": "Industry avg: 8%", "score": 8},
            {"name": "Free-to-Paid Conversion", "value": "27%", "benchmark": "Streaming avg: 15–20%", "score": 8},
        ],
        "engagement": [
            {"name": "Avg Daily Listening", "value": "30 min/day", "benchmark": "Pandora: 22 min", "score": 7},
            {"name": "Playlist Saves/User/Mo", "value": "4.2", "benchmark": "Industry: 2.1", "score": 8},
            {"name": "Podcast Listeners", "value": "250M", "benchmark": "Apple Podcasts: ~100M", "score": 9},
        ],
        "retention": [
            {"name": "12-Month Retention", "value": "~80%", "benchmark": "Streaming avg: 65%", "score": 9},
            {"name": "Churn Rate (Premium)", "value": "3.2%/mo", "benchmark": "Netflix: 2.4%", "score": 6},
            {"name": "D7 Retention (New)", "value": "61%", "benchmark": "Social avg: 45%", "score": 8},
        ],
        "business": [
            {"name": "Premium Subscribers", "value": "236M", "benchmark": "Apple Music: 90M", "score": 10},
            {"name": "Revenue (2023)", "value": "€13.2B", "benchmark": "YoY +13%", "score": 8},
            {"name": "Gross Margin", "value": "26.7%", "benchmark": "Target: 30%+", "score": 6},
        ],
        "radar": {
            "Acquisition": 9,
            "Engagement": 8,
            "Retention": 8,
            "Monetization": 7,
            "Virality": 8,
            "NPS": 8
        }
    },
    "features": {
        "features": [
            {"feature": "Collaborative Listening Rooms", "reason": "Social listening is the #1 requested feature — users want to share real-time listening with friends without third-party apps", "impact": 9, "effort": 6, "priority_score": 9.0, "priority": "High"},
            {"feature": "AI Mood-to-Playlist Generator", "reason": "Users describe their mood in natural language; AI curates a playlist instantly. Leverages existing LLM investment.", "impact": 8, "effort": 4, "priority_score": 11.2, "priority": "High"},
            {"feature": "Lyrics Sing-Along Mode", "reason": "TikTok/Instagram users share lyrics clips — Spotify loses this engagement surface to competitors", "impact": 7, "effort": 3, "priority_score": 11.2, "priority": "High"},
            {"feature": "Artist Video Integration", "reason": "YouTube holds music video discovery. Spotify surrenders 28% of music sessions by not offering video.", "impact": 8, "effort": 8, "priority_score": 6.4, "priority": "Medium"},
            {"feature": "Personalized Podcast Clips", "reason": "Short-form audio clips (60s) matched to user taste — bridges podcast discovery and TikTok-era attention spans", "impact": 7, "effort": 5, "priority_score": 8.4, "priority": "High"},
            {"feature": "Offline Smart Downloads", "reason": "Predictively download content before the user commutes — zero friction for the most common offline use case", "impact": 6, "effort": 4, "priority_score": 8.4, "priority": "High"},
            {"feature": "Concert & Event Integration", "reason": "Connect listening data to live events — users who stream an artist get notified when they tour nearby", "impact": 7, "effort": 6, "priority_score": 7.0, "priority": "High"},
            {"feature": "DJ Mode for Parties", "reason": "Auto-transitions, BPM matching, crowd-read features. Captures the social/event use case currently owned by Apple Music", "impact": 6, "effort": 7, "priority_score": 4.8, "priority": "Medium"},
        ]
    },
    "strategy": {
        "recommendations": [
            {"title": "Own the Social Layer Before a Competitor Does", "detail": "Spotify has 600M users but zero social graph. Apple Music has Shareplay. The window to build native collaborative listening and social features is 12–18 months before it becomes a retention liability. Invest in real-time listening rooms, friend activity feeds, and shared playlist notifications."},
            {"title": "Convert the Gross Margin Problem into a Product Strategy", "detail": "At 26.7% gross margin vs Netflix at 40%+, Spotify's label royalty structure is the core business risk. The product response is to grow owned content (podcasts, audiobooks, DJ AI) that carries higher margins — and to build tools that make Spotify indispensable to artists, reducing leverage labels hold."},
            {"title": "Make AI the Core Discovery Surface, Not a Feature", "detail": "Daylist and AI DJ are early signals but not product strategy. Spotify should make natural language music discovery the default interface — moving from browse/search to conversational. This is a 3-year moat-building move that compounds with every listening hour."},
        ],
        "risks": [
            {"title": "Label Re-negotiation Could Compress Margins Further", "detail": "Three major labels control 65%+ of streaming content. Any re-negotiation post-2025 could raise royalty rates and erode the path to 30% gross margin. Mitigation: accelerate owned content revenue to reduce dependency."},
            {"title": "Apple Has Structural Distribution Advantage", "detail": "Apple Music ships on every iPhone and HomePod with Siri integration. Spotify pays 30% App Store tax on iOS upgrades. If Apple tightens integration further, Spotify loses the conversion funnel. Mitigation: deepen Android/web and car integration."},
            {"title": "Podcast Investment ROI Remains Unproven", "detail": "Spotify spent $1B+ on podcast acquisitions (Anchor, Gimlet, The Ringer). Most exclusive deals have underdelivered on subscriber conversion. Risk of continued spend without clear attribution model. Mitigation: shift from exclusives to platform tools (RSS hosting, monetization)."},
        ],
        "validate_first": [
            {"title": "Does social listening drive subscription conversion?", "detail": "Hypothesis: users who listen with a friend are 2x more likely to convert from free to premium within 30 days. Test: enable collaborative listening for 5% of free users, measure 30-day conversion lift vs control."},
            {"title": "Will AI mood search replace manual discovery?", "detail": "Hypothesis: users who interact with conversational search (vs browse) have 15% higher session length. Test: A/B test a natural language search bar against current search UI, measure session depth and next-day retention."},
            {"title": "Does concert integration increase premium stickiness?", "detail": "Hypothesis: users who book a concert via Spotify integration have 40% lower 90-day churn. Test: pilot with 3 live event partners in 2 cities, track churn delta vs matched control group."},
        ],
        "success_metrics": [
            {"metric": "Free-to-Premium Conversion Rate", "target": "30% (from 27%)", "timeframe": "12 months"},
            {"metric": "Gross Margin", "target": "30%+ (from 26.7%)", "timeframe": "18 months"},
            {"metric": "AI Feature MAU Engagement", "target": "40% of MAU use AI features monthly", "timeframe": "9 months"},
        ],
        "experiments": [
            {"title": "Collaborative Listening Conversion Lift", "hypothesis": "If we launch real-time listening rooms for free users, 30-day premium conversion will increase by 15% because shared experiences create social pressure to access premium features together."},
            {"title": "Mood Search vs Browse A/B", "hypothesis": "If we replace the browse tab with a natural language mood search for 10% of users, average session length will increase by 12% because users find relevant content faster with intent-driven discovery."},
            {"title": "Pre-commute Smart Download", "hypothesis": "If we auto-download 2 hours of predicted content every morning at 7am for users with commute patterns, offline-mode satisfaction scores will increase by 25% because the #1 offline complaint is stale downloads."},
        ]
    },
    "memo": {
        "problem": "Spotify has 600M users but is losing the engagement battle to short-form video (TikTok, Reels) and the margin battle to label royalties. Discovery is algorithmic but not conversational, and the social layer that would make music a shared experience doesn't exist on the platform.",
        "user": "The core user is a 22–32 year old who uses Spotify as background infrastructure for their day. They don't browse — they want the app to know what they need before they ask. They share playlists via screenshot because Spotify has no native social surface.",
        "solution": "Invest in three compounding bets: (1) conversational AI discovery as the primary search interface, (2) real-time social listening rooms to build a social graph, and (3) expand owned-content margins via artist tools and audiobooks rather than exclusive podcast deals.",
        "metrics": "Success is measured by Free-to-Premium conversion reaching 30%, gross margin crossing 30% within 18 months, and 40% of MAU engaging with at least one AI feature monthly. Secondary: social feature adoption rate and NPS lift among 18–25 cohort.",
        "decision": "Prioritize the AI Discovery and Social Listening features in H1 2025. Pause exclusive podcast acquisition spend. Redirect budget to platform tooling for artists and podcasters. This positions Spotify as the infrastructure layer for audio — not a content company competing on catalog."
    },
    "app_store_data": {
        "rating": 4.8,
        "rating_count": "14.2M",
        "price": "Free",
        "genre": "Music",
        "developer": "Spotify AB",
        "real_data": True
    }
}
