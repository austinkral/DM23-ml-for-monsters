from bs4 import *
import requests
import re, nltk
from nltk import ConditionalFreqDist
from nltk import ngrams
from nltk.tokenize import RegexpTokenizer
from nltk.util import pad_sequence
from nltk.lm.preprocessing import pad_both_ends
from nltk.probability import ConditionalProbDist, ELEProbDist
from functools import reduce
nltk.download('punkt')

class Autopoiem():
    def __init__(self, corpus, n):
        self.n = n
        url = corpus
        res = requests.get(url)
        html_page = res.text
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.get_text()
        self.tokenized_corpus = self.tokenize_corpus(text)
        self.ngrams = self.generate_ngrams(self.tokenized_corpus, self.n)
        self.cpd = self.generate_dist(self.n)

    def tokenize_corpus(self, corpus):
        tokenized_corpus = []
        replacements = [
             ["[-\n]",                   " "] # Hyphens to whitespace
            ,[r'[][(){}#$%"]_',           ""] # Strip unwanted characters like quotes and brackets
            ,[r'\s([./-]?\d+)+[./-]?\s', ""] # Standardize numbers
            ,[r'\.{3,}',                 ""] # remove ellipsis
            ,[r'(\w)([.,?!;:])',         r'\1 \2' ]  # separate punctuation from previous word
        ]
        
        # This is a function that applies a single replacement from the list
        resub = lambda words, repls: re.sub(repls[0], repls[1], words)
        
        # we use the resub function to applea each replacement to the entire corpus,
        normalized_corpus = reduce(resub, replacements, corpus)

        spaced_corpus = re.sub(r'(\w)([.,?!;:])', r'\1 \2', normalized_corpus) 
        
        sentences = spaced_corpus.split('.')
        
        for sentence in sentences:
            words = sentence.split() # split on whitespace
            words = [word.lower() for word in words]
            words = list(pad_both_ends(words, n=self.n))
            tokenized_corpus += words
        
        return tokenized_corpus

    def generate_ngrams(self, corpus, n):
        ngrams = []
        for i in range(n-1, len(corpus)): 
            ngrams.append(tuple(corpus[i-(n-1):i+1]))  
        return ngrams

    def generate_dist(self, n):
        cfd = ConditionalFreqDist()
        for ngram in self.ngrams:
            condition = tuple(ngram[0:n-1]) 
            outcome = ngram[n-1]
            cfd[condition][outcome] += 1
        cpd = ConditionalProbDist(cfd, ELEProbDist, len(cfd))
        return cpd

    def get_autopoiem(self, num_lines, seed = None):
        autopoiem = []

        if seed:
            autopoiem = autopoiem + (list(pad_sequence(seed, self.n, pad_left=True, pad_right=False, left_pad_symbol='<s>') ) )
        else:
            autopoiem = autopoiem + (list(pad_sequence('', self.n, pad_left=True, pad_right=False, left_pad_symbol='<s>') ) )
        
        for i in range(num_lines):
            next_token = tuple(autopoiem[-(self.n-1):])

            count = 0
            
            while next_token != '</s>' or count < 10:
                
                # get the last n-1 tokens to condition on next
                lessgram = tuple(autopoiem[-(self.n-1):])

                next_token = self.cpd[lessgram].generate()
                autopoiem.append(next_token)

                count = count + 1

        autopoiem = ' '.join(autopoiem)
        autopoiem = self.add_stops(autopoiem)

        return autopoiem

    def add_stops(self, string):
        string = re.sub(r"</s>(?:\s</s>)*\s<s>(?:\s<s>)*", "\n", string)
        string = re.sub(r"(<s>\s)+", "", string) # initial tokens
        string = re.sub(r"(</s>)", "", string) # final token
        
        return string

a1 = Autopoiem('https://www.gutenberg.org/cache/epub/42041/pg42041.txt', 2)
autopoiem1 = a1.get_autopoiem(10)
print(autopoiem1)
