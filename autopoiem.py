from pygooglenews import GoogleNews
import re, nltk
from nltk import ConditionalFreqDist
from nltk import ngrams
from nltk.tokenize import RegexpTokenizer
from nltk.util import pad_sequence
from nltk.lm.preprocessing import pad_both_ends
from nltk.probability import ConditionalProbDist, ELEProbDist
nltk.download('punkt')

class Autopoiem():
    def __init__(self, n):
        self.n = n
        gn = GoogleNews(lang = 'en', country = 'US')
        self.stories = gn.top_news()
        self.ngrams = self.generate_ngrams(self.tokenize_stories(self.parse_top_stories()), self.n)
        self.generate_dist(self.n)
        self.autopoiem = self.get_autopoiem(self.n)

    def parse_top_stories(self):
        self.top_stories = {}
        for i, story in enumerate(self.stories['entries']):
            split = re.search(r'-[^-]*$', story['title']).start()
            self.top_stories[i] = story['title'][:split - 1].lower()
            print(self.top_stories[i])
        return self.top_stories

    def tokenize_stories(self, stories):
        self.tokenized_top_stories = {}
        tokenizer = RegexpTokenizer(r'\w+|\$[\d\.]+|\S+')
        for i in range (len(self.top_stories)):
            self.tokenized_top_stories[i] = ['<s>'] + tokenizer.tokenize(self.top_stories[i]) + ['<\s>']
        return self.tokenized_top_stories

    def generate_ngrams(self, stories, n):
        n_grams = []
        for story in self.tokenized_top_stories.values():
            for i in range(n-1, len(story)): 
                n_grams.append(tuple(story[i-(n-1):i+1]))    
        print(n_grams)
        return n_grams

    def generate_dist(self, n):
        cfd = ConditionalFreqDist()
        for ngram in self.ngrams:
            condition = tuple(ngram[0:n-1]) 
            outcome = ngram[n-1]
            print(condition)
            print(outcome)
            cfd[condition][outcome] += 1
        bins = len(cfd) # we have to pass the number of bins in our freq dist in as a parameter to probability distribution, so we have a bin for every word
        cpd = ConditionalProbDist(cfd, ELEProbDist, bins)
        self.cpd = cpd

    def get_autopoiem(self, num_lines, seed = []):
        autopoiem = []

        if seed:
            autopoiem = autopoiem + (list(pad_sequence(seed, self.n, pad_left=True, pad_right=False, left_pad_symbol='<s>') ) )
        else:
            autopoiem = autopoiem + (list(pad_sequence('', self.n, pad_left=True, pad_right=False, left_pad_symbol='<s>') ) )
        
        for i in range(num_lines):
            next_token = tuple(autopoiem[-(self.n-1):])
            
            # keep generating tokens as long as we havent reached the stop sequence
            while next_token != '</s>':
                
                # get the last n-1 tokens to condition on next
                lessgram = tuple(autopoiem[-(self.n-1):])

    
                next_token = self.cpd[lessgram].generate()
                autopoiem.append(next_token)

        autopoiem = ' '.join(autopoiem)
        autopoiem = add_stops(autopoiem)

        return autopoiem

    def add_stops(string):
        string = re.sub(r"</s>(?:\s</s>)*\s<s>(?:\s<s>)*", "\n", string)
        string = re.sub(r"(<s>\s)+", "", string) # initial tokens
        string = re.sub(r"(</s>)", "", string) # final token
        
        return string

a1 = Autopoiem(2)
