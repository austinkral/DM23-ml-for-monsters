from newscatcher import Newscatcher, describe_url
import re, nltk, feedparser, json, time
nltk.download('punkt')

class Autopoiem2():
    def __init__(self, news_site):
        site = Newscatcher(website = news_site)
        news = site.get_news()
        stories = news['articles']
        for story in stories:
            print(story['summary'])

a1 = Autopoiem2('nytimes.com')
a2 = Autopoiem2('theatlantic.com')