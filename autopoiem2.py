import newspaper
import re, nltk, feedparser, json, time
nltk.download('punkt')

class Autopoiem2():
    def __init__(self, news_site):
        article = newspaper.Article(url = news_site, language = 'en')
        article.download()
        article.parse()
        article = {'title': str(article.title),
                'text': str(article.text),
                'authors': article.authors,
                'published_date': str(article.publish_date),
                'top_image': str(article.top_image),
                'videos': article.movies,
                'keywords': article.keywords,
                'summary': str(article.summary)
        }
        print(article['text'])

a1 = Autopoiem2('https://www.nytimes.com/live/2021/10/25/us/biden-spending-bill-negotiations')