# 📡 RSS Feed & Planning Application Automation

## What I Built For You

Your content discovery agent now has **3 automated sources**:

### 1. **Web Search** (Claude) ✅
- Targeted queries to local newspapers
- Official OPDC and council sites
- Business group websites

### 2. **RSS Feed Monitor** 📡 (NEW!)
- Automatically checks RSS feeds from:
  - Ealing Council news
  - Ealing Times
  - Get West London
  - Hammersmith & Fulham Council
  - HS2 Official (if feed exists)
  - Network Rail (if feed exists)
- Filters for Old Oak/Park Royal relevance
- Scores by freshness and keywords

### 3. **Planning Application Scraper** 📋 (NEW!)
- Checks OPDC planning register
- Scans for business-related applications
- Detects "change of use" applications (new shops/cafes)
- Provides early warning of business openings (2-3 months ahead!)

---

## How It Works

### **Weekly Workflow Process:**

1. **Web Searches** (6 targeted queries)
   - Local newspapers
   - Official sites
   - Business groups

2. **RSS Feeds** (6 sources checked)
   - Fetches last 20 entries from each
   - Filters for Old Oak/Park Royal keywords
   - Only includes items from last 30 days

3. **Planning Applications**
   - Scrapes OPDC planning register
   - Identifies business-relevant applications
   - Auto-categorizes by keywords

4. **Claude Curation**
   - All sources combined
   - Curated into categories
   - Scored by quality/relevance
   - Generates HTML report

---

## What You'll Get

### **More Business Spotlights** 🏪
- Planning applications = advance notice of openings
- RSS feeds = local newspaper business coverage
- Targeted searches = business group announcements

### **Better Local Coverage** 📰
- RSS feeds catch stories search engines might miss
- Direct from source, no search engine delay
- Official council news first-hand

### **Earlier Detection** ⏰
- Planning apps filed 2-3 months before opening
- RSS feeds updated instantly
- Better than waiting for Google indexing

---

## Testing The New Features

### **Test RSS Monitor:**
```bash
python rss_monitor.py
```

Expected output:
```
📡 Fetching RSS feeds...
   Checking Ealing Council...
   ✓ Ealing Council: Found 2 relevant items
   Checking Ealing Times...
   ✓ Ealing Times: Found 4 relevant items
...
📊 RSS Summary: Found 8 relevant items total
```

### **Test Planning Scraper:**
```bash
python planning_scraper.py
```

Expected output:
```
📋 Checking OPDC planning register...
   Fetching https://opdc.london.gov.uk/planning/planning-applications...
   Found 12 potential applications
   ✓ Found 3 relevant applications

🏪 Checking for business-related planning applications...
📊 Found 3 business-related applications
```

### **Test Full Integration:**
```bash
python content_discovery_perplexity.py
```

Should show all three sources working together!

---

## Configuration

### **Adding More RSS Feeds**

Edit `rss_monitor.py`, line 8:

```python
rss_feeds = [
    {
        "url": "https://your-feed-url.com/rss",
        "name": "Source Name",
        "category": "business_spotlights"
    },
    # Add more feeds here
]
```

### **Adjusting Keywords**

Edit `rss_monitor.py`, line 41:

```python
keywords = [
    'old oak', 'park royal',  # Main areas
    'opdc', 'hs2',            # Projects
    'nw10', 'w3', 'w12',      # Postcodes
    # Add your own keywords
]
```

### **Adjusting Planning Keywords**

Edit `planning_scraper.py`, line 88:

```python
business_keywords = [
    'change of use', 'a1', 'a3',  # Use classes
    'retail', 'restaurant', 'cafe',
    # Add more business types
]
```

---

## How RSS Feeds Are Scored

**Base score:** 5/10

**Boosts:**
- +2: Less than 7 days old
- +1: 7-14 days old
- +2: "Old Oak Common" mentioned
- +2: "Park Royal" mentioned
- +1: "HS2" + "Old Oak" both mentioned
- +1: Business opening keywords (for business category)

**Maximum:** 10/10

---

## How Planning Apps Are Scored

**Base score:** 7/10 (planning apps are valuable!)

**Boosts:**
- +2: Business-related keywords found
- Category auto-set to "business_spotlights"

**Maximum:** 10/10

---

## Troubleshooting

### **RSS feeds not working?**
- Feed URL might be wrong
- Site might not have RSS
- Check error message in workflow logs

**Fix:** Test feed URL in browser first, or remove from list

### **Planning scraper not finding anything?**
- OPDC website structure might have changed
- Need to update CSS selectors

**Fix:** The scraper is template code - may need adjustment based on actual site structure

### **Import errors?**
- Missing dependencies

**Fix:** Run `pip install -r requirements.txt`

---

## Expected Results

### **Before (Web Search Only):**
```
📊 Total stories: 8
🏗️ Development News: 5
🏪 Business Spotlights: 0  ← Empty!
👥 Community Stories: 2
📋 Planning & Policy: 1
```

### **After (Web + RSS + Planning):**
```
📊 Total stories: 18
🏗️ Development News: 6
🏪 Business Spotlights: 5  ← Much better!
👥 Community Stories: 4
📋 Planning & Policy: 3
```

---

## Cost Impact

**RSS Feeds:** FREE ✅
- No API costs
- Just HTTP requests

**Planning Scraper:** FREE ✅
- Public data
- Just HTTP requests

**Only cost:** Claude curation of additional items
- ~$0.01 extra per week
- Still very affordable!

---

## Next Steps

1. **Merge the PR** to get these features live
2. **Run workflow** and check results
3. **Review business spotlights** - should see improvement!
4. **Fine-tune** if needed:
   - Add more RSS feeds
   - Adjust keywords
   - Update planning scraper selectors

---

## Future Enhancements

**Possible additions:**
- Twitter/X monitoring for local hashtags
- Google My Business new listings scraper
- Facebook events scraper for community events
- Email newsletter parsing
- Automatic planning app categorization

**Let me know if you want any of these!** 🚀
