# 🚀 Perplexity Integration Setup Guide

## Why Perplexity?

Perplexity AI offers superior web search capabilities compared to standard search APIs:
- ✅ **Better search quality** - More relevant, recent results
- ✅ **Built-in citations** - Automatic source tracking
- ✅ **Cost-effective** - Free tier available, affordable paid plans
- ✅ **Online models** - Always searches current web content
- ✅ **Structured responses** - Easier to parse and curate

## 📋 Setup Steps

### Step 1: Get Your Perplexity API Key

1. Go to [Perplexity API](https://www.perplexity.ai/settings/api)
2. Sign up or log in
3. Navigate to API settings
4. Click "Generate API Key"
5. Copy your API key (starts with `pplx-...`)

### Step 2: Add API Key to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top right)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add secret:
   - Name: `PERPLEXITY_API_KEY`
   - Value: `pplx-your-api-key-here`
6. Click **Add secret**

### Step 3: Verify Existing API Keys

Make sure you also have:
- ✅ `ANTHROPIC_API_KEY` - For Claude curation (should already exist)

### Step 4: Choose Your Workflow

You now have three workflow options:

#### Option A: Use Perplexity (Recommended)
```bash
# Uses: content_discovery_perplexity.py
# Workflow: .github/workflows/weekly-discovery-perplexity.yml
```
**Best for:** Better search quality, proper citations, structured data

#### Option B: Use Claude Only
```bash
# Uses: content_discovery_improved.py
# Workflow: .github/workflows/weekly-discovery.yml
```
**Best for:** Simpler setup, one API key

#### Option C: Use Original (Not Recommended)
```bash
# Uses: content_discovery.py
```
**Issues:** Known bugs with result extraction

### Step 5: Enable the Perplexity Workflow

**Option 1 - Replace current workflow:**
```bash
mv .github/workflows/weekly-discovery.yml .github/workflows/weekly-discovery-old.yml
mv .github/workflows/weekly-discovery-perplexity.yml .github/workflows/weekly-discovery.yml
```

**Option 2 - Keep both workflows:**
Both workflows can coexist. Rename if needed.

### Step 6: Test Manually

Before waiting for the scheduled run:

1. Go to **Actions** tab in GitHub
2. Click **Weekly Content Discovery (Perplexity)**
3. Click **Run workflow** → **Run workflow**
4. Wait 2-3 minutes
5. Check the results in `reviews/` folder

**Or test locally:**
```bash
export PERPLEXITY_API_KEY="pplx-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
python content_discovery_perplexity.py
```

## 📊 What's Different with Perplexity?

### Search Quality Comparison

| Feature | Perplexity | Claude Web Search |
|---------|-----------|------------------|
| Search Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Citations | ✅ Automatic | ⚠️ Limited |
| Cost (per search) | ~$0.005 | ~$0.01 |
| Rate Limits | 20 req/min (free) | 30k tokens/min |
| Response Time | 2-5 seconds | 3-8 seconds |
| Recency | Always current | Always current |

### Expected Output Improvements

**Before (Claude only):**
- Generic summaries
- Missing source URLs
- Inconsistent citation format

**After (Perplexity + Claude):**
- Specific article details
- Actual URLs from Perplexity citations
- Structured source tracking
- Better date information
- More relevant local news

## 💰 Cost Breakdown

### Perplexity Pricing

**Free Tier:**
- $5 free credit on signup
- ~1,000 searches
- 20 requests/minute limit

**Pay-as-you-go:**
- `sonar-small-online`: ~$0.20 per 1M tokens
- For this use case: ~$0.005 per search
- Weekly run (4 searches): **~$0.02/week** = **~$1/year**

**Pro Plan:** $20/month (unlimited, not needed for this use case)

### Total Cost Estimate

**Weekly automated run:**
- Perplexity: 4 searches × $0.005 = $0.02
- Claude curation: ~8k tokens × $0.003/1k = $0.024
- **Total: ~$0.04/week** or **~$2/year**

Very affordable for automated news curation!

## 🔧 Troubleshooting

### Error: "PERPLEXITY_API_KEY not found"
**Solution:** Add the API key to GitHub Secrets (see Step 2)

### Error: "401 Unauthorized"
**Solution:** Check your API key is correct and active

### Error: "429 Rate Limit Exceeded"
**Solutions:**
- Free tier limit is 20 requests/minute
- The script already includes 15s delays
- If issue persists, increase delay in code or upgrade to paid tier

### Error: "No results found"
**Possible causes:**
- Perplexity couldn't find relevant results (rare)
- API connectivity issue
- Check workflow logs for details

### Fallback Behavior

If Perplexity API key is not set, the script automatically falls back to Claude's web search:
```
⚠️  PERPLEXITY_API_KEY not found, falling back to Claude web search
```

This ensures the workflow never completely fails.

## 🎯 Perplexity Model Options

The script uses `llama-3.1-sonar-small-128k-online` by default (most cost-effective).

**Other options (edit in code if needed):**

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| `sonar-small-online` | ⚡⚡⚡ | $ | Quick searches, budget |
| `sonar-medium-online` | ⚡⚡ | $$ | Balanced quality |
| `sonar-large-online` | ⚡ | $$$ | Maximum quality |

For Old Oak Town news curation, **small is perfect** - it's fast and accurate for local news.

## 📈 Next Steps After Setup

1. ✅ Run a manual test to verify it works
2. ✅ Review the HTML output quality
3. ✅ Compare with previous Claude-only results
4. ✅ Adjust search queries if needed (edit in `content_discovery_perplexity.py`)
5. ✅ Set up email notifications (future enhancement)

## 🆘 Getting Help

**GitHub Issues:**
Create an issue in your repo with:
- Error message
- Workflow run logs
- API key status (don't share actual key!)

**Perplexity Support:**
- [API Documentation](https://docs.perplexity.ai/)
- [Discord Community](https://discord.gg/perplexity)

**Claude Support:**
- [Anthropic Documentation](https://docs.anthropic.com/)

---

## ✨ Summary

Once setup is complete:
1. ✅ Better search quality with proper citations
2. ✅ More accurate local news discovery
3. ✅ Structured data for easier curation
4. ✅ Cost-effective (~$2/year)
5. ✅ Automatic weekly runs every Monday

**Total setup time:** ~5 minutes

**Your Old Oak Town content discovery agent is now supercharged! 🚀**
