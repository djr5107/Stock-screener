import requests
import os
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient

# Import cache decorator correctly
from src.utils import cache

analyzer = SentimentIntensityAnalyzer()
newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))

@cache("sent")
def get_sentiment(ticker: str) -> dict:
    score = 0
    mentions = 0

    # === X (Twitter) API v2 ===
    bearer = os.getenv("TWITTER_BEARER")
    if bearer:
        headers = {"Authorization": f"Bearer {bearer}"}
        query = f"${ticker} lang:en -is:retweet"
        url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=10"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                for tweet in data:
                    s = analyzer.polarity_scores(tweet["text"])["compound"]
                    score += s
                mentions += len(data)
        except Exception as e:
            pass  # Silent fail

    # === News API ===
    try:
        news = newsapi.get_everything(q=ticker, language="en", page_size=10)
        for a in news.get("articles", []):
            text = a["title"] + " " + a.get("description", "")
            s = analyzer.polarity_scores(text)["compound"]
            score += s
            mentions += 1
    except:
        pass

    return {
        "sentiment_score": score,
        "mentions": mentions
    }
