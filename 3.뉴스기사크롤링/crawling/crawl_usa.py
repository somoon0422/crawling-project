import time
import logging
import pandas as pd
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log/usa_crawl_errors.log"),
        logging.StreamHandler(),
    ],
)


def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Chrome/126.0.6478.127")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver


def extract_article_details(driver, article_url, category_name):
    data = {
        "Country": "USA",
        "Press": "CNN",
        "Reporter": "Unknown",
        "Category": category_name,
        "SubmissionDate": "",
        "SubmissionTime": "",
        "UpdateDate": "",
        "UpdateTime": "",
        "Title": "No Title",
        "Article": "",
        "Size": 0,
        "url": article_url,
    }

    driver.get(article_url)
    time.sleep(2)

    # Check if the article is a video article
    try:
        video_elem = driver.find_element(
            By.XPATH, '//div[contains(@class, "media__video")]'
        )
        if video_elem:
            print(f"Video article detected, skipping: {article_url}")
            return pd.DataFrame()  # Return an empty DataFrame if it's a video article
    except Exception:
        pass  # If not a video article, continue

    try:
        reporter_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//span[contains(@class, "byline__name")]')
            )
        )
        data["Reporter"] = reporter_elem.text
    except Exception as e:
        logging.error(f"Error fetching reporter: {e}")

    try:
        timestamp_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "body > div.layout__content-wrapper.layout-with-rail__content-wrapper > section.layout__top.layout-with-rail__top > div.headline.headline--has-lowertext > div.headline__footer > div.headline__sub-container > div > div.headline__byline-sub-text > div.timestamp.vossi-timestamp-primary-core-light",
                )
            )
        )
        timestamp_text = timestamp_elem.text.strip()

        if "Published" in timestamp_text:
            timestamp_text = timestamp_text.replace("Published", "").strip()
            pub_time_str, pub_date_str = timestamp_text.split(" EDT, ")
            pub_datetime = datetime.strptime(
                f"{pub_date_str} {pub_time_str}", "%a %B %d, %Y %I:%M %p"
            )
            data["SubmissionDate"] = pub_datetime.strftime("%Y-%m-%d")
            data["SubmissionTime"] = pub_datetime.strftime("%H:%M")
            print(data["SubmissionDate"], data["SubmissionTime"])
        elif "Updated" in timestamp_text:
            timestamp_text = timestamp_text.replace("Updated", "").strip()
            upd_time_str, upd_date_str = timestamp_text.split(" EDT, ")
            upd_datetime = datetime.strptime(
                f"{upd_date_str} {upd_time_str}", "%a %B %d, %Y %I:%M %p"
            )
            data["UpdateDate"] = upd_datetime.strftime("%Y-%m-%d")
            data["UpdateTime"] = upd_datetime.strftime("%H:%M")
            print(data["UpdateDate"], data["UpdateTime"])
    except Exception as e:
        logging.error(f"Error fetching date and time: {e}")

    try:
        title_elem = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//h1[contains(@class, "headline__text")]')
            )
        )
        data["Title"] = title_elem.text
    except Exception as e:
        logging.error(f"Error fetching title: {e}")

    try:
        article_body = driver.find_element(
            By.XPATH, '//div[contains(@class, "article__content")]'
        )
        paragraphs = article_body.find_elements(By.TAG_NAME, "p")
        article_text = " ".join([p.text for p in paragraphs])
        data["Article"] = article_text
        data["Size"] = len(paragraphs)
    except Exception as e:
        logging.error(f"Error fetching article: {e}")

    article_df = pd.DataFrame([data])
    print(article_df)  # Print the article DataFrame
    return article_df


def crawl_category(driver, category_url, category_name):
    driver.get(category_url)
    time.sleep(2)

    article_links = driver.find_elements(By.XPATH, '//a[contains(@href, "/2024/")]')
    unique_urls = set()
    all_articles = pd.DataFrame()

    for link in article_links[:2]:  # Example: only crawl 2 articles
        try:
            article_url = link.get_attribute("href")
            if article_url in unique_urls:
                continue
            unique_urls.add(article_url)
            driver.execute_script("window.open(arguments[0]);", article_url)
            driver.switch_to.window(driver.window_handles[1])

            article_df = extract_article_details(driver, article_url, category_name)
            all_articles = pd.concat([all_articles, article_df], ignore_index=True)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            logging.error(f"Error occurred while processing article: {e}")
            driver.switch_to.window(driver.window_handles[0])

    print(f"Finished scraping page for category: {category_name}")
    return all_articles


def crawl_usa():
    driver = start_driver()
    categories = {
        "World": "https://edition.cnn.com/world",
        "Politics": "https://edition.cnn.com/politics",
        "Entertainment": "https://edition.cnn.com/entertainment",
        "Business": "https://edition.cnn.com/business",
        "Sports": "https://edition.cnn.com/sport",
        "Paris Olympics 2024": "https://edition.cnn.com/sport/paris-olympics-2024",
    }

    all_articles = pd.DataFrame()
    for category_name, category_url in categories.items():
        category_df = crawl_category(driver, category_url, category_name)
        all_articles = pd.concat([all_articles, category_df], ignore_index=True)
        print(f"Finished scraping category: {category_name}")

    driver.quit()
    os.makedirs("USA", exist_ok=True)

    # Ensure all DataFrame columns have the same length
    columns_to_check = [
        "Country",
        "Press",
        "Reporter",
        "Category",
        "SubmissionDate",
        "SubmissionTime",
        "UpdateDate",
        "UpdateTime",
        "Title",
        "Article",
        "Size",
        "url",
    ]
    for col in columns_to_check:
        if col not in all_articles.columns:
            all_articles[col] = ""

    all_articles = all_articles[columns_to_check]  # Rearrange columns

    all_articles.to_csv("USA/USA_articles.csv", index=False, encoding="utf-8-sig")

    usa_articles = os.path.join("USA", "USA_articles.csv")
    return usa_articles


if __name__ == "__main__":
    df = crawl_usa()
    print(df)
