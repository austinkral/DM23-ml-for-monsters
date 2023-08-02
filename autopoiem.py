from pygooglenews import GoogleNews

class Autopoiem():

    def __init__(self):
        gn = GoogleNews(lang = 'en', country = 'US')
        stories = gn.top_news()
        for story in enumerate(stories):
            story.headline()

a1 = Autopoiem()

        
        
