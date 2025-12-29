import anthropic
import json
import os
import time
from datetime import datetime
import requests

def discover_content():
    """Search for Old Oak Common content using Perplexity + Claude curation"""

    anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")

    if not perplexity_api_key:
        print("⚠️  PERPLEXITY_API_KEY not found, using Claude web search")
        use_perplexity = False
    else:
        # Temporarily disable Perplexity due to model name issues
        print("⚠️  Perplexity temporarily disabled (model name issues)")
        print("    Using Claude web search instead")
        use_perplexity = False
        # TODO: Re-enable once correct model name is confirmed
        # use_perplexity = True

    # Focused queries for Old Oak Town news
    search_queries = [
        {
            "query": "Old Oak Common HS2 station construction news updates 2025",
            "category": "development_news",
            "focus": "HS2 station progress, construction milestones, delays, opening dates"
        },
        {
            "query": "Park Royal OPDC regeneration development London 2025",
            "category": "development_news",
            "focus": "OPDC projects, Park Royal redevelopment, housing developments"
        },
        {
            "query": "Old Oak Common local business openings new shops restaurants",
            "category": "business_spotlights",
            "focus": "New businesses, closures, local business news"
        },
        {
            "query": "Old Oak Common OPDC planning applications consultations",
            "category": "planning_policy",
            "focus": "Planning applications, public consultations, policy changes"
        }
    ]

    all_search_results = []

    print(f"🔍 Starting content discovery for Old Oak Town...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Execute searches
    for i, search_item in enumerate(search_queries):
        query = search_item["query"]
        print(f"📡 Search {i+1}/{len(search_queries)}: {query[:60]}...")

        try:
            if use_perplexity:
                try:
                    search_results = search_with_perplexity(perplexity_api_key, query, search_item["focus"])
                    search_source = "Perplexity"
                except Exception as perplexity_error:
                    # Fallback to Claude if Perplexity fails
                    print(f"   ⚠️  Perplexity failed: {str(perplexity_error)[:100]}")
                    print(f"   🔄 Falling back to Claude web search...")
                    search_results = search_with_claude(anthropic_client, query, search_item["focus"])
                    search_source = "Claude (fallback)"
            else:
                search_results = search_with_claude(anthropic_client, query, search_item["focus"])
                search_source = "Claude"

            all_search_results.append({
                "query": query,
                "category": search_item["category"],
                "focus": search_item["focus"],
                "results": search_results,
                "result_count": len(search_results) if isinstance(search_results, list) else 1
            })

            print(f"   ✓ Found content (using {search_source})")

        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
            all_search_results.append({
                "query": query,
                "category": search_item["category"],
                "focus": search_item["focus"],
                "results": [],
                "result_count": 0,
                "error": str(e)
            })

        # Rate limit protection - Perplexity free tier: 20 requests/min
        if i < len(search_queries) - 1:
            wait_time = 15 if use_perplexity else 20
            print(f"   ⏳ Waiting {wait_time}s (rate limit protection)...\n")
            time.sleep(wait_time)

    print(f"✅ Search complete!\n")

    # Wait a bit to avoid rate limits
    print("⏳ Waiting 10s before curation (rate limit protection)...")
    time.sleep(10)

    # Curate with Claude
    print("🎯 Curating content with Claude AI...")
    curated = curate_with_claude(anthropic_client, all_search_results)

    # Save results
    save_results(curated, all_search_results)

    return curated


def search_with_perplexity(api_key, query, focus):
    """Search using Perplexity API - returns structured results"""

    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-small",  # Perplexity online search model (updated name)
        "messages": [
            {
                "role": "system",
                "content": "You are a local news research assistant. Find recent, credible news articles and provide structured information."
            },
            {
                "role": "user",
                "content": f"""Search for: {query}

Focus on: {focus}

Find the most recent news articles (last 7-14 days preferred). For each relevant article provide:
- Article headline/title
- Source publication
- URL/link
- Publication date (if available)
- 2-3 sentence summary
- Why it's relevant to Old Oak Common/Park Royal residents

Format as a clear list. Prioritize local London news sources and official announcements."""
            }
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
        "return_citations": True,
        "return_related_questions": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Extract the response and citations
        content = data['choices'][0]['message']['content']
        citations = data.get('citations', [])

        return {
            "content": content,
            "citations": citations,
            "source": "perplexity"
        }
    except requests.exceptions.HTTPError as e:
        # Provide detailed error message for HTTP errors
        error_detail = ""
        try:
            error_data = response.json()
            error_detail = f": {error_data.get('error', {}).get('message', str(e))}"
        except:
            error_detail = f": {str(e)}"
        raise Exception(f"Perplexity API error{error_detail}")


def search_with_claude(client, query, focus):
    """Fallback: Search using Claude's web search tool"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Search for: {query}

Focus on: {focus}

Find recent news articles and provide:
- Title
- Source
- URL
- Date
- Brief summary
- Local relevance"""
        }]
    )

    # Extract text content
    content = ""
    for block in response.content:
        if block.type == "text":
            content += block.text

    return {
        "content": content,
        "citations": [],
        "source": "claude"
    }


def curate_with_claude(client, all_search_results):
    """Use Claude to analyze and curate findings into structured content"""

    # Process in batches to manage token limits
    batch_size = 2
    all_curated_items = []

    for i in range(0, len(all_search_results), batch_size):
        batch = all_search_results[i:i+batch_size]

        print(f"   Curating batch {i//batch_size + 1}/{(len(all_search_results) + batch_size - 1)//batch_size}...")

        # Build context from search results
        search_context = []
        for result in batch:
            context = f"""
QUERY: {result['query']}
CATEGORY: {result['category']}
FOCUS: {result['focus']}

FINDINGS:
{result['results'].get('content', 'No results') if isinstance(result['results'], dict) else str(result['results'])}

CITATIONS: {len(result['results'].get('citations', [])) if isinstance(result['results'], dict) else 0} sources
---
"""
            search_context.append(context)

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""You are curating content for Old Oak Town, a hyperlocal news platform covering Old Oak Common, Park Royal, and the HS2 development area in West London.

Review these search results and extract newsworthy stories:

{"".join(search_context)}

For each distinct news story found, extract:
- title: Clear, engaging headline
- url: Source URL (use actual URL from citations/results)
- source: Publication name (e.g., "Ealing Times", "Construction News", "OPDC Official")
- date: Publication date if mentioned (format: YYYY-MM-DD or "Recent")
- summary: 2-3 sentences describing what happened
- category: ONE of: development_news, business_spotlights, community_stories, planning_policy
- relevance: One sentence explaining why this matters to Old Oak Town readers
- score: Quality/importance score 1-10 based on:
  * Local impact (high = directly affects residents)
  * Timeliness (high = very recent)
  * Credibility (high = official sources, known publications)
  * Uniqueness (high = exclusive or first reporting)

Return ONLY valid JSON (no markdown, no extra text):
{{
  "items": [
    {{
      "title": "string",
      "url": "string",
      "source": "string",
      "date": "string",
      "summary": "string",
      "category": "string",
      "relevance": "string",
      "score": number
    }}
  ]
}}

Only include stories that are genuinely newsworthy and relevant to Old Oak Common/Park Royal area. Minimum score of 5 to include."""
                }]
            )

            content_text = response.content[0].text

            # Parse JSON from response
            try:
                # Clean up any markdown code blocks
                content_text = content_text.replace('```json', '').replace('```', '')
                start = content_text.find('{')
                end = content_text.rfind('}') + 1

                if start >= 0 and end > start:
                    json_content = content_text[start:end]
                    batch_data = json.loads(json_content)
                    items = batch_data.get('items', [])
                    all_curated_items.extend(items)
                    print(f"      ✓ Extracted {len(items)} stories")
                else:
                    print(f"      ⚠️  No valid JSON found in response")

            except json.JSONDecodeError as e:
                print(f"      ✗ JSON parse error: {str(e)}")

        except Exception as e:
            print(f"      ✗ Curation error: {str(e)}")

        # Brief pause between batches
        if i + batch_size < len(all_search_results):
            time.sleep(3)

    # Organize by category
    categories = {
        "development_news": [],
        "business_spotlights": [],
        "community_stories": [],
        "planning_policy": []
    }

    for item in all_curated_items:
        category = item.get('category', 'community_stories')
        if category in categories:
            categories[category].append(item)

    # Sort each category by score (highest first)
    for category in categories:
        categories[category].sort(key=lambda x: x.get('score', 0), reverse=True)

    # Generate summary
    total_items = len(all_curated_items)
    active_categories = sum(1 for items in categories.values() if items)

    week_summary = f"This week's content discovery found {total_items} newsworthy stories across {active_categories} categories. "

    if total_items > 0:
        avg_score = sum(item.get('score', 0) for item in all_curated_items) / total_items
        week_summary += f"Average quality score: {avg_score:.1f}/10. "

    # Top 3 stories overall
    top_stories = sorted(all_curated_items, key=lambda x: x.get('score', 0), reverse=True)[:3]

    print(f"\n✨ Curation complete: {total_items} stories curated")

    return {
        "categories": categories,
        "week_summary": week_summary,
        "top_stories": [s.get('title', '') for s in top_stories],
        "top_stories_full": top_stories,
        "total_items": total_items,
        "stats": {
            "total_items": total_items,
            "by_category": {cat: len(items) for cat, items in categories.items()},
            "average_score": sum(item.get('score', 0) for item in all_curated_items) / total_items if total_items > 0 else 0
        }
    }


def save_results(curated_content, raw_search_results):
    """Save results as JSON and HTML"""

    timestamp = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("reviews", exist_ok=True)

    # Save comprehensive JSON
    json_filename = f"reviews/review_{timestamp}.json"

    with open(json_filename, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "date": timestamp,
            "curated_content": curated_content,
            "search_summary": [
                {
                    "query": r['query'],
                    "category": r.get('category', 'unknown'),
                    "source": r['results'].get('source', 'unknown') if isinstance(r['results'], dict) else 'unknown',
                    "citations_count": len(r['results'].get('citations', [])) if isinstance(r['results'], dict) else 0
                } for r in raw_search_results
            ],
            "statistics": curated_content.get('stats', {})
        }, f, indent=2)

    print(f"\n💾 Saved: {json_filename}")

    # Create HTML review
    create_html_review(curated_content, timestamp)


def create_html_review(content, timestamp):
    """Create beautiful HTML review page"""

    stats = content.get('stats', {})
    total_items = stats.get('total_items', 0)
    avg_score = stats.get('average_score', 0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Old Oak Town Content Review - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #F5F5DC 0%, #E8E8D0 100%);
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2D5016 0%, #3a6b1c 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 32px; margin-bottom: 8px; }}
        .header .date {{ font-size: 16px; opacity: 0.9; }}

        .stats-bar {{
            display: flex;
            justify-content: space-around;
            background: #fff8e7;
            padding: 25px;
            border-bottom: 3px solid #2D5016;
            flex-wrap: wrap;
        }}
        .stat {{
            text-align: center;
            padding: 10px 20px;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #2D5016;
            display: block;
        }}
        .stat-label {{
            font-size: 13px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .summary {{
            background: #fffef9;
            padding: 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .summary h2 {{
            color: #2D5016;
            margin-bottom: 15px;
            font-size: 22px;
        }}

        .top-stories {{
            background: linear-gradient(135deg, #fff8e7 0%, #fffef9 100%);
            padding: 30px;
            margin: 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .top-stories h2 {{
            color: #2D5016;
            margin-bottom: 20px;
            font-size: 22px;
        }}
        .top-story {{
            background: white;
            border-left: 5px solid #FFD700;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .top-story-title {{
            font-size: 20px;
            font-weight: 600;
            color: #2D5016;
            margin-bottom: 10px;
        }}
        .top-story-meta {{
            font-size: 13px;
            color: #666;
            margin-bottom: 10px;
        }}
        .top-story-summary {{
            color: #444;
            line-height: 1.6;
        }}

        .category {{
            padding: 30px;
            border-bottom: 1px solid #e8e8e8;
        }}
        .category:last-child {{ border-bottom: none; }}
        .category-header {{
            display: flex;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .category-header h2 {{
            color: #8B4513;
            font-size: 24px;
            margin: 0;
            flex: 1;
        }}
        .category-count {{
            background: #2D5016;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
        }}

        .item {{
            background: #fafafa;
            border-left: 4px solid #2D5016;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }}
        .item:hover {{
            background: #f0f0f0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateX(4px);
        }}

        .item-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
            gap: 15px;
        }}
        .item-title {{
            font-size: 20px;
            font-weight: 600;
            color: #2D5016;
            flex: 1;
            line-height: 1.3;
        }}

        .score {{
            background: #2D5016;
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            white-space: nowrap;
            min-width: 60px;
            text-align: center;
        }}
        .score.high {{ background: #2D5016; }}
        .score.medium {{ background: #8B4513; }}
        .score.low {{ background: #999; }}

        .item-meta {{
            display: flex;
            gap: 20px;
            font-size: 13px;
            color: #666;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }}
        .item-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .item-summary {{
            color: #333;
            margin-bottom: 15px;
            line-height: 1.6;
        }}

        .item-relevance {{
            background: #fff8e7;
            border-left: 3px solid #FFD700;
            padding: 12px 15px;
            border-radius: 4px;
            font-size: 14px;
            color: #555;
            margin-bottom: 12px;
            font-style: italic;
        }}

        .item-link {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: #2D5016;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            padding: 8px 16px;
            background: #f0f0f0;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        .item-link:hover {{
            background: #2D5016;
            color: white;
        }}

        .empty-category {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}

        .footer {{
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Old Oak Town Content Review</h1>
            <div class="date">Week of {timestamp}</div>
        </div>

        <div class="stats-bar">
            <div class="stat">
                <span class="stat-number">{total_items}</span>
                <span class="stat-label">Stories Found</span>
            </div>
            <div class="stat">
                <span class="stat-number">{avg_score:.1f}</span>
                <span class="stat-label">Avg Quality Score</span>
            </div>
            <div class="stat">
                <span class="stat-number">{sum(1 for c in content.get('categories', {}).values() if c)}</span>
                <span class="stat-label">Active Categories</span>
            </div>
        </div>

        <div class="summary">
            <h2>📋 Week Summary</h2>
            <p>{content.get('week_summary', 'No summary available')}</p>
        </div>
"""

    # Top Stories section
    top_stories_full = content.get('top_stories_full', [])
    if top_stories_full:
        html += """
        <div class="top-stories">
            <h2>⭐ Top Stories This Week</h2>
"""
        for story in top_stories_full:
            score = story.get('score', 0)
            html += f"""
            <div class="top-story">
                <div class="top-story-title">{story.get('title', 'No title')}</div>
                <div class="top-story-meta">
                    📰 {story.get('source', 'Unknown')} • 📅 {story.get('date', 'Date unknown')} • ⭐ Score: {score}/10
                </div>
                <div class="top-story-summary">{story.get('summary', '')}</div>
            </div>
"""
        html += """
        </div>
"""

    # Categories
    categories = content.get('categories', {})
    category_info = {
        'development_news': ('🏗️ Development News', 'HS2, OPDC, construction updates'),
        'business_spotlights': ('🏪 Business Spotlights', 'Local businesses, openings, closures'),
        'community_stories': ('👥 Community Stories', 'Events, residents, initiatives'),
        'planning_policy': ('📋 Planning & Policy', 'Applications, consultations, decisions')
    }

    for key, (title, description) in category_info.items():
        items = categories.get(key, [])

        html += f"""
        <div class="category">
            <div class="category-header">
                <h2>{title}</h2>
                <span class="category-count">{len(items)} items</span>
            </div>
"""

        if items:
            for item in items:
                score = item.get('score', 0)
                score_class = 'high' if score >= 7 else 'medium' if score >= 5 else 'low'

                html += f"""
            <div class="item">
                <div class="item-header">
                    <div class="item-title">{item.get('title', 'No title')}</div>
                    <span class="score {score_class}">{score}/10</span>
                </div>
                <div class="item-meta">
                    <span>📰 {item.get('source', 'Unknown source')}</span>
                    <span>📅 {item.get('date', 'Date unknown')}</span>
                </div>
                <div class="item-summary">{item.get('summary', 'No summary available')}</div>
                <div class="item-relevance">
                    <strong>Why it matters:</strong> {item.get('relevance', 'Local relevance to be determined')}
                </div>
                <a href="{item.get('url', '#')}" target="_blank" class="item-link">
                    Read full article →
                </a>
            </div>
"""
        else:
            html += """
            <div class="empty-category">No stories found in this category this week</div>
"""

        html += """
        </div>
"""

    html += f"""
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M')} • Old Oak Town Content Agent • Powered by Perplexity + Claude
        </div>
    </div>
</body>
</html>"""

    html_filename = f"reviews/review_{timestamp}.html"
    with open(html_filename, 'w') as f:
        f.write(html)

    print(f"📄 Created: {html_filename}")
    print(f"\n✨ Review complete! Open {html_filename} in your browser.\n")


if __name__ == "__main__":
    print("="*60)
    print("OLD OAK TOWN CONTENT DISCOVERY AGENT")
    print("Powered by Perplexity Search + Claude Curation")
    print("="*60 + "\n")

    results = discover_content()

    print("="*60)
    print("✅ CONTENT DISCOVERY COMPLETE!")
    print(f"📊 Total items curated: {results.get('total_items', 0)}")
    print(f"⭐ Average quality score: {results.get('stats', {}).get('average_score', 0):.1f}/10")
    print("="*60)
