import os
import pandas as pd
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from mtranslate import translate
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


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


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log/korea_crawl_errors.log"),
        logging.StreamHandler(),
    ],
)


def extract_article_data(driver, url, category):
    driver.get(url)
    try:
        # Journalist name
        journalist = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="newsWriterCarousel01"]/div/div/div/div/div/a')
            )
        )
        reporter = journalist.text
    except Exception as e:
        logging.error(f"Error extracting journalist name from {url}: {str(e)}")
        reporter = "unknown"

    try:
        # Submission date and time
        submission_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "newsUpdateTime01"))
        )
        data_published_time = submission_element.get_attribute("data-published-time")
        submission_datetime = datetime.strptime(data_published_time, "%Y%m%d%H%M")
        submission_date = submission_datetime.strftime("%Y-%m-%d")
        submission_time = submission_datetime.strftime("%H:%M")
    except Exception as e:
        logging.error(f"Error extracting submission date/time from {url}: {str(e)}")
        submission_date = "unknown"
        submission_time = "unknown"

    try:
        # Article title
        article_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="articleWrap"]/div[1]/header/h1')
            )
        )
        title = article_title.text
    except Exception as e:
        logging.error(f"Error extracting article title from {url}: {str(e)}")
        title = "unknown"

    try:
        # Article body
        article_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "container"))
        )
        paragraphs = article_body.find_elements(By.TAG_NAME, "p")
        body = " ".join([p.text for p in paragraphs])
    except Exception as e:
        logging.error(f"Error extracting article body from {url}: {str(e)}")
        body = "unknown"

    article_data = {
        "Country": "SouthKorea",
        "Press": "Yonhap News Agency",
        "Reporter": reporter,
        "Category": category,
        "SubmissionDate": submission_date,
        "SubmissionTime": submission_time,
        "UpdateDate": "null",
        "UpdateTime": "null",
        "Title": title,
        "Article": body,
        "Size": len(body),
        "url": url,
    }

    print(article_data)  # Print article data

    return article_data


def scrape_category(driver, base_url, category, page_count, article_count):
    articles_data = []
    for i in range(1, page_count + 1):
        driver.get(f"{base_url}/all/{i}")
        for j in range(1, article_count + 1):
            try:
                element_xpath = f'//*[@id="container"]/div/div/div[2]/section/div[1]/ul/li[{j}]/div/div[2]/a'
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, element_xpath))
                )
                article_url = element.get_attribute("href")
                article_data = extract_article_data(driver, article_url, category)
                articles_data.append(article_data)
            except TimeoutException:
                logging.error(f"Timeout while reading element at index {j} on page {i}")
            except Exception as e:
                logging.error(
                    f"Error reading element at index {j} on page {i}: {str(e)}"
                )
        print(
            f"Page {i} of category {category} completed."
        )  # Page crawling completion message
    return articles_data


def translate_text(text):
    try:
        if text == "unknown" or not text.strip():
            return text

        # Splitting text into sentences to avoid long text issues
        sentences = text.split('.')
        translated_sentences = [translate(sentence, "en").strip() for sentence in sentences]
        translation = '. '.join(translated_sentences)

        print(f"Original text: {text}")
        print(f"Translated text: {translation}")
        print("=" * 50)
        return translation
    except Exception as e:
        logging.error(f"Error during translation: {str(e)}")
        return text  # Return original text if translation fails


def crawl_korea():
    driver = start_driver()

    all_articles = []

    if not os.path.exists("Korea"):
        os.makedirs("Korea")

    categories = [
        {
            "name": "politics",
            "url": "https://www.yna.co.kr/politics",
            "pages": 1,
            "articles": 1,
        },
        {
            "name": "economy",
            "url": "https://www.yna.co.kr/economy",
            "pages": 1,
            "articles": 1,
        },
        {
            "name": "society",
            "url": "https://www.yna.co.kr/society",
            "pages": 1,
            "articles": 1,
        },
        {
            "name": "world",
            "url": "https://www.yna.co.kr/international",
            "pages": 1,
            "articles": 1,
        },
        {
            "name": "industry",
            "url": "https://www.yna.co.kr/industry",
            "pages": 1,
            "articles": 1,
        },
        {
            "name": "culture",
            "url": "https://www.yna.co.kr/culture",
            "pages": 1,
            "articles": 1,
        },
        {
            "name": "sports",
            "url": "https://www.yna.co.kr/sports",
            "pages": 1,
            "articles": 1,
        },
    ]

    for category in categories:
        articles = scrape_category(
            driver,
            category["url"],
            category["name"],
            category["pages"],
            category["articles"],
        )
        all_articles.extend(articles)
        print(f"Category {category['name']} completed.")  # Category crawling completion message

    # Create DataFrame
    df = pd.DataFrame(all_articles)
    df.to_csv(
        os.path.join("Korea", "SouthKorea_articles.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    print("SouthKorea_articles.csv file created.")

    driver.quit()

    # Read CSV file
    df = pd.read_csv(os.path.join("Korea", "SouthKorea_articles.csv"))

    # Select columns to translate
    columns_to_translate = ["Reporter", "Title", "Article"]

    # Translate all data
    for i in range(len(df)):
        for column in columns_to_translate:
            original_text = str(df.at[i, column])
            translated_text = translate_text(original_text)
            if original_text != translated_text:
                print(f"Translated {column} at index {i}: {translated_text}")
            df.at[i, column] = translated_text

    # Save translated DataFrame to new CSV file
    translated_file_name = os.path.join("Korea", "korea_translated.csv")
    df.to_csv(translated_file_name, index=False, encoding="utf-8-sig")
    print(f"{translated_file_name} file created.")

    # Print file save location
    current_dir = os.path.join(os.getcwd(), "Korea")
    print(f"Files saved in: {current_dir}")

    return translated_file_name  # Return the path of the final translated CSV file


if __name__ == "__main__":
    translated_file = crawl_korea()
    print(f"Translated file: {translated_file}")
