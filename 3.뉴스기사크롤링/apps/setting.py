import os
import nltk
import gzip
import pickle
import streamlit as st
from nltk.corpus import stopwords

PICKLEFILENAME = 'stopwords.pickle'


class app():

    def __init__(self):
        st.title('StopWords Setting')
        # sideBar = st.sidebar
        # self.tabPrint, self.tabAdd, self.tabDel = st.tabs(['StopWords','Add','Delete'])

        self.showStopWords()

        isSave = st.button("Save", type="primary")
        if isSave:
            self.saveStopWords()
            self.showStopWords()

    def saveStopWords(self):
        print('Saving stop words')
        print(self.de)

        with open(PICKLEFILENAME, 'wb') as f:
            pickle.dump(self.de, f)

    def showStopWords(self):
        print(os.getcwd())
        if not os.path.isfile(PICKLEFILENAME):
            print('Can not find stopwords file. Downloading start.')
            nltk.download('stopwords')
            self.stop_words = set(stopwords.words('english'))

            self.de = st.data_editor(self.stop_words, num_rows='dynamic',height=380)
            self.saveStopWords()
        else :
            with open(PICKLEFILENAME, 'rb') as f:
                print('Read stopwords from pickle file')
                self.stop_words = pickle.load(f)

                self.de = st.data_editor(self.stop_words, num_rows='dynamic',height=380)

        return self.de



if __name__ == '__main__':
    app()