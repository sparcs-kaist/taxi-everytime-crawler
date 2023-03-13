import os
import schedule
import time
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

login_url = "https://everytime.kr/login"
taxi_url_prefix = "https://everytime.kr/514512/p/"


def crawling():
    browser = webdriver.Chrome(os.getenv("chromedriver_filepath"))
    login(browser)
    db_articles = connect_db()
    update_db(browser, db_articles)


def login(browser):
    browser.get(login_url)

    browser.find_element(By.NAME, "userid").send_keys(os.getenv("everytime_id"))
    browser.find_element(By.NAME, "password").send_keys(os.getenv("everytime_password"))

    solve_captcha(browser)

    login_button = browser.find_element(
        By.XPATH, "//*[@id='container']/form/p[3]/input"
    )

    login_button.click()


def solve_captcha(browser):

    site_key = "6LcIzJgkAAAAAPBm90Y_3UPvkR_ZuM9Rh0P89CBe"
    method = "userrecaptcha"
    key = os.getenv("2captcha_api_key")

    url = f"http://2captcha.com/in.php?key={key}&method={method}&googlekey={site_key}&pageurl={login_url}"
    response = requests.get(url)

    print(response.text)

    captcha_id = response.text[3:]
    token_url = "http://2captcha.com/res.php?key={}&action=get&id={}".format(
        key, captcha_id
    )

    while True:
        time.sleep(10)
        response = requests.get(token_url)

        if response.text[0:2] == "OK":
            break

    print(response.text)
    captha_results = response.text[3:]
    browser.execute_script(
        """document.querySelector('[name="g-recaptcha-response"]').innerText='{}'""".format(
            captha_results
        )
    )
    browser.find_element(By.XPATH, '//*//*[@id="recaptcha-anchor"]').click()

    # solver = TwoCaptcha(os.getenv("2captcha_api_key"))

    # try:
    #     print("Solving captcha...")
    #     result = solver.recaptcha(
    #         sitekey="6LcIzJgkAAAAAPBm90Y_3UPvkR_ZuM9Rh0P89CBe",
    #         url="https://everytime.kr/login",
    #     )
    #     WebDriverWait(browser, 10).until(
    #         EC.presence_of_element_located((By.ID, "g-recaptcha-response"))
    #     )

    #     captcha_response_textarea = browser.find_element(
    #         By.XPATH, '//*[@id="g-recaptcha-response"]'
    #     )

    #     captcha_response_textarea.send_keys(result["code"])

    #     captcha_button = browser.find_element(By.XPATH, '//*[@id="recaptcha-anchor"]')
    #     captcha_button.click()

    # except Exception as e:
    #     print("Error: ", e)


def connect_db():
    client = MongoClient(os.getenv("mongodb_uri"))
    db = client[os.getenv("db")]

    if not "db_articles" in db.list_collection_names():
        db_articles = db.create_collection("db_articles")
    db_articles = db["db_articles"]

    return db_articles


def update_db(browser, db_articles):
    page_number = 1
    while True:
        browser.get(taxi_url_prefix + str(page_number))
        taxi_page = browser.page_source

        soup = BeautifulSoup(taxi_page, "html5lib")
        wrap_articles = soup.find("div", attrs={"class": "wrap articles"})

        if wrap_articles.find("article", attrs={"class": "dialog"}) != None:
            break

        raw_articles = wrap_articles.find_all("article")

        for raw_article in raw_articles:
            id = raw_article.find("a", attrs={"class": "article"})["href"][-9:]
            date, time = raw_article.find("time").text.split(" ")
            context = raw_article.find("p", attrs={"class": "medium"}).text

            article = {"id": id, "date": date, "time": time, "context": context}

            if len(list(db_articles.find_one({"id": id}))) == 0:
                db_articles.insert_one(article)
                post_message(context)

        page_number += 1


def post_message(context, channel="#taxi-crawler-bot"):

    token = os.getenv("slack_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = f"text={context}&channel={channel}"

    try:
        response = requests.post(
            "https://slack.com/api/chat.postMessage", headers=headers, data=data
        )
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    schedule.every(10).seconds.do(crawling)

    while True:
        schedule.run_pending()
        time.sleep(1)
