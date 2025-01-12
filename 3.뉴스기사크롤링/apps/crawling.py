import logging
import os
import pandas as pd
import streamlit as st
from crawling.crawl_china import crawl_china
from crawling.crawl_vietnam import crawl_vietnam
from crawling.crawl_korea import crawl_korea
from crawling.crawl_usa import crawl_usa
from crawling.crawl_taiwan import crawl_taiwan
from crawling.crawl_readable import crawl_readable
import base64
from tqdm import tqdm


def app():
    st.title("Crawling App")

    countries = ["China", "Vietnam", "SouthKorea", "USA", "Taiwan", "Readable"]
    selected_country = st.selectbox("Select a country for crawling", countries)

    if "crawled_data" not in st.session_state:
        st.session_state.crawled_data = {country: None for country in countries}
    if "crawled_filename" not in st.session_state:
        st.session_state.crawled_filename = {country: None for country in countries}
    if "merged_filename" not in st.session_state:
        st.session_state.merged_filename = None
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = None

    if st.button("Crawling Start!"):
        st.write(f"Starting crawling for {selected_country}...")
        # try:
        if selected_country == "China":
            crawl_data = crawl_china()
            filename = "China_articles.csv"
        elif selected_country == "Vietnam":
            crawl_data = crawl_vietnam()
            filename = "Vietnam_articles.csv"
        elif selected_country == "SouthKorea":
            crawl_data = crawl_korea()
            filename = "SouthKorea_translated.csv"
        elif selected_country == "USA":
            crawl_data = crawl_usa()
            filename = "USA_articles.csv"
        elif selected_country == "Taiwan":
            crawl_data = crawl_taiwan()
            filename = "Taiwan_articles.csv"
        elif selected_country == "Readable":
            crawl_data = crawl_readable()
            filename = "Readable_articles.csv"

        if crawl_data is not None:
            st.session_state.crawled_data[selected_country] = pd.read_csv(crawl_data)
            st.session_state.crawled_filename[selected_country] = filename
            st.success("Crawling completed!")
        else:
            st.error(
                "Error occurred during crawling. Please check the logs for details."
            )
        # except Exception as e:
        #     logging.error(
        #         f"Error occurred during crawling for {selected_country}: {str(e)}"
        #     )
        #     st.error(
        #         "Error occurred during crawling. Please check the logs for details."
        #     )

    for country in countries:
        if st.session_state.crawled_data[country] is not None:
            with st.expander(f"Crawled Data: {country}"):
                st.write(st.session_state.crawled_data[country])
                st.markdown(
                    get_table_download_link(
                        st.session_state.crawled_data[country],
                        st.session_state.crawled_filename[country],
                    ),
                    unsafe_allow_html=True,
                )

    if st.button("Reset Upload"):
        st.session_state.uploaded_files = None
        st.experimental_rerun()

    uploaded_files = st.file_uploader(
        "Choose CSV files to merge",
        accept_multiple_files=True,
        type="csv",
        key="file_uploader",
    )
    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    if st.button("Merge Start!"):
        if st.session_state.uploaded_files:
            try:
                st.session_state.merged_filename = (
                    None  # Reset the merged filename to avoid accumulation
                )
                merged_filename = merge_selected_files(st.session_state.uploaded_files)
                if merged_filename:
                    st.session_state.merged_filename = merged_filename
                    st.success("Data merging completed!")
                    with st.expander("Merged Data Preview"):
                        merged_df = pd.read_csv(st.session_state.merged_filename)
                        st.write(merged_df)
                        st.markdown(
                            get_table_download_link(
                                merged_df, "Hawaii_all_articles.csv"
                            ),
                            unsafe_allow_html=True,
                        )
                else:
                    st.error("No data files found for merging.")
            except Exception as e:
                logging.error(f"Error occurred during data merging: {str(e)}")
                st.error(
                    "Error occurred during data merging. Please check the logs for details."
                )

    if st.session_state.merged_filename:
        with st.expander("Merged Data"):
            st.write(f"Merged file: {st.session_state.merged_filename}")
            st.markdown(
                get_table_download_link(
                    pd.read_csv(st.session_state.merged_filename),
                    "Hawaii_all_articles.csv",
                ),
                unsafe_allow_html=True,
            )


def get_table_download_link(df, filename):
    if isinstance(df, pd.DataFrame):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename} CSV File</a>'
        return href
    else:
        logging.error(f"Expected DataFrame, but got {type(df)}")
        return None


def merge_selected_files(uploaded_files):
    all_dataframes = []
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)

    for idx, uploaded_file in enumerate(tqdm(uploaded_files, desc="Merging Files")):
        df = pd.read_csv(uploaded_file)
        all_dataframes.append(df)
        progress_bar.progress((idx + 1) / total_files)

    if all_dataframes:
        merged_df = pd.concat(all_dataframes, ignore_index=True)
        merged_filename = "Hawaii_all_articles.csv"
        merged_df.to_csv(merged_filename, index=False, encoding="utf-8-sig")
        return merged_filename
    else:
        return None


if __name__ == "__main__":
    app()
