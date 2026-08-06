#!/usr/bin/env python3
"""
KDP Listing Metadata Generator — Bright Mindful Pages
Generates Amazon KDP listing metadata: title, subtitle, description, keywords, categories, price.

Rules (from KDP guidelines):
- Subtitle: ONE clause value prop, no keyword stuffing
- Max 7 keywords, each under 50 chars, no duplication of title words
- Description: 4000 chars max, plain text, no HTML allowed in certain fields
"""

import sys
import json
import argparse

# ── Keyword banks by niche ────────────────────────────────────────────────────
NICHE_KEYWORDS = {
    "adhd": [
        "adhd planner for adults",
        "adhd daily organizer",
        "executive function planner",
        "focus planner for adhd",
        "adhd productivity journal",
        "time management planner adhd",
        "daily planner with time blocks",
    ],
    "sobriety": [
        "sobriety journal",
        "addiction recovery journal",
        "alcohol free daily tracker",
        "sober life journal",
        "recovery workbook for adults",
        "sobriety tracker 90 days",
        "one day at a time journal",
    ],
    "anxiety": [
        "anxiety journal for adults",
        "anxiety and depression journal",
        "mental health planner",
        "worry journal",
        "calm daily planner",
        "mindfulness journal anxiety",
        "self care planner for anxiety",
    ],
    "mindfulness": [
        "mindfulness journal",
        "daily mindfulness planner",
        "gratitude and mindfulness journal",
        "mindful living planner",
        "meditation and mindfulness journal",
        "mindfulness practice journal",
        "present moment journal",
    ],
    "habit": [
        "habit tracker journal",
        "habit building planner",
        "daily habit tracker",
        "routine planner for adults",
        "goal and habit tracker",
        "daily routine planner",
        "habit journal for adults",
    ],
    "gratitude": [
        "gratitude journal",
        "daily gratitude journal",
        "gratitude and affirmation journal",
        "positivity journal",
        "gratitude practice journal",
        "thankfulness journal",
        "guided gratitude journal",
    ],
    "productivity": [
        "productivity planner",
        "daily planner for productivity",
        "time blocking planner",
        "work planner for productivity",
        "daily planner with priorities",
        "goal setting planner",
        "weekly planner for adults",
    ],
    "chronic_pain": [
        "chronic pain journal",
        "pain management journal",
        "fibromyalgia journal",
        "chronic illness planner",
        "pain tracker journal",
        "health journal for chronic pain",
        "medical tracker journal",
    ],
}

DEFAULT_KEYWORDS = [
    "daily planner for adults",
    "structured daily planner",
    "morning routine planner",
    "daily journal for adults",
    "self improvement planner",
    "daily self care journal",
    "personal development planner",
]

# ── KDP category pairs ─────────────────────────────────────────────────────────
NICHE_CATEGORIES = {
    "adhd": [
        "Books > Self-Help > Attention Deficit & Attention Deficit Hyperactivity Disorder",
        "Books > Health, Fitness & Dieting > Mental Health > Attention Deficit Disorder (ADD & ADHD)",
    ],
    "sobriety": [
        "Books > Self-Help > Substance Abuse & Addictions > Alcoholism",
        "Books > Health, Fitness & Dieting > Diseases & Physical Ailments > Substance Abuse",
    ],
    "anxiety": [
        "Books > Self-Help > Anxieties & Phobias",
        "Books > Health, Fitness & Dieting > Mental Health > Anxiety Disorders",
    ],
    "mindfulness": [
        "Books > Self-Help > Stress Management",
        "Books > Religion & Spirituality > Mindfulness & Meditation",
    ],
    "gratitude": [
        "Books > Self-Help > Personal Transformation",
        "Books > Self-Help > Happiness",
    ],
    "productivity": [
        "Books > Business & Money > Skills > Time Management",
        "Books > Self-Help > Time Management",
    ],
    "chronic_pain": [
        "Books > Health, Fitness & Dieting > Diseases & Physical Ailments > Pain Management",
        "Books > Self-Help > Motivational",
    ],
}

DEFAULT_CATEGORIES = [
    "Books > Self-Help > Personal Transformation",
    "Books > Health, Fitness & Dieting > Diets & Weight Loss > Other Diets",
]

# ── Price points ──────────────────────────────────────────────────────────────
PRICE_MAP = {
    "full_color": {"60": "8.99", "90": "10.99", "default": "9.99"},
    "black_white": {"60": "6.99", "90": "8.99", "default": "7.99"},
}


def get_keywords(niche, title):
    """Get 7 KDP keywords for a given niche, avoiding title word repetition."""
    niche_lower = niche.lower()
    candidates = None
    for key in NICHE_KEYWORDS:
        if key in niche_lower:
            candidates = NICHE_KEYWORDS[key]
            break
    if not candidates:
        candidates = DEFAULT_KEYWORDS

    title_words = set(title.lower().split())
    filtered = []
    for kw in candidates:
        kw_words = set(kw.lower().split())
        # Allow keyword if < 3 title words overlap (to avoid obvious stuffing)
        overlap = len(title_words & kw_words)
        if overlap < 3:
            filtered.append(kw)

    return filtered[:7] if len(filtered) >= 7 else candidates[:7]


def get_categories(niche):
    niche_lower = niche.lower()
    for key in NICHE_CATEGORIES:
        if key in niche_lower:
            return NICHE_CATEGORIES[key]
    return DEFAULT_CATEGORIES


def build_subtitle(niche, day_count, target_audience=None):
    """Build a single-clause subtitle — value prop only, no keyword stuffing."""
    audience = target_audience or "Adults"
    niche_lower = niche.lower()

    if "adhd" in niche_lower:
        return f"A {day_count}-Day Structured Organizer with Time Blocks and Daily Focus Pages"
    elif "sobri" in niche_lower or "recovery" in niche_lower:
        return f"A {day_count}-Day Daily Reflection Journal for Your Recovery Journey"
    elif "anxiet" in niche_lower:
        return f"A {day_count}-Day Guided Journal for Managing Anxiety and Building Calm"
    elif "mindful" in niche_lower:
        return f"A {day_count}-Day Mindfulness Practice Planner for Daily Awareness"
    elif "gratitud" in niche_lower:
        return f"A {day_count}-Day Guided Gratitude Practice for a More Positive Life"
    elif "habit" in niche_lower:
        return f"A {day_count}-Day Habit Building Planner with Daily Tracker Pages"
    elif "chronic" in niche_lower or "pain" in niche_lower:
        return f"A {day_count}-Day Pain and Wellness Tracking Journal for Clarity and Relief"
    else:
        return f"A {day_count}-Day Structured Daily Planner for Intentional Living"


def build_description(title, subtitle, niche, day_count, author_name, include_habit, include_weekly):
    """Build a KDP-compliant book description (4000 char limit)."""
    niche_lower = niche.lower()

    features = []
    features.append(f"  - {day_count} beautifully designed daily pages")
    features.append("  - Morning intentions and evening reflection prompts")
    features.append("  - Time-blocked schedule with hourly slots")
    features.append("  - Top 3 priorities section on every page")
    if include_habit:
        features.append("  - Weekly habit tracker to build consistency")
    if include_weekly:
        features.append("  - Weekly review pages to celebrate progress")
    features.append("  - Motivational close for every week")
    features.append("  - Clean, distraction-free layout — no clutter")

    desc = f"""{title}: {subtitle}

Are you ready to stop planning and start DOING?

Whether you're building a new routine, overcoming challenges, or simply trying to make the most of each day — this {day_count}-day planner gives you the structure you need without the overwhelm.

WHAT'S INSIDE:
{chr(10).join(features)}

WHY THIS PLANNER WORKS:
Unlike generic planners that sit on your shelf, this one is built for real life. Each page takes just minutes to fill out, yet creates the kind of clarity that changes how you approach your day. After {day_count} days, you won't just have a completed journal — you'll have proof of what you're capable of.

PERFECT FOR:
  - Anyone ready to build better daily habits
  - People who love structure but hate complicated systems
  - A thoughtful gift for someone who deserves to invest in themselves

DETAILS:
  - {day_count} daily pages
  - Sturdy paperback cover
  - Published by {author_name}

Start your {day_count}-day journey today. Scroll up and click Add to Cart."""

    # Trim to 4000 chars
    if len(desc) > 4000:
        desc = desc[:3997] + "..."

    return desc


def generate_listing(args):
    niche = args.niche or "productivity"
    title = args.title or "My Daily Planner"
    day_count = int(args.day_count or 60)
    author = args.author_name or "Bright Mindful Pages"
    target_audience = args.target_audience or "Adults"
    interior_type = args.interior_type or "full_color"
    include_habit = not args.no_habit_tracker
    include_weekly = not args.no_weekly_review

    subtitle = build_subtitle(niche, day_count, target_audience)
    keywords = get_keywords(niche, title)
    categories = get_categories(niche)
    description = build_description(title, subtitle, niche, day_count, author, include_habit, include_weekly)

    dc_key = str(day_count) if str(day_count) in PRICE_MAP[interior_type] else "default"
    suggested_price = PRICE_MAP[interior_type][dc_key]

    warnings = []
    if len(subtitle.split(",")) > 1 or "," in subtitle:
        warnings.append("Subtitle contains a comma — check it reads as a single clause.")
    if len(subtitle) > 200:
        warnings.append("Subtitle may be too long for KDP — aim for under 200 characters.")
    # Check for keyword stuffing in subtitle
    sub_words = subtitle.lower().split()
    kw_words = " ".join(keywords).lower().split()
    overlap = set(sub_words) & set(kw_words)
    if len(overlap) > 6:
        warnings.append("Subtitle shares many words with keywords — risk of keyword stuffing flag.")

    return {
        "title": title,
        "subtitle": subtitle,
        "description": description,
        "keywords": keywords,
        "categories": categories,
        "suggestedPrice": suggested_price,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate KDP listing metadata")
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", default="My Daily Planner")
    parser.add_argument("--niche", default="productivity")
    parser.add_argument("--author-name", default="Bright Mindful Pages")
    parser.add_argument("--target-audience", default="Adults")
    parser.add_argument("--day-count", type=int, default=60)
    parser.add_argument("--interior-type", default="full_color")
    parser.add_argument("--no-habit-tracker", action="store_true")
    parser.add_argument("--no-weekly-review", action="store_true")
    args = parser.parse_args()

    result = generate_listing(args)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
