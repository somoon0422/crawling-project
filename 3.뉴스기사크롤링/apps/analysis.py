# import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import networkx as nx
# from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# from sklearn.decomposition import LatentDirichletAllocation
# from sklearn.model_selection import train_test_split
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.metrics import classification_report
# from wordcloud import WordCloud
# from nltk.corpus import stopwords
# from textblob import TextBlob
# import base64
# import nltk
# import spacy
# import os
# import pickle
# import platform
# import subprocess
# import matplotlib.font_manager as fm

# PICKLEFILENAME = 'stopwords.pickle'

# # Set Korean font in Matplotlib
# plt.rcParams["font.family"] = "NanumGothic"

# def install_nanum_font():
#     if platform.system() == "Windows":
#         font_path = "C:/Windows/Fonts/NanumGothic.ttf"
#         if not os.path.exists(font_path):
#             url = "https://github.com/naver/nanumfont/blob/master/NanumGothic.ttf?raw=true"
#             font_path = "NanumGothic.ttf"
#             subprocess.run(["curl", "-Lo", font_path, url])
#             font_install_cmd = f"copy {font_path} C:\\Windows\\Fonts"
#             subprocess.run(["cmd", "/c", font_install_cmd])
#     elif platform.system() == "Darwin":
#         font_path = "/Library/Fonts/NanumGothic.ttf"
#         if not os.path.exists(font_path):
#             url = "https://github.com/naver/nanumfont/blob/master/NanumGothic.ttf?raw=true"
#             font_path = "NanumGothic.ttf"
#             subprocess.run(["curl", "-Lo", font_path, url])
#             font_install_cmd = f"cp {font_path} /Library/Fonts"
#             subprocess.run(["sh", "-c", font_install_cmd])
#     elif platform.system() == "Linux":
#         font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
#         if not os.path.exists(font_path):
#             url = "https://github.com/naver/nanumfont/blob/master/NanumGothic.ttf?raw=true"
#             font_path = "NanumGothic.ttf"
#             subprocess.run(["curl", "-Lo", font_path, url])
#             font_install_cmd = f"sudo cp {font_path} /usr/share/fonts/truetype/nanum/"
#             subprocess.run(["sh", "-c", font_install_cmd])
#             subprocess.run(["fc-cache", "-fv"])

#     # Verify the font installation
#     font_dirs = fm.findSystemFonts(fontpaths=None, fontext="ttf")
#     if any("NanumGothic" in font for font in font_dirs):
#         print("NanumGothic font installed successfully.")
#     else:
#         print("NanumGothic font installation failed.")

# def set_mpl_font():
#     # Set Matplotlib to use NanumGothic
#     plt.rcParams["font.family"] = "NanumGothic"
#     print("Matplotlib is set to use NanumGothic font.")

# install_nanum_font()
# set_mpl_font()

# PICKLEFILENAME = 'stopwords.pickle'

# def showStopWords():
#     print(os.getcwd())
#     if not os.path.isfile(PICKLEFILENAME):
#         print('Cannot find stopwords file. Downloading start.')
#         nltk.download('stopwords')
#         stop_words = set(stopwords.words('english'))

#         stop_words = st.data_editor(stop_words, num_rows='dynamic', height=380)
        
#     else:
#         with open(PICKLEFILENAME, 'rb') as f:
#             print('Read stopwords from pickle file')
#             stop_words = pickle.load(f)
            
#     return stop_words

# def remove_stopwords(text, stop_words):
#     words = text.split()
#     filtered_words = [word for word in words if word.lower() not in stop_words]
#     return " ".join(filtered_words)

# def parse_date(date_string):
#     if pd.isna(date_string) or date_string == 0:
#         return None

#     supported_formats = ["%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d%H%M%S"]
#     for fmt in supported_formats:
#         try:
#             return pd.to_datetime(date_string, format=fmt)
#         except ValueError:
#             continue
#     return None

# def get_table_download_link(df):
#     csv = df.to_csv(index=False)
#     b64 = base64.b64encode(csv.encode()).decode()
#     href = f'<a href="data:file/csv;base64,{b64}" download="news_data.csv">Download Data</a>'
#     return href

# def app():
#     st.title("News Article Data Analysis Dashboard")

#     uploaded_file = st.file_uploader("Please upload your news article data file (CSV format)")

#     if uploaded_file is not None:
#         try:
#             df = pd.read_csv(uploaded_file)
#             if df.empty:
#                 st.error("The uploaded file is empty. Please upload a valid CSV file.")
#                 return
#         except Exception as e:
#             st.error(f"An error occurred while reading the file: {str(e)}")
#             return

#         # Check unique values in the Country column
#         st.write("Unique countries in the dataset:", df["Country"].unique())

#         date_columns = ["SubmissionDate", "UpdateDate"]
#         valid_date_column = None
#         for col in date_columns:
#             if col in df.columns:
#                 valid_date_column = col
#                 break

#         if valid_date_column is None:
#             st.error("SubmissionDate or UpdateDate column is required.")
#             return

#         try:
#             df["Date"] = df.apply(
#                 lambda row: parse_date(row[valid_date_column]), axis=1
#             )
#             df["Date"] = df["Date"].fillna(pd.NaT)
#         except Exception as e:
#             st.error(f"An error occurred while processing date data: {str(e)}")
#             return

#         # Display the number of NaT values
#         st.write("Number of NaT values in Date column:", df["Date"].isna().sum())

#         min_date = df["Date"].min()
#         max_date = df["Date"].max()

#         start_date = st.date_input("Start Date", min_value=min_date, value=min_date)
#         end_date = st.date_input("End Date", max_value=max_date, value=max_date)

#         if start_date > end_date:
#             st.error("End date must be after the start date.")
#             return

#         # Convert start_date and end_date to datetime
#         start_date = pd.to_datetime(start_date)
#         end_date = pd.to_datetime(end_date)

#         # Include rows with missing dates
#         mask = ((df["Date"] >= start_date) & (df["Date"] <= end_date)) | (
#             df["Date"].isna()
#         )
#         filtered_df = df[mask]

#         st.write("Filtered Data:", filtered_df)  # Display filtered data for verification

#         analysis_type = st.radio("Select Analysis Type", ["Quick Analysis", "In-depth Analysis"])

#         keyword = st.text_input("Enter a keyword")

#         stop_words = showStopWords()
#         print('Retrieved stopwords')
#         print(stop_words)

#         # Modified code for visualization
#         if analysis_type == "Quick Analysis":
#             st.header("Quick Analysis Results")
#             if keyword:
#                 filtered_df["Keyword Frequency"] = filtered_df["Title"].apply(
#                     lambda x: (
#                         str(x).lower().count(keyword.lower())
#                         if isinstance(x, str)
#                         else 0
#                     )
#                 )
#                 country_keyword_freq = (
#                     filtered_df.groupby("Country")["Keyword Frequency"]
#                     .sum()
#                     .reset_index()
#                 )
#                 st.bar_chart(country_keyword_freq.set_index("Country"))

#         elif analysis_type == "In-depth Analysis":
#             st.header("In-depth Analysis Results")
#             if keyword:
#                 filtered_df["Keyword Frequency"] = filtered_df["Article"].apply(
#                     lambda x: (
#                         str(x).lower().count(keyword.lower())
#                         if isinstance(x, str)
#                         else 0
#                     )
#                 )
#                 country_keyword_freq = (
#                     filtered_df.groupby("Country")["Keyword Frequency"]
#                     .sum()
#                     .reset_index()
#                 )
#                 st.bar_chart(country_keyword_freq.set_index("Country"))

#             filtered_df["polarity"] = filtered_df["Article"].apply(
#                 lambda x: TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else None
#             )

#             country_options = ["All"] + list(filtered_df["Country"].unique())
#             selected_country = st.selectbox("Select a country", country_options)

#             if selected_country != "All":
#                 country_data = filtered_df[filtered_df["Country"] == selected_country]
#             else:
#                 country_data = filtered_df.copy()

#             st.header(f"{selected_country} Data Summary")
#             st.write(f"Total number of articles: {len(country_data)}")

#             country_data["text"] = country_data["Title"] + " " + country_data["Article"]
#             country_data = country_data.dropna(subset=["text"])
#             country_data = country_data[country_data["text"].str.strip() != ""]
#             country_data["text"] = country_data["text"].apply(
#                 lambda x: remove_stopwords(str(x), stop_words)
#             )

#             st.header("Analysis Results")
#             options = [
#                 "Frequency Analysis",
#                 "Sentiment Analysis",
#                 "Word Cloud",
#                 "Topic Modeling",
#                 "Sentiment Classification",
#                 "Topic Classification",
#                 "Network Analysis",
#             ]
#             analysis_choice = st.selectbox("Select Analysis Type", options)

#             # Word Frequency Analysis
#             if analysis_choice == "Frequency Analysis":
#                 st.header("Word Frequency Analysis")
#                 vectorizer = CountVectorizer(stop_words=stop_words)
#                 X = vectorizer.fit_transform(country_data["text"])
#                 word_freq = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
#                 word_freq_sum = word_freq.sum().sort_values(ascending=False)
#                 st.bar_chart(word_freq_sum.head(20))

#             # Sentiment Analysis
#             elif analysis_choice == "Sentiment Analysis":
#                 st.header("Sentiment Analysis Results")
#                 sentiment_counts = country_data["polarity"].value_counts()
#                 st.bar_chart(sentiment_counts)

#             # Word Cloud
#             elif analysis_choice == "Word Cloud":
#                 st.header("Word Cloud")
#                 wordcloud = WordCloud(width=800, height=400, background_color="white", colormap='plasma').generate(" ".join(country_data["text"]))
#                 plt.figure(figsize=(10, 5))
#                 plt.imshow(wordcloud, interpolation='bilinear')
#                 plt.axis('off')
#                 st.pyplot(plt)

#             # Topic Modeling
#             elif analysis_choice == "Topic Modeling":
#                 st.header("Topic Modeling Results")
#                 vectorizer = CountVectorizer(stop_words=stop_words)
#                 X = vectorizer.fit_transform(country_data["text"])
#                 lda = LatentDirichletAllocation(n_components=5, random_state=42)
#                 lda.fit(X)

#                 topic_words = []
#                 for index, topic in enumerate(lda.components_):
#                     words = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-10:]]
#                     topic_words.append(f"Topic {index+1}: {', '.join(words)}")

#                 st.write("\n".join(topic_words))

#             # Sentiment Classification
#             elif analysis_choice == "Sentiment Classification":
#                 st.header("Sentiment Classification Results")
#                 X_train, X_test, y_train, y_test = train_test_split(
#                     country_data["text"],
#                     country_data["polarity"].apply(lambda x: 1 if x > 0 else (0 if x == 0 else -1)),
#                     test_size=0.2,
#                     random_state=42,
#                 )

#                 vectorizer = TfidfVectorizer(stop_words=stop_words)
#                 X_train_vectorized = vectorizer.fit_transform(X_train)
#                 model = MultinomialNB()
#                 model.fit(X_train_vectorized, y_train)

#                 X_test_vectorized = vectorizer.transform(X_test)
#                 y_pred = model.predict(X_test_vectorized)

#                 st.write(classification_report(y_test, y_pred))

#             # Topic Classification
#             elif analysis_choice == "Topic Classification":
#                 st.header("Topic Classification Results")
#                 topic_labels = st.text_input("Enter topic labels (comma separated)").split(",")
#                 topic_labels = [label.strip() for label in topic_labels]

#                 if len(topic_labels) > 0:
#                     X_train, X_test, y_train, y_test = train_test_split(
#                         country_data["text"],
#                         country_data["Country"],
#                         test_size=0.2,
#                         random_state=42,
#                     )

#                     vectorizer = TfidfVectorizer(stop_words=stop_words)
#                     X_train_vectorized = vectorizer.fit_transform(X_train)
#                     model = MultinomialNB()
#                     model.fit(X_train_vectorized, y_train)

#                     X_test_vectorized = vectorizer.transform(X_test)
#                     y_pred = model.predict(X_test_vectorized)

#                     st.write(classification_report(y_test, y_pred))

#             # Network Analysis
#             elif analysis_choice == "Network Analysis":
#                 st.header("Network Analysis Results")
#                 G = nx.Graph()
#                 for index, row in country_data.iterrows():
#                     text = row["text"]
#                     words = text.split()
#                     for i in range(len(words)):
#                         for j in range(i + 1, len(words)):
#                             G.add_edge(words[i], words[j])
#                 plt.figure(figsize=(12, 12))
#                 pos = nx.spring_layout(G)
#                 nx.draw(G, pos, with_labels=True, node_size=50, font_size=8)
#                 st.pyplot(plt)

#     st.markdown(get_table_download_link(filtered_df), unsafe_allow_html=True)

# if __name__ == "__main__":
#     app()


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
from wordcloud import WordCloud
from nltk.corpus import stopwords
from textblob import TextBlob
import base64
import nltk
import spacy
import os
import pickle
import platform
import subprocess
import matplotlib.font_manager as fm

PICKLEFILENAME = 'stopwords.pickle'

# Set Korean font in Matplotlib
plt.rcParams["font.family"] = "NanumGothic"

def install_nanum_font():
    if platform.system() == "Windows":
        font_path = "C:/Windows/Fonts/NanumGothic.ttf"
        if not os.path.exists(font_path):
            url = "https://github.com/naver/nanumfont/blob/master/NanumGothic.ttf?raw=true"
            font_path = "NanumGothic.ttf"
            subprocess.run(["curl", "-Lo", font_path, url])
            font_install_cmd = f"copy {font_path} C:\\Windows\\Fonts"
            subprocess.run(["cmd", "/c", font_install_cmd])
    elif platform.system() == "Darwin":
        font_path = "/Library/Fonts/NanumGothic.ttf"
        if not os.path.exists(font_path):
            url = "https://github.com/naver/nanumfont/blob/master/NanumGothic.ttf?raw=true"
            font_path = "NanumGothic.ttf"
            subprocess.run(["curl", "-Lo", font_path, url])
            font_install_cmd = f"cp {font_path} /Library/Fonts"
            subprocess.run(["sh", "-c", font_install_cmd])
    elif platform.system() == "Linux":
        font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
        if not os.path.exists(font_path):
            url = "https://github.com/naver/nanumfont/blob/master/NanumGothic.ttf?raw=true"
            font_path = "NanumGothic.ttf"
            subprocess.run(["curl", "-Lo", font_path, url])
            font_install_cmd = f"sudo cp {font_path} /usr/share/fonts/truetype/nanum/"
            subprocess.run(["sh", "-c", font_install_cmd])
            subprocess.run(["fc-cache", "-fv"])

    # Verify the font installation
    font_dirs = fm.findSystemFonts(fontpaths=None, fontext="ttf")
    if any("NanumGothic" in font for font in font_dirs):
        print("NanumGothic font installed successfully.")
    else:
        print("NanumGothic font installation failed.")

def set_mpl_font():
    # Set Matplotlib to use NanumGothic
    plt.rcParams["font.family"] = "NanumGothic"
    print("Matplotlib is set to use NanumGothic font.")

install_nanum_font()
set_mpl_font()

PICKLEFILENAME = 'stopwords.pickle'

def showStopWords():
    print(os.getcwd())
    if not os.path.isfile(PICKLEFILENAME):
        print('Cannot find stopwords file. Downloading start.')
        nltk.download('stopwords')
        stop_words = list(stopwords.words('english'))

        stop_words = st.text_area("Stop Words", "\n".join(stop_words), height=380)
        stop_words = set(stop_words.split("\n"))
        
    else:
        with open(PICKLEFILENAME, 'rb') as f:
            print('Read stopwords from pickle file')
            stop_words = pickle.load(f)
            
    return stop_words

def remove_stopwords(text, stop_words):
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return " ".join(filtered_words)

def parse_date(date_string):
    if pd.isna(date_string) or date_string == 0:
        return None

    supported_formats = ["%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d%H%M%S"]
    for fmt in supported_formats:
        try:
            return pd.to_datetime(date_string, format=fmt)
        except ValueError:
            continue
    return None

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="news_data.csv">Download Data</a>'
    return href

def app():
    st.title("News Article Data Analysis Dashboard")

    uploaded_file = st.file_uploader("Please upload your news article data file (CSV format)")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            if df.empty:
                st.error("The uploaded file is empty. Please upload a valid CSV file.")
                return
        except Exception as e:
            st.error(f"An error occurred while reading the file: {str(e)}")
            return

        # Check unique values in the Country column
        st.write("Unique countries in the dataset:", df["Country"].unique())

        date_columns = ["SubmissionDate", "UpdateDate"]
        valid_date_column = None
        for col in date_columns:
            if col in df.columns:
                valid_date_column = col
                break

        if valid_date_column is None:
            st.error("SubmissionDate or UpdateDate column is required.")
            return

        try:
            df["Date"] = df.apply(
                lambda row: parse_date(row[valid_date_column]), axis=1
            )
            df["Date"] = df["Date"].fillna(pd.NaT)
        except Exception as e:
            st.error(f"An error occurred while processing date data: {str(e)}")
            return

        # Display the number of NaT values
        st.write("Number of NaT values in Date column:", df["Date"].isna().sum())

        min_date = df["Date"].min()
        max_date = df["Date"].max()

        start_date = st.date_input("Start Date", min_value=min_date, value=min_date)
        end_date = st.date_input("End Date", max_value=max_date, value=max_date)

        if start_date > end_date:
            st.error("End date must be after the start date.")
            return

        # Convert start_date and end_date to datetime
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Include rows with missing dates
        mask = ((df["Date"] >= start_date) & (df["Date"] <= end_date)) | (
            df["Date"].isna()
        )
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning("No data available for the selected date range.")
            return

        st.write("Filtered Data:", filtered_df)  # Display filtered data for verification

        analysis_type = st.radio("Select Analysis Type", ["Quick Analysis", "In-depth Analysis"])

        keyword = st.text_input("Enter a keyword")

        stop_words = showStopWords()
        print('Retrieved stopwords')
        print(stop_words)

        # Modified code for visualization
        if analysis_type == "Quick Analysis":
            st.header("Quick Analysis Results")
            if keyword:
                filtered_df["Keyword Frequency"] = filtered_df["Title"].apply(
                    lambda x: (
                        str(x).lower().count(keyword.lower())
                        if isinstance(x, str)
                        else 0
                    )
                )
                country_keyword_freq = (
                    filtered_df.groupby("Country")["Keyword Frequency"]
                    .sum()
                    .reset_index()
                )
                st.bar_chart(country_keyword_freq.set_index("Country"))

        elif analysis_type == "In-depth Analysis":
            st.header("In-depth Analysis Results")
            if keyword:
                filtered_df["Keyword Frequency"] = filtered_df["Article"].apply(
                    lambda x: (
                        str(x).lower().count(keyword.lower())
                        if isinstance(x, str)
                        else 0
                    )
                )
                country_keyword_freq = (
                    filtered_df.groupby("Country")["Keyword Frequency"]
                    .sum()
                    .reset_index()
                )
                st.bar_chart(country_keyword_freq.set_index("Country"))

            filtered_df["polarity"] = filtered_df["Article"].apply(
                lambda x: TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else None
            )

            country_options = ["All"] + list(filtered_df["Country"].unique())
            selected_country = st.selectbox("Select a country", country_options)

            if selected_country != "All":
                country_data = filtered_df[filtered_df["Country"] == selected_country]
            else:
                country_data = filtered_df.copy()

            st.header(f"{selected_country} Data Summary")
            st.write(f"Total number of articles: {len(country_data)}")

            country_data["text"] = country_data["Title"] + " " + country_data["Article"]
            country_data = country_data.dropna(subset=["text"])
            country_data = country_data[country_data["text"].str.strip() != ""]
            country_data["text"] = country_data["text"].apply(
                lambda x: remove_stopwords(str(x), stop_words)
            )

            st.header("Analysis Results")
            options = [
                "Frequency Analysis",
                "Sentiment Analysis",
                "Word Cloud",
                "Topic Modeling",
                "Sentiment Classification",
                "Topic Classification",
                "TF-IDF Analysis",
                "Word Frequency Distribution",
                "Heatmap",
                "Scatter Plot",
                "Network Analysis"
            ]
            selected_options = st.multiselect("Select the analysis you want", options)

            if "Frequency Analysis" in selected_options:
                st.subheader("Frequency Analysis")
                vectorizer = CountVectorizer(stop_words=list(stop_words))
                word_count = vectorizer.fit_transform(country_data["text"])
                word_count_sum = word_count.sum(axis=0)
                words_freq = [
                    (word, word_count_sum[0, idx])
                    for word, idx in vectorizer.vocabulary_.items()
                ]
                words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
                words_df = pd.DataFrame(words_freq, columns=["Word", "Frequency"])
                st.write(words_df.head(10))

            if "Sentiment Analysis" in selected_options:
                st.subheader("Sentiment Analysis")
                country_data["polarity"] = country_data["text"].apply(
                    lambda x: TextBlob(str(x)).sentiment.polarity
                )
                st.write(country_data[["Date", "polarity"]].describe())
                plt.figure(figsize=(10, 6))
                plt.hist(country_data["polarity"], bins=20)
                plt.xlabel("Polarity")
                plt.ylabel("Frequency")
                st.pyplot(plt)

            if "Word Cloud" in selected_options:
                st.subheader("Word Cloud")
                text = " ".join(country_data["text"])
                wordcloud = WordCloud(
                    stopwords=stop_words, background_color="white"
                ).generate(text)
                plt.figure(figsize=(10, 6))
                plt.imshow(wordcloud, interpolation="bilinear")
                plt.axis("off")
                st.pyplot(plt)

            if "Topic Modeling" in selected_options:
                st.subheader("Topic Modeling")
                vectorizer = CountVectorizer(stop_words=list(stop_words))
                dtm = vectorizer.fit_transform(country_data["text"])
                lda = LatentDirichletAllocation(n_components=5, random_state=0)
                lda.fit(dtm)
                for i, topic in enumerate(lda.components_):
                    st.write(f"Topic {i}:")
                    st.write(
                        [
                            vectorizer.get_feature_names_out()[i]
                            for i in topic.argsort()[-10:]
                        ]
                    )

            if "Sentiment Classification" in selected_options:
                st.subheader("Sentiment Classification")
                country_data["polarity"] = country_data["text"].apply(
                    lambda x: (
                        TextBlob(str(x)).sentiment.polarity if pd.notnull(x) else None
                    )
                )
                country_data = country_data.dropna(subset=["polarity"])
                country_data["label"] = (country_data["polarity"] > 0).astype(int)
                X_train, X_test, y_train, y_test = train_test_split(
                    country_data["text"],
                    country_data["label"],
                    test_size=0.2,
                    random_state=0,
                )
                vectorizer = TfidfVectorizer(stop_words=list(stop_words))
                X_train_vec = vectorizer.fit_transform(X_train)
                X_test_vec = vectorizer.transform(X_test)
                clf = MultinomialNB()
                clf.fit(X_train_vec, y_train)
                y_pred = clf.predict(X_test_vec)
                st.write("### Sentiment Classification Performance Metrics")
                report = classification_report(
                    y_test, y_pred, target_names=["Negative", "Positive"], output_dict=True
                )
                report_df = pd.DataFrame(report).transpose()
                st.dataframe(report_df)
                st.write(f"Accuracy: {report['accuracy']:.2f}")

            if "Topic Classification" in selected_options:
                st.subheader("Topic Classification")
                if "Category" in country_data.columns:
                    country_data = country_data.dropna(subset=["Category"])
                    X_train, X_test, y_train, y_test = train_test_split(
                        country_data["text"],
                        country_data["Category"],
                        test_size=0.2,
                        random_state=0,
                    )
                    vectorizer = TfidfVectorizer(stop_words=list(stop_words))
                    X_train_vec = vectorizer.fit_transform(X_train)
                    X_test_vec = vectorizer.transform(X_test)
                    clf = MultinomialNB()
                    clf.fit(X_train_vec, y_train)
                    y_pred = clf.predict(X_test_vec)
                    st.write("### Topic Classification Performance Metrics")
                    report = classification_report(y_test, y_pred, output_dict=True)
                    report_df = pd.DataFrame(report).transpose()
                    st.dataframe(report_df)
                    st.write(f"Accuracy: {report['accuracy']:.2f}")
                else:
                    st.error("The dataset does not contain a 'Category' column.")

            if "TF-IDF Analysis" in selected_options:
                st.subheader("TF-IDF Analysis")
                vectorizer = TfidfVectorizer(stop_words=list(stop_words))
                X = vectorizer.fit_transform(country_data["text"])
                tfidf_df = pd.DataFrame(
                    X.toarray(), columns=vectorizer.get_feature_names_out()
                )
                st.write(tfidf_df)

            if "Word Frequency Distribution" in selected_options:
                st.subheader("Word Frequency Distribution")
                vectorizer = CountVectorizer(stop_words=list(stop_words))
                word_count = vectorizer.fit_transform(country_data["text"])
                word_count_sum = word_count.sum(axis=0)
                words_freq = [
                    (word, word_count_sum[0, idx])
                    for word, idx in vectorizer.vocabulary_.items()
                ]
                words_freq = sorted(words_freq, key=lambda x: x[1], reverse=True)
                words_df = pd.DataFrame(words_freq, columns=["Word", "Frequency"])
                st.write(words_df)

            if "Heatmap" in selected_options:
                st.subheader("Heatmap")
                keyword_input = st.text_input(
                    "Enter the keywords to display on the heatmap (you can enter multiple keywords separated by commas :)"
                )
                if keyword_input:
                    # 입력된 키워드를 쉼표로 구분하여 리스트로 변환
                    top_keywords = [
                        kw.strip().lower() for kw in keyword_input.split(",")
                    ]

                    # 각 기사의 입력된 키워드 빈도 계산
                    for word in top_keywords:
                        filtered_df[word] = filtered_df["Article"].apply(
                            lambda x: (
                                str(x).lower().count(word) if isinstance(x, str) else 0
                            )
                        )

                    # 히트맵 데이터 생성
                    heatmap_data = filtered_df.groupby("Country")[top_keywords].sum()

                    plt.figure(figsize=(10, 6))
                    sns.heatmap(
                        heatmap_data,
                        annot=True,
                        fmt=".1f",
                        cmap="YlGnBu",
                        cbar_kws={"label": "Frequency"},
                    )
                    plt.xlabel("Keywords")
                    plt.ylabel("Country")
                    plt.title("Heatmap of Keywords by Country")
                    st.pyplot(plt)

            if "Scatter Plot" in selected_options:
                st.subheader("Scatter Plot")

                # spaCy 모델 로드
                nlp = spacy.load("en_core_web_sm")

                # 필요한 텍스트 분석 함수 정의
                def calculate_polarity(text):
                    return TextBlob(str(text)).sentiment.polarity

                def calculate_subjectivity(text):
                    return TextBlob(str(text)).sentiment.subjectivity

                def calculate_word_count(text):
                    return len(str(text).split())

                def calculate_named_entity_count(text):
                    return len([ent for ent in nlp(str(text)).ents])

                # 텍스트 분석 컬럼 추가
                filtered_df["Polarity"] = filtered_df["Article"].apply(
                    lambda x: calculate_polarity(x) if pd.notnull(x) else 0
                )
                filtered_df["Subjectivity"] = filtered_df["Article"].apply(
                    lambda x: calculate_subjectivity(x) if pd.notnull(x) else 0
                )
                filtered_df["Word Count"] = filtered_df["Article"].apply(
                    lambda x: calculate_word_count(x) if pd.notnull(x) else 0
                )
                filtered_df["Named Entity Count"] = filtered_df["Article"].apply(
                    lambda x: calculate_named_entity_count(x) if pd.notnull(x) else 0
                )

                # 키워드 설정 및 빈도수 컬럼 추가
                keyword = st.text_input("Enter a keyword", key="scatter_plot_keyword")
                if keyword:
                    filtered_df["Keyword Frequency"] = filtered_df["Article"].apply(
                        lambda x: (
                            str(x).lower().count(keyword.lower())
                            if isinstance(x, str)
                            else 0
                        )
                    )

                    # 산점도 옵션 선택
                    x_options = [
                        "Keyword Frequency",
                        "Word Count",
                        "Polarity",
                        "Subjectivity",
                        "Named Entity Count",
                    ]
                    y_options = [
                        "Keyword Frequency",
                        "Word Count",
                        "Polarity",
                        "Subjectivity",
                        "Named Entity Count",
                    ]

                    x_axis = st.selectbox("Select X-axis variable", x_options, index=0)
                    y_axis = st.selectbox("Select Y-axis variable", y_options, index=1)

                    # 산점도 생성
                    plt.figure(figsize=(10, 6))
                    sns.scatterplot(data=filtered_df, x=x_axis, y=y_axis, hue="Country")
                    plt.title(f"Scatter Plot of {x_axis} vs {y_axis}")
                    plt.xlabel(x_axis)
                    plt.ylabel(y_axis)
                    plt.legend(title="Country")
                    plt.grid(True)
                    st.pyplot(plt)
                else:
                    st.error("Please enter the keywords.")

            if "Network Analysis" in selected_options:
                st.subheader("Network Analysis")
                G = nx.Graph()
                for index, row in country_data.iterrows():
                    text = row["text"]
                    words = text.split()
                    for i in range(len(words)):
                        for j in range(i + 1, len(words)):
                            G.add_edge(words[i], words[j])
                plt.figure(figsize=(12, 12))
                pos = nx.spring_layout(G)
                nx.draw(G, pos, with_labels=True, node_size=50, font_size=8)
                st.pyplot(plt)

        st.markdown(get_table_download_link(filtered_df), unsafe_allow_html=True)

if __name__ == "__main__":
    app()


