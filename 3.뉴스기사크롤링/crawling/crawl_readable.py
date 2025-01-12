import requests
import re
import pandas as pd
import csv
import os
import time
import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def start_driver():
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


# Logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log/readable_crawl_errors.log"),
        logging.StreamHandler(),
    ],
)


def get_last_page(driver, url):
    driver.get(url)
    time.sleep(random.randint(1, 3))
    try:
        pagination_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "page-numbers"))
        )
        last_page_element = pagination_elements[-2]
        last_page_number = int(last_page_element.text)
        return last_page_number
    except Exception as e:
        logging.error(f"Error getting last page number: {e}")
        return 1


def crawl_and_save_articles(driver, url, category_name, max_pages=1, max_articles=1):
    (
        Press,
        Reporter,
        Category,
        SubmissionDate,
        SubmissionTime,
        UpdateDate,
        UpdateTime,
        titles,
        articles,
        Size,
        urls,
    ) = ([] for _ in range(11))

    last_page = get_last_page(driver, url)
    print(f"Last page of category {category_name}: {last_page}")

    for i in range(1, max_pages + 1):
        if i == 1:
            page_url = f"{url}"
        else:
            page_url = f"{url}page/{i}/"

        driver.get(page_url)
        time.sleep(random.randint(1, 3))

        for j in range(1, max_articles + 1):
            try:
                article_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            "/html/body/div[2]/div[2]/div/div[2]/div/div/div/div[1]/div",
                        )
                    )
                )
                article_href = (
                    article_elements[j - 1]
                    .find_element(By.TAG_NAME, "a")
                    .get_attribute("href")
                )
                driver.get(article_href)
                time.sleep(1)

                Press.append("The Readable")
                reporter_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[2]/div[4]/div/div[1]/div/div[1]/div/div/div/div/span/ul/li/div[2]/div/a",
                        )
                    )
                )
                reporter = reporter_element.text.split()
                Reporter.append(reporter[1] + " " + reporter[0])
                Category.append(category_name)

                submission_date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div/div[1]/div",
                        )
                    )
                )
                submission_date_text = submission_date_element.text.split()
                month = submission_date_text[0].strip(".")
                day = submission_date_text[1].strip(",")
                year = submission_date_text[2]
                month_map = {
                    "Jan": "01",
                    "Feb": "02",
                    "Mar": "03",
                    "Apr": "04",
                    "May": "05",
                    "Jun": "06",
                    "Jul": "07",
                    "Aug": "08",
                    "Sep": "09",
                    "Oct": "10",
                    "Nov": "11",
                    "Dec": "12",
                }
                month_number = month_map.get(month, "01")
                submission_datetime = datetime.strptime(
                    f"{year}-{month_number}-{day}", "%Y-%m-%d"
                )
                submission_date = submission_datetime.strftime("%Y-%m-%d")
                submission_time = "00:00"  # Default time when no time information is available
                SubmissionDate.append(submission_date)
                SubmissionTime.append(submission_time)

                try:
                    update_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]")
                        )
                    )
                    if "Updated" in update_element.text:
                        update_text = update_element.text.split()
                        month = update_text[1]
                        day = update_text[2].strip(",")
                        year = update_text[3]
                        month_number = month_map.get(month, "01")
                        update_datetime = datetime.strptime(
                            f"{year}-{month_number}-{day}", "%Y-%m-%d"
                        )
                        update_date = update_datetime.strftime("%Y-%m-%d")
                        update_time = (
                            "00:00"  # Default time when no time information is available
                        )
                        UpdateDate.append(update_date)
                        UpdateTime.append(update_time)
                    else:
                        UpdateDate.append("")
                        UpdateTime.append("")
                except:
                    UpdateDate.append("")
                    UpdateTime.append("")

                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[2]/div[1]/div/div[1]/div/h1")
                    )
                )
                article_title = title_element.text.strip()
                titles.append(article_title)

                article_body_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[2]/div[2]/div/div[2]/div/div[3]")
                    )
                )
                article_paragraphs = article_body_element.find_elements(
                    By.TAG_NAME, "p"
                )
                article_content = " ".join([p.text.strip() for p in article_paragraphs])
                articles.append(article_content)

                Size.append(len(article_content))
                urls.append(driver.current_url)

                print(f"Completed article {j}")
                driver.back()
            except Exception as e:
                logging.error(f"Error processing article: {e}")
                driver.back()
                continue

        print(f"Completed page {i}")
        time.sleep(random.randint(1, 3))

    df = pd.DataFrame(
        {
            "Country": "SouthKorea",
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


def crawl_readable():
    driver = start_driver()
    categories = {
        "World": "https://thereadable.co/world/",
        "Privacy": "https://thereadable.co/privacy/",
        "Security": "https://thereadable.co/security/",
        "North Korea": "https://thereadable.co/north-korea/",
        "Business Wire": "https://thereadable.co/business-wire/",
    }

    if not os.path.exists("TheReadable"):
        os.makedirs("TheReadable")

    dataframes = []
    for category_name, url in categories.items():
        df = crawl_and_save_articles(
            driver, url, category_name, max_pages=1, max_articles=1
        )  # For testing
        df.to_csv(
            os.path.join("TheReadable", f"{category_name}_articles.csv"),
            index=False,
            encoding="utf-8-sig",
        )
        dataframes.append(df)
        print(f"Completed {category_name}.")

    driver.quit()
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_csv(
        os.path.join("TheReadable", "Readable_articles.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    readable_articles = os.path.join("TheReadable", "Readable_articles.csv")

    print("Crawling and merging files completed")

    current_dir = os.path.join(os.getcwd(), "TheReadable")
    print(f"Files saved in: {current_dir}")

    return readable_articles


if __name__ == "__main__":
    crawl_readable()
