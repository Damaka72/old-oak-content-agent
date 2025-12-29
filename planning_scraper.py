import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

def scrape_ealing_planning():
    """Scrape Ealing Council planning applications for Old Oak area"""

    print("📋 Checking Ealing Council planning applications...")

    # Old Oak area postcodes
    postcodes = ["W3", "W12", "NW10"]

    all_applications = []

    # Note: This is a simplified version - real implementation would need
    # to handle the actual Ealing planning portal structure
    base_url = "https://pam.ealing.gov.uk/online-applications"

    for postcode in postcodes:
        try:
            print(f"   Searching postcode {postcode}...")

            # In a real implementation, you'd construct proper search URL
            # and parse the results. This is a template:

            # Example search parameters
            search_url = f"{base_url}/search.do?action=simple&searchType=Application"

            # Would need to:
            # 1. Submit search form with postcode
            # 2. Parse results table
            # 3. Extract application details

            # Placeholder for now
            print(f"   ○ {postcode}: Would search planning portal here")

        except Exception as e:
            print(f"   ✗ {postcode}: Error - {str(e)[:50]}")

    return all_applications


def scrape_opdc_planning():
    """Scrape OPDC planning register"""

    print("📋 Checking OPDC planning register...")

    all_applications = []

    try:
        # OPDC Planning Applications page
        url = "https://opdc.london.gov.uk/planning/planning-applications"

        print(f"   Fetching {url}...")

        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find planning application links/entries
            # Note: This is a template - actual selectors depend on site structure

            # Look for common patterns
            app_links = soup.find_all('a', href=lambda x: x and 'application' in x.lower())

            print(f"   Found {len(app_links)} potential applications")

            # Extract recent applications
            for link in app_links[:10]:  # Limit to recent ones
                title = link.get_text(strip=True)

                # Check if relevant
                if any(keyword in title.lower() for keyword in ['old oak', 'park royal', 'business', 'retail']):
                    all_applications.append({
                        "title": title,
                        "url": f"https://opdc.london.gov.uk{link.get('href', '')}",
                        "source": "OPDC Planning",
                        "category": "planning_policy",
                        "date": datetime.now().strftime('%Y-%m-%d'),
                        "summary": f"Planning application: {title}",
                        "score": 7
                    })

            if all_applications:
                print(f"   ✓ Found {len(all_applications)} relevant applications")
            else:
                print(f"   ○ No relevant applications found")

        else:
            print(f"   ✗ Failed to fetch (status {response.status_code})")

    except Exception as e:
        print(f"   ✗ Error: {str(e)[:50]}")

    return all_applications


def check_business_planning_applications():
    """
    Check for business-related planning applications
    Focus on change of use applications that indicate new businesses
    """

    print("\n🏪 Checking for business-related planning applications...\n")

    business_applications = []

    # Combine results from different sources
    opdc_apps = scrape_opdc_planning()
    ealing_apps = scrape_ealing_planning()

    all_apps = opdc_apps + ealing_apps

    # Filter for business-relevant applications
    business_keywords = [
        'change of use', 'a1', 'a2', 'a3', 'a4', 'a5',  # Use classes
        'retail', 'restaurant', 'cafe', 'shop', 'bar', 'pub',
        'commercial', 'business', 'office', 'warehouse'
    ]

    for app in all_apps:
        content = (app.get('title', '') + ' ' + app.get('summary', '')).lower()

        if any(keyword in content for keyword in business_keywords):
            # Boost score for business applications
            app['score'] = min(app.get('score', 5) + 2, 10)
            app['category'] = 'business_spotlights'
            app['relevance'] = f"Planning application indicating potential business activity"
            business_applications.append(app)

    print(f"📊 Found {len(business_applications)} business-related applications\n")

    return business_applications


def format_planning_for_curation(planning_items):
    """Format planning applications for Claude curation"""

    formatted = []

    for item in planning_items:
        formatted.append({
            "query": f"Planning: {item['source']}",
            "category": item['category'],
            "focus": "Planning application monitoring",
            "results": {
                "content": f"Title: {item['title']}\nDate: {item['date']}\nSummary: {item['summary']}\nURL: {item['url']}",
                "citations": [item['url']],
                "source": "planning"
            },
            "result_count": 1
        })

    return formatted


if __name__ == "__main__":
    # Test the planning scraper
    print("="*60)
    print("PLANNING APPLICATION SCRAPER TEST")
    print("="*60 + "\n")

    apps = check_business_planning_applications()

    if apps:
        print("\nBUSINESS-RELATED APPLICATIONS:")
        print("-" * 60)
        for app in apps[:5]:  # Show top 5
            print(f"[{app['score']}/10] {app['title']}")
            print(f"           {app['source']} - {app['date']}")
            print(f"           {app['url'][:70]}...")
            print()
    else:
        print("No business-related planning applications found.")
