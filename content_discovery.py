import anthropic
import json
import os
from datetime import datetime

def discover_content():
    """Search for Old Oak Common content using Claude"""
    
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    search_queries = [
        "Old Oak Common HS2 news last 7 days",
        "Old Oak station construction update",
        "Park Royal regeneration news",
        "Old Oak Common local business news"
    ]
    
    all_results = []
    
    print("🔍 Starting content discovery...")
    
    for query in search_queries:
        print(f"Searching: {query}")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=[{
                "role": "user",
                "content": f"""Search for: {query}
                
                Find recent news articles, announcements, and updates.
                Return: title, URL, source, date, and brief summary for each result."""
            }]
        )
        
        all_results.append({
            "query": query,
            "response": str(response.content)
        })
    
    print("✅ Search complete! Now curating...")
    
    # Curate the findings
    curated = curate_results(client, all_results)
    
    # Save results
    save_results(curated)
    
    return curated

def curate_results(client, raw_results):
    """Use Claude to analyze and categorize findings - simplified version"""

    # Just summarize the first 2 queries to stay within limits
    simplified_results = raw_results[:2]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"""Curate content for Old Oak Town news platform.

Search results summary (first 2 queries only):
Query 1: {simplified_results[0]['query']}
Query 2: {simplified_results[1]['query'] if len(simplified_results) > 1 else 'N/A'}

Extract top 5 news items total. Return as JSON:
{{
  "categories": {{
    "development_news": [],
    "business_spotlights": [],
    "community_stories": []
  }},
  "week_summary": "Brief summary here",
  "top_stories": []
}}

Keep response concise."""
        }]
    )

    content_text = response.content[0].text

    # Extract JSON
    try:
        start = content_text.find('{')
        end = content_text.rfind('}') + 1
        json_content = content_text[start:end]
        return json.loads(json_content)
    except:
        return {
            "categories": {
                "development_news": [{"title": "Error parsing results", "summary": "Check logs"}]
            },
            "week_summary": "Content discovery ran but results need manual review"
        }

def save_results(curated_content):
    """Save results as JSON and HTML"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Save JSON
    json_filename = f"reviews/review_{timestamp}.json"
    os.makedirs("reviews", exist_ok=True)
    
    with open(json_filename, 'w') as f:
        json.dump({
            "date": timestamp,
            "content": curated_content
        }, f, indent=2)
    
    print(f"💾 Saved: {json_filename}")
    
    # Create HTML review page
    create_html_review(curated_content, timestamp)

def create_html_review(content, timestamp):
    """Create a beautiful HTML review page"""
    
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
        .summary {{
            padding: 25px 30px;
            background: #fff8e7;
            border-bottom: 2px solid #2D5016;
        }}
        .category {{
            padding: 25px 30px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .category h2 {{
            color: #8B4513;
            margin-bottom: 20px;
        }}
        .item {{
            background: #fafafa;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        .item-title {{
            font-size: 18px;
            font-weight: 600;
            color: #2D5016;
            margin-bottom: 10px;
        }}
        .item-summary {{
            color: #555;
            margin-bottom: 10px;
        }}
        .score {{
            background: #2D5016;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 13px;
            display: inline-block;
        }}
        a {{
            color: #2D5016;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Old Oak Town Content Review</h1>
            <p>Week of {timestamp}</p>
        </div>
        
        <div class="summary">
            <h2>Week Summary</h2>
            <p>{content.get('week_summary', 'Content summary will appear here')}</p>
        </div>
"""
    
    categories = content.get('categories', {})
    category_names = {
        'development_news': '🏗️ Development News',
        'business_spotlights': '🏪 Business Spotlights',
        'community_stories': '👥 Community Stories',
        'planning_policy': '📋 Planning & Policy'
    }
    
    for key, title in category_names.items():
        items = categories.get(key, [])
        if items:
            html += f"""
        <div class="category">
            <h2>{title}</h2>
"""
            for item in items:
                html += f"""
            <div class="item">
                <div class="item-title">{item.get('title', 'No title')}</div>
                <div class="item-summary">{item.get('summary', '')}</div>
                <p><strong>Relevance:</strong> {item.get('relevance', '')}</p>
                <p>
                    <a href="{item.get('url', '#')}" target="_blank">Read source →</a>
                    <span class="score">Score: {item.get('score', 'N/A')}/10</span>
                </p>
            </div>
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

if __name__ == "__main__":
    results = discover_content()
    print("✅ Content discovery complete!")
