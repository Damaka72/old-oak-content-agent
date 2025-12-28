import anthropic
import json
import os
import time
from datetime import datetime

def discover_content():
    """Search for Old Oak Common content using Claude - IMPROVED VERSION"""

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    # More focused queries for better results
    search_queries = [
        "Old Oak Common HS2 station news 2025",
        "Park Royal development news London",
        "Old Oak Common local business openings",
        "OPDC planning applications Old Oak"
    ]

    all_search_results = []

    print("🔍 Starting content discovery for Old Oak Town...")

    # Step 1: Execute searches with proper result extraction
    for i, query in enumerate(search_queries):
        print(f"📡 Searching ({i+1}/{len(search_queries)}): {query}")

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{
                    "role": "user",
                    "content": f"""Search for: {query}

Find the most recent and relevant news articles. Focus on:
- Local impact on Old Oak Common residents
- Development and construction updates
- Business news and openings
- Community events and initiatives

For each result, I need: title, URL, source name, publication date, and a brief description."""
                }]
            )

            # Extract the actual search results from the response
            search_findings = extract_search_results(response)

            all_search_results.append({
                "query": query,
                "findings": search_findings,
                "result_count": len(search_findings)
            })

            print(f"   ✓ Found {len(search_findings)} results")

        except Exception as e:
            print(f"   ✗ Error searching '{query}': {str(e)}")
            all_search_results.append({
                "query": query,
                "findings": [],
                "error": str(e)
            })

        # Rate limit protection
        if i < len(search_queries) - 1:
            print("   ⏳ Waiting 20s to avoid rate limits...")
            time.sleep(20)

    print(f"\n✅ Search complete! Found {sum(r['result_count'] for r in all_search_results)} total results")

    # Step 2: Curate in batches to avoid token limits
    print("🎯 Curating content...")
    curated = curate_results_smart(client, all_search_results)

    # Step 3: Save results
    save_results(curated, all_search_results)

    return curated


def extract_search_results(response):
    """Extract structured search results from Claude's response"""
    findings = []

    # Claude's response contains the text analysis of search results
    for block in response.content:
        if block.type == "text":
            # The text contains Claude's summary of findings
            # Store it for later processing
            findings.append({
                "summary": block.text,
                "type": "analysis"
            })

    return findings


def curate_results_smart(client, all_search_results):
    """Smart curation that processes all queries in batches"""

    # Process 2 queries at a time to stay under token limits
    batch_size = 2
    all_curated_items = []

    for i in range(0, len(all_search_results), batch_size):
        batch = all_search_results[i:i+batch_size]

        print(f"   Processing batch {i//batch_size + 1}...")

        # Build a concise summary of findings
        batch_summary = []
        for result in batch:
            summary_text = f"Query: {result['query']}\n"
            summary_text += f"Results found: {result['result_count']}\n"

            if result['findings']:
                # Take first finding summary (most relevant)
                for finding in result['findings'][:1]:  # Limit to first finding to save tokens
                    summary_text += f"Key finding: {finding.get('summary', 'No summary')[:500]}\n"

            batch_summary.append(summary_text)

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""You are curating content for Old Oak Town, a hyperlocal news platform covering Old Oak Common, Park Royal, and the HS2 development area.

Review these search results:

{chr(10).join(batch_summary)}

Extract the TOP 3-5 most newsworthy stories. For EACH story provide:
- title: Clear, engaging headline
- url: Source URL (use placeholder if not available)
- source: Publication name
- summary: 2-3 sentence description
- category: ONE of [development_news, business_spotlights, community_stories, planning_policy]
- relevance: Why this matters to Old Oak Town readers (1 sentence)
- score: Quality score 1-10 based on local relevance, timeliness, and impact

Return ONLY valid JSON in this exact format:
{{
  "items": [
    {{
      "title": "Exact title",
      "url": "https://...",
      "source": "Source name",
      "summary": "Brief summary",
      "category": "development_news",
      "relevance": "Why it matters",
      "score": 8
    }}
  ]
}}"""
                }]
            )

            # Parse the response
            content_text = response.content[0].text

            try:
                # Extract JSON
                start = content_text.find('{')
                end = content_text.rfind('}') + 1
                if start >= 0 and end > start:
                    json_content = content_text[start:end]
                    batch_data = json.loads(json_content)
                    all_curated_items.extend(batch_data.get('items', []))
            except json.JSONDecodeError:
                print(f"   ⚠️  Could not parse JSON from batch {i//batch_size + 1}")

        except Exception as e:
            print(f"   ✗ Error curating batch: {str(e)}")

        # Small delay between batches
        if i + batch_size < len(all_search_results):
            time.sleep(5)

    # Organize items by category
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

    # Sort each category by score
    for category in categories:
        categories[category].sort(key=lambda x: x.get('score', 0), reverse=True)

    # Generate week summary
    week_summary = f"This week's content review found {len(all_curated_items)} stories across {sum(1 for c in categories.values() if c)} categories. "
    top_stories = [item['title'] for item in sorted(all_curated_items, key=lambda x: x.get('score', 0), reverse=True)[:3]]

    return {
        "categories": categories,
        "week_summary": week_summary,
        "top_stories": top_stories,
        "total_items": len(all_curated_items)
    }


def save_results(curated_content, raw_search_results):
    """Save results as JSON and HTML"""

    timestamp = datetime.now().strftime("%Y-%m-%d")

    # Save JSON with both curated and raw data
    json_filename = f"reviews/review_{timestamp}.json"
    os.makedirs("reviews", exist_ok=True)

    with open(json_filename, 'w') as f:
        json.dump({
            "date": timestamp,
            "curated_content": curated_content,
            "raw_search_summary": [
                {
                    "query": r['query'],
                    "result_count": r['result_count']
                } for r in raw_search_results
            ],
            "total_searches": len(raw_search_results),
            "total_curated_items": curated_content.get('total_items', 0)
        }, f, indent=2)

    print(f"💾 Saved: {json_filename}")

    # Create HTML review page
    create_html_review(curated_content, timestamp)


def create_html_review(content, timestamp):
    """Create a beautiful HTML review page with actual data"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Old Oak Town Content Review - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #F5F5DC;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2D5016 0%, #3a6b1c 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .stats {{
            background: #fff8e7;
            padding: 20px 30px;
            border-bottom: 2px solid #2D5016;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }}
        .stat {{
            text-align: center;
            margin: 10px;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #2D5016;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
        }}
        .summary {{
            padding: 25px 30px;
            background: #fffef9;
            border-bottom: 1px solid #e0e0e0;
        }}
        .category {{
            padding: 25px 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .category h2 {{
            color: #8B4513;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .item {{
            background: #fafafa;
            border-left: 4px solid #2D5016;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }}
        .item:hover {{
            background: #f0f0f0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .item-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }}
        .item-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2D5016;
            flex: 1;
        }}
        .score {{
            background: #2D5016;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            white-space: nowrap;
            margin-left: 15px;
        }}
        .score.high {{
            background: #2D5016;
        }}
        .score.medium {{
            background: #8B4513;
        }}
        .score.low {{
            background: #999;
        }}
        .item-source {{
            color: #666;
            font-size: 13px;
            margin-bottom: 10px;
        }}
        .item-summary {{
            color: #333;
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .item-relevance {{
            background: #fff8e7;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
            color: #555;
            margin-bottom: 10px;
            font-style: italic;
        }}
        .item-link {{
            display: inline-block;
            color: #2D5016;
            text-decoration: none;
            font-weight: 500;
            margin-top: 5px;
        }}
        .item-link:hover {{
            text-decoration: underline;
        }}
        .empty-category {{
            color: #999;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
        .top-stories {{
            background: #fff8e7;
            padding: 20px 30px;
            margin: 20px 30px;
            border-radius: 8px;
            border: 2px solid #2D5016;
        }}
        .top-stories h3 {{
            color: #2D5016;
            margin-top: 0;
        }}
        .top-stories ul {{
            margin: 10px 0;
            padding-left: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Old Oak Town Content Review</h1>
            <p>Week of {timestamp}</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">{content.get('total_items', 0)}</div>
                <div class="stat-label">Stories Found</div>
            </div>
            <div class="stat">
                <div class="stat-number">{sum(1 for c in content.get('categories', {}).values() if c)}</div>
                <div class="stat-label">Active Categories</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(content.get('top_stories', []))}</div>
                <div class="stat-label">Top Stories</div>
            </div>
        </div>

        <div class="summary">
            <h2>📋 Week Summary</h2>
            <p>{content.get('week_summary', 'Content summary will appear here')}</p>
        </div>
"""

    # Top Stories Section
    if content.get('top_stories'):
        html += """
        <div class="top-stories">
            <h3>⭐ Top Stories This Week</h3>
            <ul>
"""
        for story in content.get('top_stories', []):
            html += f"                <li>{story}</li>\n"
        html += """
            </ul>
        </div>
"""

    # Categories
    categories = content.get('categories', {})
    category_info = {
        'development_news': ('🏗️ Development News', 'HS2, OPDC, construction updates'),
        'business_spotlights': ('🏪 Business Spotlights', 'Local businesses, openings, closures'),
        'community_stories': ('👥 Community Stories', 'Events, residents, local initiatives'),
        'planning_policy': ('📋 Planning & Policy', 'Consultations, applications, decisions')
    }

    for key, (title, description) in category_info.items():
        items = categories.get(key, [])

        html += f"""
        <div class="category">
            <h2>
                <span>{title}</span>
                <span style="font-size: 14px; color: #666; font-weight: normal;">({len(items)} items)</span>
            </h2>
"""

        if items:
            for item in items:
                score = item.get('score', 0)
                score_class = 'high' if score >= 7 else 'medium' if score >= 5 else 'low'

                html += f"""
            <div class="item">
                <div class="item-header">
                    <div class="item-title">{item.get('title', 'No title')}</div>
                    <span class="score {score_class}">Score: {score}/10</span>
                </div>
                <div class="item-source">📰 {item.get('source', 'Unknown source')}</div>
                <div class="item-summary">{item.get('summary', 'No summary available')}</div>
                <div class="item-relevance">
                    <strong>Why it matters:</strong> {item.get('relevance', 'Local relevance to be determined')}
                </div>
                <a href="{item.get('url', '#')}" target="_blank" class="item-link">Read full article →</a>
            </div>
"""
        else:
            html += """
            <div class="empty-category">No stories found in this category this week</div>
"""

        html += """
        </div>
"""

    html += """
    </div>
</body>
</html>"""

    html_filename = f"reviews/review_{timestamp}.html"
    with open(html_filename, 'w') as f:
        f.write(html)

    print(f"📄 Created: {html_filename}")
    print(f"✨ Review complete! Open {html_filename} in a browser to review content.")


if __name__ == "__main__":
    results = discover_content()
    print("\n✅ Content discovery complete!")
    print(f"📊 Total items curated: {results.get('total_items', 0)}")
