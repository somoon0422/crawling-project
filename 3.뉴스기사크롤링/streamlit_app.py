import streamlit as st
from apps import analysis, crawling, setting
# import apps.crawling
from apps import crawling
# from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
# load_dotenv()

# # Example: Get the CHROMEDRIVER_PATH environment variable
# chrome_driver_path = os.getenv("CHROMEDRIVER_PATH")

logger = logging.getLogger(__name__)

def main():
    st.title('🎡 Welcome to the Hawaii Project!')

    st.sidebar.title('Menu')
    page = st.sidebar.selectbox('Please choose', ('Main Page', 'Visualization', 'Crawling Page', 'Settings'))

    if page == 'Main Page':
        st.write(
            """
            #### This is a data crawling and analytics application.

            This application is a simple tool for data crawling and analysis.

            Please select the desired page from the sidebar on the left.
            """
        )

    elif page == 'Visualization':
        analysis.app()

    elif page == 'Crawling Page':
        crawling.app()

    elif page == 'Settings':
        setting.app()

if __name__ == '__main__':
    main()
