import tweepy, os
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from newsapi import NewsApiClient
from .utils import cache

twitter = tweepy.Client(bearer_token=os.getenv("TWITTER_BEARER"))
newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))
analyzer = SentimentIntensityAnalyzer()

@cache("sent")
def get_sentiment(ticker: str) -> dict:
    score = 0
    mentions = 0

    # Twitter
    try:
        tweets = twitter.search_recent_tweets(query=f"${ticker} lang:en -is:retweet", max_results=30)
        if tweets.data:
            for t in tweets.data:
                s = analyzer.polarity_scores(t.text)["compound"]
                score += s
            mentions += len(tweets.data)
    except:
        pass

    # News
    try:
        news = newsapi.get_everything(q=ticker, language="en", page_size=10, sort_by="publishedAt")
        for a in news.get("articles", []):
            text = a["title"] + " " + a.get("description", "")
            s = analyzer.polarity_scores(text)["compound"]
            score += s
            mentions += 1
    except:
        pass

    return {"sentiment_score": score, "mentions": mentions}
