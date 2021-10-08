from __future__ import division
from collections import Counter
import math
class nGram():
    def __init__(self, uni=False, bi=False):
        self.words=self.loadCorpus()
        if uni : self.unigram=self.createUnigram(self.words)
        if bi : self.bigram=self.createBigram(self.words)
        return
    def loadCorpus(self):
        """Method to load external file which contains raw corpus."""
        print ("Loading Corpus from data file")
        corpusfile = open('corpus.data', 'r')
        corpus = corpusfile.read()
        corpusfile.close()
        words = corpus.split(' ')
        print("there are %s words."%len(words))
        return words
    def createUnigram(self, words):
        print("Creating Unigram Model")
        unigram = Counter(words)
        return unigram
    def createBigram(self, words):
        """Method to create Bigram Model for words loaded from corpus."""
        print("Creating Bigram Model")
        biwords = []
        for index, item in enumerate(words):
            if index==len(words)-1:
                break
            biwords.append(item+' '+words[index+1])
        print("Calculating Count for Bigram Model")
        bigram = Counter(biwords)

        return bigram
    def  count_word(self,word, gram = 'bi'):
        if gram == 'bi':
            return self.unigram[word],  len(self.unigram)
        else:
            return 0
    def probability(self, word, words = "", gram = 'uni'):
        if gram == 'uni':
            return math.log((self.unigram[word]+1)/(len(self.words)+len(self.unigram)))
        elif gram == 'bi':
            if  self.bigram[words] == 0:
                return math.log((self.bigram[words])+1/(self.unigram[word]+len(self.unigram)))   #1-smooth
            else:
                return math.log((self.bigram[words])/(self.unigram[word]))
    def sentenceprobability(self, sent, gram='uni', form='antilog'):
        words = sent.lower().split()
        P=0
        if gram == 'uni':
            for index, item in enumerate(words):
                P = P + self.probability(item)
        if gram == 'bi':
            for index, item in enumerate(words):
                if index == len(words)- 1: break
                P = P + self.probability(item, item+' '+words[index+1], 'bi')
        if form == 'log':
            return P
        elif form == 'antilog':
            return math.pow(math.e, P)

