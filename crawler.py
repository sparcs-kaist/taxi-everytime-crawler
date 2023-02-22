import os
import schedule
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient

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

    # 로그인
    browser.find_element(By.NAME, "userid").send_keys(os.getenv("everytime_id"))
    browser.find_element(By.NAME, "password").send_keys(os.getenv("everytime_password"))
    login_button = browser.find_element(
        By.XPATH, "//*[@id='container']/form/p[3]/input"
    )
    login_button.click()


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

            if len(list(db_articles.find({"id": id}))) == 0:
                db_articles.insert_one(article)

        page_number += 1


if __name__ == "__main__":
    schedule.every(30).minutes.do(crawling)

    while True:
        schedule.run_pending()
        time.sleep(1)
