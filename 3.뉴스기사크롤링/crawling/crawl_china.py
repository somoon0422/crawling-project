import os
import pandas as pd
import logging
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Logging configuration
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log/china_crawl_errors.log"),
        logging.StreamHandler(),
    ],
)

# Category URLs
categories = {
    "politics": "http://en.people.cn/90785/index{}.html",
    "economy": "http://en.people.cn/business/index{}.html",
    "society": "http://en.people.cn/90882/index{}.html",
    "world": "http://en.people.cn/90777/index{}.html",
    "culture": "http://en.people.cn/90782/index{}.html",
    "sports": "http://en.people.cn/90779/index{}.html",
    "military": "http://en.people.cn/90786/index{}.html",
}

def start_driver():
    # Selenium WebDriver configuration
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=Chrome/126.0.6478.127")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    return driver

def crawl_articles(category, driver):
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

    url_format = categories[category]
    time_pattern = re.compile(r"(\d{2}:\d{2}), (\w+ \d{2}, \d{4})")

    for i in range(1, 2):  # Infinite page setting possible
        page = url_format.format(i)
        driver.get(page)

        try:
            for j in range(1, 2):  # Maximum number of articles 21
                time.sleep(3)
                headline = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"/html/body/div/div[5]/div[1]/ul/li[{j}]/a")
                    )
                )
                headline_href = headline.get_attribute("href")
                driver.execute_script("window.open(arguments[0]);", headline_href)
                driver.switch_to.window(driver.window_handles[1])

                if len(driver.window_handles) > 3:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[1])

                Press.append("People.cn")

                try:
                    reporter = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "editor"))
                    )
                    reporter_text = reporter.text
                    if "(" in reporter_text and ")" in reporter_text:
                        names = reporter_text.split("(")[1].split(")")[0]
                        names = names.replace("Web editor:", "").strip()
                        reporter_names = [name.strip() for name in names.split(",")]
                        reporter_result = ", ".join(reporter_names)
                    else:
                        reporter_result = ""
                    Reporter.append(reporter_result)

                except Exception as e:
                    logging.error(e)
                    Reporter.append(None)

                Category.append(category.capitalize())

                try:
                    submission_time_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="origin cf"]/span')
                        )
                    )
                    submission_time_text = submission_time_element.text

                    match = time_pattern.search(submission_time_text)

                    if match:
                        time_str = match.group(1)
                        date_str = match.group(2)
                        datetime_obj = datetime.strptime(
                            f"{date_str} {time_str}", "%B %d, %Y %H:%M"
                        )
                        date = datetime_obj.strftime("%Y-%m-%d")
                        time_formatted = datetime_obj.strftime("%H:%M")

                        SubmissionDate.append(date)
                        SubmissionTime.append(time_formatted)
                    else:
                        SubmissionDate.append(None)
                        SubmissionTime.append(None)
                except Exception as e:
                    logging.error(e)
                    SubmissionDate.append(None)
                    SubmissionTime.append(None)

                UpdateDate.append(None)
                UpdateTime.append(None)

                try:
                    title = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "/html/body/div/div[3]/h1")
                        )
                    )
                    titles.append(title.text)
                except Exception as e:
                    titles.append(None)

                try:
                    article_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="w860 d2txtCon cf"]')
                        )
                    )
                    paragraphs = article_box.find_elements(By.TAG_NAME, "p")
                    article = ""
                    for paragraph in paragraphs:
                        article += paragraph.text + "\n"
                    articles.append(article)
                except Exception as e:
                    articles.append(None)

                try:
                    Size.append(len(article))
                except Exception as e:
                    articles.append(None)

                urls.append(headline_href)

                print(f"Completed crawling article {j}", end="\r")

                driver.close()

                driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            logging.error(e)
            continue

        print(f"Completed crawling page {i}")

    df = pd.DataFrame(
        {
            "Country": "China",
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

def crawl_china():
    driver = start_driver()
    dfs = []
    if not os.path.exists("China"):
        os.makedirs("China")

    for category in categories.keys():
        try:
            category_data = crawl_articles(category, driver)
            category_data.to_csv(
                os.path.join("China", f"China_{category.capitalize()}.csv"), index=False
            )
            dfs.append(category_data)
            print(f"Completed crawling category {category}")
            print(category_data.head(1))  # Print first row
        except Exception as e:
            logging.error(f"Error occurred during China crawling: {str(e)}")

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv(os.path.join("China", "China_articles.csv"), index=False)
    china_articles = os.path.join("China", "China_articles.csv")
    print("Completed crawling all categories")

    driver.quit()

    # Print file save location
    current_dir = os.path.join(os.getcwd(), "China")
    print(f"Files saved in: {current_dir}")

    return china_articles

if __name__ == "__main__":
    crawl_china()
