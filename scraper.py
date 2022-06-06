from newspaper import Article
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from nltk.sentiment import SentimentIntensityAnalyzer
import plotly.express as px

sia = SentimentIntensityAnalyzer()

def get_all_links(req: requests.Response):
    soup = BeautifulSoup(req.content, 'lxml')
    a_s = soup.find_all('a', {"class": "u-clickable-card__link"}, href=True)
    
    article_links = []
    for a in a_s:
        article_links.append(a['href'])
        
    return article_links

def process_link(link: list):
    article = Article(link)
    article.download()
    article.parse()
    
    return article

def get_sentiments(text):
    """
    find the sentiment score for the text and return the sentiment of the maximum score generated
    """
    scores = sia.polarity_scores(text)
    return "positive" if scores["pos"] > scores["neg"] else "negative"


if __name__ == '__main__':
    url = 'https://www.aljazeera.com/where/mozambique/'
    req = requests.get(url)
    
    links = get_all_links(req)
    articles = {"links": [], "title": [], "text": [], "sentiment": []}
    
    for link in tqdm(links, desc="Scraping articles"):
        l = "https://www.aljazeera.com"+link
        article = process_link(l)
        articles["links"].append(l)
        articles["title"].append(article.title)
        articles["text"].append(article.text)
        articles["sentiment"].append(get_sentiments(article.text))
        
    articles = pd.DataFrame(articles)
    
    articles.to_json("articles.json", orient="records")
    
    num_counts = articles.sentiment.value_counts().to_list()
    
    plot = px.bar(x=["negative", "positive"], y=num_counts)
    
    plot.write_image("./sentiment_plot.png")