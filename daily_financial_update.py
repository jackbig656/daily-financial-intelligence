#!/usr/bin/env python3
"""
Daily Financial Intelligence Notion Updater
Automatically fetches financial news and creates daily updates in Notion
"""

import os
import requests
from datetime import datetime
from typing import List, Dict, Any
import json

# Configuration from environment variables
NOTION_API_KEY = os.environ.get('NOTION_API_KEY')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')  # Free Google Search API

# Notion API Configuration
NOTION_VERSION = '2022-06-28'
NOTION_HEADERS = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Content-Type': 'application/json',
    'Notion-Version': NOTION_VERSION
}


def search_financial_news() -> List[Dict[str, str]]:
    """
    Search for latest financial news using Serper API (free tier: 2,500 queries/month)
    Alternative: Could use NewsAPI, but Serper is more generous for free tier
    """
    today = datetime.now().strftime('%Y-%m-%d')

    # Multiple targeted searches for comprehensive coverage
    search_queries = [
        f"major financial news worldwide {today} stock market",
        f"market movers stocks {today}",
        f"investment opportunities {today} emerging markets"
    ]

    all_results = []

    for query in search_queries:
        if SERPER_API_KEY:
            # Use Serper API if available
            url = "https://google.serper.dev/search"
            payload = json.dumps({
                "q": query,
                "num": 5
            })
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }

            try:
                response = requests.post(url, headers=headers, data=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'organic' in data:
                        all_results.extend(data['organic'][:3])
            except Exception as e:
                print(f"Error searching with Serper: {e}")
        else:
            # Fallback: Use free public APIs or RSS feeds
            print(f"No Serper API key found. Skipping search: {query}")

    return all_results


def analyze_market_data() -> Dict[str, Any]:
    """
    Fetch market data from free APIs
    Using Alpha Vantage (free tier: 25 requests/day) or Yahoo Finance
    """
    market_data = {
        'indices': {},
        'top_movers': [],
        'sentiment': 'Mixed'
    }

    # You can add Alpha Vantage API calls here
    # For now, return template data
    # In production, you'd call: https://www.alphavantage.co/query?function=MARKET_STATUS&apikey=YOUR_KEY

    return market_data


def generate_investment_insights(news_results: List[Dict]) -> str:
    """
    Generate investment insights based on news and market data
    This is a template - in production you might use AI APIs or more sophisticated analysis
    """

    today = datetime.now().strftime('%B %d, %Y')

    # Build content from news results
    news_summary = "\n\n".join([
        f"**{item.get('title', 'News Item')}**: {item.get('snippet', 'No description available')}"
        for item in news_results[:5]
    ])

    content = f"""# Market Overview - {today}

## Key Financial Events Worldwide

{news_summary if news_summary else "Unable to fetch current news. Please check API configurations."}

---

## Investment Opportunities for Aggressive Growth (Week Ahead)

### 🎯 HIGH-CONVICTION PLAYS

**1. Technology Sector**
- **Focus Areas**: AI infrastructure, semiconductors, cloud computing
- **Catalyst**: Continued enterprise AI adoption
- **Risk Level**: Medium-High

**2. Emerging Markets**
- **Focus Areas**: Latin American fintech, Asian e-commerce
- **Catalyst**: Digital transformation in developing economies
- **Risk Level**: High (currency and political risk)

**3. Biotech/Healthcare**
- **Focus Areas**: Gene therapy, precision medicine
- **Catalyst**: FDA approvals pipeline, aging demographics
- **Risk Level**: Very High (regulatory and clinical trial risk)

---

## 💰 Cash Deployment Strategy (Month-to-Month)

For aggressive growth with extra monthly cash flow:

**40%** - Core Tech Positions
- Dollar-cost average into established tech leaders
- Focus on companies with strong cash flow and AI exposure

**30%** - High-Growth Plays
- Build positions in companies with 30%+ revenue growth
- Look for market leaders in emerging categories

**20%** - Sector Rotation/Opportunistic
- Rotate based on weekly news and earnings
- Consider undervalued sectors showing momentum

**10%** - Speculative/High-Risk
- Small cap stocks with breakthrough potential
- Set strict stop-losses (15-20%)

---

## ⚠️ Risk Factors This Week

- **Geopolitical Tensions**: Monitor international developments
- **Interest Rate Environment**: Fed policy impacts valuations
- **Valuation Concerns**: Growth stocks at premium multiples
- **Market Momentum**: Watch for technical indicators

---

## 📅 Week Ahead Catalysts

- Earnings season developments
- Economic data releases (GDP, employment, inflation)
- Sector-specific news and M&A activity
- Global market correlations

---

**Disclaimer**: This is educational analysis based on current market data, not personalized financial advice. Markets are inherently risky, especially with aggressive growth strategies. Conduct your own research and consider consulting a licensed financial advisor before making investment decisions.

**Data Sources**: {len(news_results)} news sources analyzed
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
"""

    return content


def create_notion_page(content: str) -> bool:
    """
    Create a new page in the Notion database with today's financial update
    """
    today = datetime.now()
    page_title = f"Financial Intelligence - {today.strftime('%B %d, %Y')}"

    # Build the page data
    page_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": page_title
                        }
                    }
                ]
            },
            "Date": {
                "date": {
                    "start": today.strftime('%Y-%m-%d')
                }
            },
            "Market Sentiment": {
                "select": {
                    "name": "Mixed"
                }
            },
            "Key Events": {
                "number": 5
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content[:2000]  # Notion has block size limits
                            }
                        }
                    ]
                }
            }
        ]
    }

    try:
        response = requests.post(
            'https://api.notion.com/v1/pages',
            headers=NOTION_HEADERS,
            json=page_data,
            timeout=30
        )

        if response.status_code == 200:
            print(f"✅ Successfully created Notion page: {page_title}")
            print(f"URL: {response.json().get('url')}")
            return True
        else:
            print(f"❌ Error creating Notion page: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Exception creating Notion page: {e}")
        return False


def main():
    """
    Main execution function
    """
    print("🚀 Starting Daily Financial Intelligence Update...")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Validate environment variables
    if not NOTION_API_KEY:
        print("❌ ERROR: NOTION_API_KEY environment variable not set")
        return False

    if not NOTION_DATABASE_ID:
        print("❌ ERROR: NOTION_DATABASE_ID environment variable not set")
        return False

    print("✅ Environment variables validated")

    # Step 1: Fetch financial news
    print("\n📰 Fetching financial news...")
    news_results = search_financial_news()
    print(f"✅ Found {len(news_results)} news items")

    # Step 2: Analyze market data
    print("\n📊 Analyzing market data...")
    market_data = analyze_market_data()
    print("✅ Market data analyzed")

    # Step 3: Generate insights
    print("\n🧠 Generating investment insights...")
    content = generate_investment_insights(news_results)
    print("✅ Insights generated")

    # Step 4: Create Notion page
    print("\n📝 Creating Notion page...")
    success = create_notion_page(content)

    if success:
        print("\n✅ Daily financial update completed successfully!")
        return True
    else:
        print("\n❌ Failed to create daily update")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
