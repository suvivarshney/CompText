import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
import collections
from nltk. import BigramCollocationFinder
from nltk.metrics import *
import json
import itertools
from utilities import str_parser
import pickle


with open('positive-speech.json') as pluses:
    info1 = json.load(pluses)

with open('negative-speech.json') as minuses:
    info2 = json.load(minuses)


def training_corpora(texts):

    full_speeches = []

    for item in texts:
        original_text = item['TEXT']
        speech = str_parser(original_text)

        full_speeches.append(speech)

    return full_speeches


posdata = training_corpora(info1)
negdata = training_corpora(info2)

all_words = []

for item in posdata:
    for word in item:
        all_words.append(word)

for item in negdata:
    for word in item:
        all_words.append(word)


most_common = nltk.FreqDist(all_words)

common_feats = list(most_common.keys())[:1500]


def get_features(document):

    words = set(document)
    features = {}
    for word in common_feats:
        features[word] = (word in words)

    return features


def bigram_features(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])



pos_tags = [(get_features(speech), 'pos') for speech in posdata]
neg_tags = [(get_features(speech), 'neg') for speech in negdata]

poscut = len(pos_tags)*7/8
negcut = len(neg_tags)*7/8

trainfeats = pos_tags[:poscut] + neg_tags[:negcut]
testfeats = pos_tags[poscut:] + neg_tags[negcut:]



classifier = NaiveBayesClassifier.train(trainfeats)

save_classifier = open('naivebayes.pickle', "wb")
pickle.dump(classifier, save_classifier)
save_classifier.close()

testsets = collections.defaultdict(set)
refsets = collections.defaultdict(set)

for i, (feats, label) in enumerate(testfeats):
    refsets[label].add(i)
    observed = classifier.classify(feats)
    testsets[observed].add(i)


classifier.show_most_informative_features(15)


with open('allspeeches.json') as speeches:
    real_data = json.load(speeches)


def analyze_speeches():
   

    sentiment_scores = {}

    for data in real_data:
        title = ''.join(data['title'])         
        text_string = ''.join(data['TEXT'])

        speech = str_parser(text_string)

        speech_feats = get_features(speech)

        sentiment = classifier.classify(speech_feats)

        sentiment_scores[title] = sentiment

    return sentiment_scores
