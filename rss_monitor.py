import feedparser
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse

def fetch_rss_feeds():
    """Fetch content from RSS feeds relevant to Old Oak/Park Royal"""

    # RSS feeds to monitor
    rss_feeds = [
        {
            "url": "https://www.ealing.gov.uk/news/rss",
            "name": "Ealing Council",
            "category": "planning_policy"
        },
        {
            "url": "https://www.ealingtimes.co.uk/news/rss/",
            "name": "Ealing Times",
            "category": "development_news"
        },
        {
            "url": "https://www.getwestlondon.co.uk/news/?service=rss",
            "name": "Get West London",
            "category": "development_news"
        },
        {
            "url": "https://www.hammersmithandfulham.gov.uk/news/rss",
            "name": "Hammersmith & Fulham Council",
            "category": "planning_policy"
        },
        # HS2 and transport feeds (may not exist, will handle gracefully)
        {
            "url": "https://www.hs2.org.uk/feeds/news/",
            "name": "HS2 Official",
            "category": "development_news"
        },
        {
            "url": "https://www.networkrail.co.uk/feed/",
            "name": "Network Rail",
            "category": "development_news"
        }
    ]

    all_items = []

    print("📡 Fetching RSS feeds...")

    for feed_config in rss_feeds:
        feed_url = feed_config["url"]
        feed_name = feed_config["name"]
        category = feed_config["category"]

        try:
            print(f"   Checking {feed_name}...")
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                print(f"   ⚠️  {feed_name}: Feed error or doesn't exist")
                continue

            relevant_items = []

            # Check each entry for Old Oak/Park Royal relevance
            for entry in feed.entries[:20]:  # Check last 20 entries
                title = entry.get('title', '').lower()
                summary = entry.get('summary', entry.get('description', '')).lower()
                content = title + ' ' + summary

                # Check if relevant to Old Oak/Park Royal area
                keywords = [
                    'old oak', 'oldoak', 'park royal', 'parkroyal',
                    'opdc', 'hs2', 'nw10', 'w3 ', 'w12', 'w10'
                ]

                if any(keyword in content for keyword in keywords):
                    # Check if recent (last 30 days)
                    published = entry.get('published_parsed', entry.get('updated_parsed'))
                    if published:
                        pub_date = datetime(*published[:6])
                        days_old = (datetime.now() - pub_date).days

                        if days_old <= 30:  # Only include items from last month
                            relevant_items.append({
                                "title": entry.get('title', 'No title'),
                                "url": entry.get('link', ''),
                                "source": feed_name,
                                "date": pub_date.strftime('%Y-%m-%d'),
                                "summary": entry.get('summary', entry.get('description', ''))[:300],
                                "category": category,
                                "days_old": days_old
                            })

            if relevant_items:
                print(f"   ✓ {feed_name}: Found {len(relevant_items)} relevant items")
                all_items.extend(relevant_items)
            else:
                print(f"   ○ {feed_name}: No relevant items")

        except Exception as e:
            print(f"   ✗ {feed_name}: Error - {str(e)[:50]}")

        # Small delay between feeds
        time.sleep(1)

    print(f"\n📊 RSS Summary: Found {len(all_items)} relevant items total\n")

    return all_items


def categorize_rss_items(items):
    """Organize RSS items by category and score them"""

    categorized = {
        "development_news": [],
        "business_spotlights": [],
        "community_stories": [],
        "planning_policy": []
    }

    for item in items:
        title_lower = item['title'].lower()
        summary_lower = item['summary'].lower()
        content = title_lower + ' ' + summary_lower

        # Auto-categorize based on keywords if needed
        category = item.get('category', 'development_news')

        # Recategorize business items
        business_keywords = ['shop', 'business', 'restaurant', 'cafe', 'opening', 'retail', 'store']
        if any(kw in content for kw in business_keywords):
            category = 'business_spotlights'

        # Recategorize community items
        community_keywords = ['community', 'residents', 'event', 'forum', 'group', 'meeting']
        if any(kw in content for kw in community_keywords):
            category = 'community_stories'

        # Recategorize planning items
        planning_keywords = ['planning', 'application', 'consultation', 'proposal', 'development']
        if any(kw in content for kw in planning_keywords):
            category = 'planning_policy'

        # Score based on relevance and freshness
        score = 5  # Base score

        # Boost for very recent items
        if item['days_old'] <= 7:
            score += 2
        elif item['days_old'] <= 14:
            score += 1

        # Boost for specific mentions
        if 'old oak common' in content:
            score += 2
        if 'park royal' in content:
            score += 2
        if 'hs2' in content and 'old oak' in content:
            score += 1

        # Boost for business-specific terms
        if category == 'business_spotlights':
            if any(word in content for word in ['opening', 'new', 'launch']):
                score += 1

        item['score'] = min(score, 10)  # Cap at 10
        item['relevance'] = f"Found via {item['source']} RSS feed, {item['days_old']} days old"

        categorized[category].append(item)

    # Sort each category by score
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x['score'], reverse=True)

    return categorized


def format_rss_for_curation(rss_items):
    """Format RSS items for Claude curation"""

    formatted = []

    for item in rss_items:
        formatted.append({
            "query": f"RSS: {item['source']}",
            "category": item['category'],
            "focus": "RSS feed monitoring",
            "results": {
                "content": f"Title: {item['title']}\nDate: {item['date']}\nSummary: {item['summary']}\nURL: {item['url']}",
                "citations": [item['url']],
                "source": "rss"
            },
            "result_count": 1
        })

    return formatted


if __name__ == "__main__":
    # Test the RSS feed fetcher
    print("="*60)
    print("RSS FEED MONITOR TEST")
    print("="*60 + "\n")

    items = fetch_rss_feeds()

    if items:
        categorized = categorize_rss_items(items)

        print("\n" + "="*60)
        print("CATEGORIZED RESULTS")
        print("="*60 + "\n")

        for category, items_list in categorized.items():
            if items_list:
                print(f"\n{category.upper().replace('_', ' ')} ({len(items_list)} items):")
                print("-" * 60)
                for item in items_list[:3]:  # Show top 3
                    print(f"  [{item['score']}/10] {item['title']}")
                    print(f"            {item['source']} - {item['date']}")
                    print(f"            {item['url'][:70]}...")
                    print()
    else:
        print("No relevant RSS items found.")
