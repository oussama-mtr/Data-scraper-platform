import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

def fetch_ma_deals(days_back=30):
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    queries = [
        'Morocco acquisition merger',
        'Africa merger acquisition deal',
        'Maroc fusion acquisition',
        'Morocco investment deal finance',
    ]

    all_articles = []
    seen_titles = set()

    for query in queries:
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 10,
            'apiKey': NEWS_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for article in data.get('articles', []):
                title = article.get('title', '')
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    all_articles.append({
                        'title': title,
                        'description': article.get('description', '') or '',
                        'content': article.get('content', '') or '',
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt', '')[:10],
                    })

    all_articles.sort(key=lambda x: x['published_at'], reverse=True)
    return all_articles[:20]