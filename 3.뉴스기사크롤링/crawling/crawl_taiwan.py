import requests
import re
import pandas as pd
import csv
import os
import time
import random
import sys
import json
import logging
from datetime import datetime
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import selenium

# Logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log/taiwan_crawl_errors.log"),
        logging.StreamHandler(),
    ],
)


def start_driver():
    # Selenium WebDriver configuration
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=Chrome/126.0.6478.127")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )
    return driver


def crawl_category(
    driver, url, category_name, max_pages=1, max_articles=1
):  # Check page and article count

    Press = []
    Reporter = []
    Category = []
    SubmissionDate = []
    SubmissionTime = []
    UpdateDate = []
    UpdateTime = []
    titles = []
    articles = []
    Size = []
    urls = []

    for p in range(1, max_pages + 1):
        page = f"{url}&page={p}"
        driver.get(page)

        print(f"Starting to crawl page {p}")

        time.sleep(2)

        # Crawl all articles
        for i in range(1, max_articles + 1):
            try:
                # Press
                Press.append("Taiwan Today")

                # Reporter
                Reporter.append(None)

                # Category
                Category.append(category_name.lower())

                # Submission Date
                submission_time_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"/html/body/div/div[2]/div[3]/ul/li[{i}]/a/div[2]")
                    )
                )

                submission_date_text = submission_time_element.text
                try:
                    submission_datetime = datetime.strptime(
                        submission_date_text, "%B %d, %Y"
                    )
                    submission_date = submission_datetime.strftime("%Y-%m-%d")
                    submission_time = submission_datetime.strftime("%H:%M")
                except ValueError:
                    submission_date = None
                    submission_time = None
                SubmissionDate.append(submission_date)
                SubmissionTime.append(submission_time)

                # Last Edited Date
                UpdateDate.append(None)

                # Last Edited Time
                UpdateTime.append(None)

                # Article Title
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"/html/body/div/div[2]/div[3]/ul/li[{i}]/a/h3")
                    )
                )
                title = title_element.text
                titles.append(title)

                # Click on the page
                pg = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            f"body > div > div.ui_main.news > div.list.pic > ul > li:nth-child({i}) > a",
                        )
                    )
                )
                pg.click()

                time.sleep(2)

                # Identify the div tag containing the article content
                main_content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "maincontent"))
                )

                # Extract all text contained in the article and add it to the list
                article_content = main_content.text
                articles.append(article_content)

                print(submission_date, submission_time, title, article_content)

                # Size
                Size.append(len(article_content) if article_content else None)

                # URL
                urls.append(driver.current_url)

                # Go back
                driver.back()

                print(f"Completed crawling article {i}")
            except Exception as e:
                logging.error(f"Error on page {p}, article {i}: {e}")

        print(f"Completed crawling page {p}")

    # Create DataFrame
    df = pd.DataFrame(
        {
            "Country": "Taiwan",
            "Press": Press,
            "Reporter": Reporter,
            "Category": Category,
            "SubmissionDate": SubmissionDate,
            "SubmissionTime": SubmissionTime,
            "UpdateDate": UpdateDate,
            "UpdateTime": UpdateTime,
            "Title": titles,
            "Article": articles,
            "Size": Size,
            "url": urls,
        }
    )

    return df


def crawl_taiwan():
    driver = start_driver()  # Start ChromeDriver once

    # URLs and names of each category
    categories = {
        "Politics": "https://www.taiwantoday.tw/list_tt.php?unit=2&unitname=Politics-Top-News",
        "Economy": "https://www.taiwantoday.tw/list_tt.php?unit=6&unitname=Economics-Top-News",
        "Society": "https://www.taiwantoday.tw/list_tt.php?unit=10&unitname=Society-Top-News",
        "Environment": "https://www.taiwantoday.tw/list_tt.php?unit=15&unitname=Environment-Top-News",
        "Culture": "https://www.taiwantoday.tw/list_tt.php?unit=18&unitname=Culture-Top-News",
    }

    if not os.path.exists("Taiwan"):
        os.makedirs("Taiwan")

    # Crawl each category
    dataframes = []
    for category_name, url in categories.items():
        df = crawl_category(
            driver, url, category_name, max_pages=1, max_articles=2
        )  # Set the number of pages and articles needed
        df.to_csv(
            os.path.join("Taiwan", f"Taiwan_{category_name}.csv"),
            index=False,
            encoding="utf-8-sig",
        )
        dataframes.append(df)
        print(f"Completed {category_name}.")

    driver.quit()  # Close driver after all crawling is complete

    # Merge DataFrames
    taiwan_df = pd.concat(dataframes, ignore_index=True)

    # Preprocessing
    taiwan_df["SubmissionDate"] = taiwan_df["SubmissionDate"].fillna("1970-01-01")
    taiwan_df["SubmissionTime"] = taiwan_df["SubmissionTime"].fillna("00:00")
    taiwan_df["UpdateDate"] = taiwan_df["UpdateDate"].fillna("1970-01-01")
    taiwan_df["UpdateTime"] = taiwan_df["UpdateTime"].fillna("00:00")
    taiwan_df["Size"] = taiwan_df["Size"].fillna(0).astype(int)
    taiwan_df["Reporter"] = taiwan_df["Reporter"].fillna("Unknown")

    taiwan_df.to_csv(
        os.path.join("Taiwan", "Taiwan_articles.csv"), index=False, encoding="utf-8-sig"
    )

    taiwan_articles = os.path.join("Taiwan", "Taiwan_articles.csv")
    return taiwan_articles


if __name__ == "__main__":
    # Execute the crawl_taiwan function
    df = crawl_taiwan()

    print("Crawling and preprocessing completed")

    # Print file save location
    current_dir = os.path.join(os.getcwd(), "Taiwan")
    print(f"Files saved in: {current_dir}")
