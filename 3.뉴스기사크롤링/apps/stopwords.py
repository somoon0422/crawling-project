import os
import nltk
import pickle
from nltk.corpus import stopwords

PICKLEFILENAME = '../stopwords.pickle'

class stopwords():
    def __init__(self):

        self.stopWordsDict = {}

        if not os.path.isfile(PICKLEFILENAME):
            nltk.download('stopwords')
            stop_words = set(stopwords.words('english'))

            # for word in stop_words:
            #     self.stopWordsDict[word]=True

    def writePickle(self):
        with open(PICKLEFILENAME, 'wb') as f:
            pickle.dump(self.stopWordsDict, f, pickle.HIGHEST_PROTOCOL)


    def showStopWords(self):
        pass
            ######
            #pickle 저장
            ######
        