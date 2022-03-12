import nltk
from nltk.collocations import *
import json
from utilities import str_parser
import pickle

with open('allspeeches.json') as speeches:
    real_data = json.load(speeches)


bigram_measures = nltk.collocations.BigramAssocMeasures()


def top_bigrams():
  

    prez_phrases = {}



    for data in real_data:
     

        prez_name = ''.join(data['president'])

        title = ''.join(data['title'])

        if prez_name not in prez_phrases:
            prez_phrases[prez_name] = {}

        speech_str = ''.join(data['TEXT'])

        speech = str_parser(speech_str)  



        finder = BigramCollocationFinder.from_words(speech)

        finder.apply_freq_filter(3)

        ngrams = finder.nbest(bigram_measures.pmi, 5) 

        prez_phrases[prez_name][title] = ngrams

    return prez_phrases


def bigram_sentiment():
  

    classifier_f = open("naivebayes.pickle", "rb")
    classifier = pickle.load(classifier_f)
    classifier_f.close()

    relevant_bigrams = top_bigrams()

    bigram_rating = {}

    for prez in relevant_bigrams:
        for speech in relevant_bigrams[prez]:
            current_bigram = relevant_bigrams[prez][speech]

            for tup1, tup2 in current_bigram:
                sentiment1 = classifier.classify({tup1: True})
                sentiment2 = classifier.classify({tup2: True})
    

                if sentiment1 == 'pos' and sentiment2 == 'pos':
                    bigram_rating[tup1, tup2] = 'positive'
                elif sentiment1 != sentiment2:
                    bigram_rating[tup1, tup2] = 'neutral'
                else:
                    bigram_rating[tup1, tup2] = 'negative'

    return bigram_rating
