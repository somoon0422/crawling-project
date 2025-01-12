import os
import pandas as pd
import logging
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from mtranslate import translate
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import WebDriverException

# Logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# List of category URLs to crawl
category_urls = [
    ("society", "https://vietnamnews.vn/society"),
    ("politics-laws", "https://vietnamnews.vn/politics-laws"),
    ("economy", "https://vietnamnews.vn/economy"),
    ("sports", "https://vietnamnews.vn/sports"),
    ("life-style", "https://vietnamnews.vn/life-style"),
]


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

# Crawling function
def crawl_and_translate(driver, category_name, category_url):
    # Adding to column list
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

    try:
        for i in range(1, 2):  # For testing: crawl only 1 page
            logging.info(f"Processing page {i} of {category_name}")
            driver.get(f"{category_url}?p={i}")
            try:
                # Crawl main article
                big_headline = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[2]/div[2]/div[1]/section[1]/div/article/h2/a",
                        )
                    )
                )
                big_headline_href = big_headline.get_attribute("href")
                driver.execute_script(
                    "window.open(arguments[0], '_blank');", big_headline_href
                )
                driver.switch_to.window(driver.window_handles[1])

                # Add news site name
                press = "Vietnam News"
                Press.append(press)

                # Add reporter name
                reporter = "null"
                Reporter.append(reporter)

                # Add category
                category = category_name
                Category.append(category)

                # Add submission date
                datetime_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "datetime"))
                )
                datetime_text = datetime_element.text.strip()

                # Use regex to extract date and time
                date_pattern = re.compile(r"(\w+ \d{1,2}, \d{4})")
                time_pattern = re.compile(r"(\d{2}:\d{2})")

                date_match = date_pattern.search(datetime_text)
                time_match = time_pattern.search(datetime_text)

                if date_match and time_match:
                    # Date and time strings
                    date_str = date_match.group(1)
                    time_str = time_match.group(1)

                    # Convert date format
                    date_obj = datetime.strptime(date_str, "%B %d, %Y")
                    submission_date = date_obj.strftime("%Y%m%d")
                    SubmissionDate.append(submission_date)

                    # Convert time format
                    submission_time = time_str.replace(":", "")
                    SubmissionTime.append(submission_time)
                else:
                    SubmissionDate.append("null")
                    SubmissionTime.append("null")

                # Add update date
                UpdateDate.append("null")
                UpdateTime.append("null")

                # Add title
                title_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "headline"))
                )
                title = title_element.text
                titles.append(title)

                # Add article content
                content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "abody"))
                )
                paragraphs = content.find_elements(By.TAG_NAME, "p")
                article_text = "\n".join([p.text for p in paragraphs])
                articles.append(article_text)

                # Add article size
                size = len(article_text)
                Size.append(size)

                # Add article URL
                article_url = big_headline_href
                urls.append(article_url)

                logging.info(f"Page {i} of {category_name} processed successfully")

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                logging.error(
                    f"Error processing main article on page {i} of {category_name}: {str(e)}"
                )

            # Crawl smaller articles
            for j in range(1, 2):  # For testing: crawl only 1 article
                try:
                    small_headline = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                f"/html/body/div[2]/div[2]/div[1]/div[2]/div[1]/article[{j}]/h2/a",
                            )
                        )
                    )
                    small_headline_href = small_headline.get_attribute("href")
                    driver.execute_script(
                        "window.open(arguments[0], '_blank');", small_headline_href
                    )
                    driver.switch_to.window(driver.window_handles[1])

                    # Add news site name
                    press = "Vietnam News"
                    Press.append(press)

                    # Add reporter name
                    reporter = "null"
                    Reporter.append(reporter)

                    # Add category
                    category = category_name
                    Category.append(category)

                    # Add submission date
                    datetime_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "datetime"))
                    )
                    datetime_text = datetime_element.text.strip()

                    # Use regex to extract date and time
                    date_match = date_pattern.search(datetime_text)
                    time_match = time_pattern.search(datetime_text)

                    if date_match and time_match:
                        # Date and time strings
                        date_str = date_match.group(1)
                        time_str = time_match.group(1)

                        # Convert date format
                        date_obj = datetime.strptime(date_str, "%B %d, %Y")
                        submission_date = date_obj.strftime("%Y%m%d")
                        SubmissionDate.append(submission_date)

                        # Convert time format
                        submission_time = time_str.replace(":", "")
                        SubmissionTime.append(submission_time)
                    else:
                        SubmissionDate.append("null")
                        SubmissionTime.append("null")

                    # Add update date
                    UpdateDate.append("null")
                    UpdateTime.append("null")

                    # Add title
                    title_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "headline"))
                    )
                    title = title_element.text
                    titles.append(title)

                    # Add article content
                    first_body = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "abody"))
                    )
                    first_body = first_body.find_elements(By.TAG_NAME, "p")
                    article_text = " ".join([p.text for p in first_body])
                    articles.append(article_text)

                    # Add article size
                    size = len(article_text)
                    Size.append(size)

                    # Add article URL
                    article_url = small_headline_href
                    urls.append(article_url)

                    logging.info(
                        f"Page {i}, article {j} of {category_name} processed successfully"
                    )

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                except Exception as e:
                    logging.error(
                        f"Error processing small article on page {i}, article {j} of {category_name}: {str(e)}"
                    )

    except WebDriverException as e:
        logging.error(f"WebDriverException occurred: {str(e)}")
    finally:
        driver.quit()

    # Convert to DataFrame
    df = pd.DataFrame(
        {
            "Country": "Vietnam",
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


# Select columns to translate
columns_to_translate = ["Title", "Article"]


# Define translation function
def translate_text(text):
    try:
        translation = translate(text, "en")
        logging.info(f"Original Text: {text}")
        logging.info(f"Translated Text: {translation}")
        logging.info("=" * 50)
        return translation
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        return None  # Replace with 'None' if an error occurs during translation


# Create DataFrame and translate
def create_dataframe_and_translate(df, category_name):
    if not os.path.exists("Vietnam"):
        os.makedirs("Vietnam")

    # If there is previously translated data, continue from where left off
    try:
        translated_df = pd.read_csv(
            os.path.join("Vietnam", f"Translated_Vietnamnews_{category_name}.csv")
        )
        logging.info(f"Loaded previously translated data for {category_name}")
    except FileNotFoundError:
        logging.info(
            f"No previously translated data found for {category_name}. Starting new translation."
        )
        translated_df = None

    if translated_df is not None and not translated_df.empty:
        for column in columns_to_translate:
            df[column] = df[column].where(df[column].notnull(), translated_df[column])
        start_index = len(translated_df)
    else:
        start_index = 0

    # Translate remaining data
    for i in range(start_index, len(df)):
        for column in columns_to_translate:
            df.at[i, column] = translate_text(str(df.at[i, column]))

    # Save translated DataFrame to a new CSV file
    df.to_csv(
        os.path.join("Vietnam", f"Translated_Vietnamnews_{category_name}.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    logging.info(f"Translated_Vietnamnews_{category_name}.csv created successfully")


# Execute crawling and translation for all categories
def crawl_vietnam():
    driver = start_driver()
    all_dfs = []  # List to store data of each category

    try:
        for category_name, category_url in category_urls:
            logging.info(f"Processing category: {category_name}")
            df = crawl_and_translate(driver, category_name, category_url)
            create_dataframe_and_translate(df, category_name)
            all_dfs.append(df)
    except Exception as e:
        logging.error(f"Error occurred during crawling for Vietnam: {e}")
    finally:
        driver.quit()

    # Combine all category data into one file
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_file_path = os.path.join("Vietnam", "Vietnam_articles.csv")
    combined_df.to_csv(combined_file_path, index=False, encoding="utf-8-sig")
    logging.info(f"All categories combined into {combined_file_path}")

    return combined_file_path  # Modified: Return DataFrame


if __name__ == "__main__":
    crawl_vietnam()
    print(f"Combined DataFrame:\n{combined_df}")
