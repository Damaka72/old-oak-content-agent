# 📰 Old Oak Town Content Discovery Agent

Automated AI-powered news curation for Old Oak Common, Park Royal, and the HS2 development area.

## 🎯 What It Does

This agent automatically:
1. **Searches the web** for Old Oak Common news using Perplexity AI
2. **Curates content** using Claude AI to identify newsworthy stories
3. **Categorizes stories** into Development, Business, Community, and Planning
4. **Scores quality** based on local relevance, timeliness, and credibility
5. **Generates reports** as beautiful HTML pages for editorial review
6. **Runs weekly** every Monday at 9 AM UTC via GitHub Actions

## 🚀 Quick Start

### Prerequisites
- GitHub account
- Anthropic API key (Claude)
- Perplexity API key (recommended)

### Setup

1. **Clone this repository**
   ```bash
   git clone https://github.com/yourusername/old-oak-content-agent.git
   cd old-oak-content-agent
   ```

2. **Add API keys to GitHub Secrets**
   - Go to Settings → Secrets and variables → Actions
   - Add `ANTHROPIC_API_KEY`
   - Add `PERPLEXITY_API_KEY` (see [PERPLEXITY_SETUP.md](PERPLEXITY_SETUP.md))

3. **Enable GitHub Actions**
   - Go to Actions tab
   - Enable workflows

4. **Test manually**
   - Actions → Weekly Content Discovery → Run workflow

## 📁 Files Overview

### Main Scripts

| File | Description | Status |
|------|-------------|--------|
| `content_discovery_perplexity.py` | **RECOMMENDED** - Uses Perplexity for search, Claude for curation | ✅ Ready |
| `content_discovery_improved.py` | Uses Claude web search only, improved algorithm | ✅ Ready |
| `content_discovery.py` | Original version with known issues | ⚠️ Deprecated |

### Workflows

| File | Description |
|------|-------------|
| `.github/workflows/weekly-discovery-perplexity.yml` | Perplexity + Claude workflow (recommended) |
| `.github/workflows/weekly-discovery.yml` | Claude-only workflow |

### Documentation

| File | Description |
|------|-------------|
| `PERPLEXITY_SETUP.md` | Complete Perplexity integration guide |
| `IMPROVEMENTS.md` | Technical comparison of implementations |
| `README.md` | This file |

## 🔍 How It Works

### 1. Web Search (Perplexity)
```python
# Searches for:
- Old Oak Common HS2 station news
- Park Royal OPDC development updates
- Local business openings and closures
- Planning applications and consultations
```

### 2. Content Curation (Claude)
```python
# Analyzes search results and extracts:
- Article title, URL, source
- Publication date
- Summary and local relevance
- Category assignment
- Quality score (1-10)
```

### 3. Report Generation
```
# Creates:
- JSON file with structured data
- HTML review page with:
  * Statistics dashboard
  * Top stories section
  * Categorized content
  * Quality scores
  * Direct links to sources
```

## 📊 Output Example

**Weekly JSON** (`reviews/review_2025-01-15.json`):
```json
{
  "date": "2025-01-15",
  "curated_content": {
    "categories": {
      "development_news": [
        {
          "title": "HS2 Old Oak Station Construction Reaches Milestone",
          "url": "https://...",
          "source": "Construction News",
          "date": "2025-01-12",
          "summary": "Major progress on the station concourse...",
          "relevance": "Direct impact on local transport connectivity",
          "score": 9
        }
      ]
    },
    "total_items": 12,
    "week_summary": "This week found 12 newsworthy stories..."
  }
}
```

**Weekly HTML** (`reviews/review_2025-01-15.html`):
- Professional layout with Old Oak Town branding
- Color-coded quality scores
- Clickable links to source articles
- Mobile-responsive design

## 🎨 Categories

| Category | Icon | Focus |
|----------|------|-------|
| Development News | 🏗️ | HS2, OPDC, construction updates |
| Business Spotlights | 🏪 | Local businesses, openings, closures |
| Community Stories | 👥 | Events, residents, initiatives |
| Planning & Policy | 📋 | Applications, consultations, decisions |

## ⚙️ Configuration

### Adjust Search Queries

Edit in `content_discovery_perplexity.py`:
```python
search_queries = [
    {
        "query": "Your custom search query",
        "category": "development_news",
        "focus": "What to prioritize"
    }
]
```

### Change Schedule

Edit `.github/workflows/weekly-discovery-perplexity.yml`:
```yaml
schedule:
  - cron: '0 9 * * 1'  # Monday 9 AM UTC
  # Examples:
  # - cron: '0 9 * * 5'  # Friday 9 AM UTC
  # - cron: '0 14 * * 1,3,5'  # Mon/Wed/Fri 2 PM UTC
```

### Modify Curation Criteria

Adjust quality scoring in the curation prompt:
```python
# In curate_with_claude() function
# score: Quality/importance score 1-10 based on:
#   * Local impact (high = directly affects residents)
#   * Timeliness (high = very recent)
#   * Credibility (high = official sources)
#   * Uniqueness (high = exclusive reporting)
```

## 💰 Cost Estimate

**Weekly automated run (4 searches + curation):**
- Perplexity API: ~$0.02
- Claude API: ~$0.02
- **Total: ~$0.04/week** or **~$2/year**

Very affordable for automated news curation!

## 🔧 Local Development

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export PERPLEXITY_API_KEY="pplx-..."

# Run locally
python content_discovery_perplexity.py
```

### Test Different Versions
```bash
# Test Perplexity version (recommended)
python content_discovery_perplexity.py

# Test improved Claude-only version
python content_discovery_improved.py

# Compare outputs in reviews/ folder
ls -la reviews/
open reviews/review_$(date +%Y-%m-%d).html
```

## 📈 Future Enhancements

Potential features to add:
- [ ] Email digest to editors
- [ ] RSS feed generation
- [ ] Slack/Discord integration
- [ ] Sentiment analysis
- [ ] Duplicate detection
- [ ] Image extraction from articles
- [ ] Historical trend analysis
- [ ] Geographic tagging by area
- [ ] Source diversity tracking
- [ ] Manual override system (YAML config)

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for details.

## 🐛 Troubleshooting

### Common Issues

**"PERPLEXITY_API_KEY not found"**
- Add to GitHub Secrets (see [PERPLEXITY_SETUP.md](PERPLEXITY_SETUP.md))

**"Rate limit exceeded"**
- Script includes delays, but check your API tier limits
- Free tier: 20 requests/min (Perplexity)

**"No stories found"**
- Check search queries are relevant
- Review raw search results in JSON output
- Adjust minimum quality score threshold

**Workflow not running**
- Check Actions tab is enabled
- Verify cron schedule syntax
- Check API keys are set in Secrets

### Getting Help

1. Check the logs in Actions tab
2. Review [PERPLEXITY_SETUP.md](PERPLEXITY_SETUP.md)
3. Read [IMPROVEMENTS.md](IMPROVEMENTS.md) for technical details
4. Create an issue with error details

## 📜 License

MIT License - feel free to adapt for your own hyperlocal news platform!

## 🙏 Credits

- **Perplexity AI** - Web search API
- **Anthropic Claude** - Content curation and analysis
- **Old Oak Town** - Hyperlocal news for Old Oak Common

## 🌳 About Old Oak Town

Old Oak Common is undergoing one of Europe's largest regeneration projects, with HS2, Elizabeth Line, and extensive housing development transforming the area. This agent helps track the rapid changes and keep residents informed.

---

**Built with ❤️ for the Old Oak Common community**
