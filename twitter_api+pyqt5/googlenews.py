#ref https://towardsdatascience.com/how-to-get-the-latest-covid-19-news-using-google-news-feed-950d9deb18f1

import feedparser
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd

search = input('Search Key:')
web = "http://news.google.com/news?q={}-19&hl=en-US&sort=date&gl=US&num=100&output=rss"
url = web.format(search)

class ParseFeed():

    def __init__(self, url):
        self.feed_url = url
        
    def clean(self, html):
        '''
        Get the text from html and do some cleaning
        '''
        soup = BeautifulSoup(html)
        text = soup.get_text()
        text = text.replace('\xa0', ' ')
        return text

    def parse(self):
        '''
        Parse the URL, and print all the details of the news 
        '''
        feeds = feedparser.parse(self.feed_url).entries
        df = pd.DataFrame(columns= ['Headline','Posted', 'Content', 'Link'])
        for f in feeds:   
            '''pprint({
                'Description': self.clean(f.get("description", "")),
                'Published Date': f.get("published", ""),
                'Title': f.get("title", ""),
                'Url': f.get("link", "")
            })'''

            cont = self.clean(f.get("description", ""))
            date = f.get("published", "")
            title = f.get("title", "")
            link =  f.get("link", "")
            new_column = pd.Series([title,date,cont,link], index=df.columns)
            df = df.append(new_column,ignore_index=True)

        df.to_csv('google.csv')


            
feed = ParseFeed(url)
feed.parse()