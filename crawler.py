import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from pymongo import MongoClient

load_dotenv()

login_url = "https://everytime.kr/login"
taxi_url_prefix = "https://everytime.kr/514512/p/"
chromedriver_filepath = os.getenv("chromedriver_filepath")
mongodb_uri = os.getenv("mongodb_uri")
db_name = os.getenv("db")

if __name__ == "__main__":

    # TODO: python scheduler 사용 시 리팩토링

    browser = webdriver.Chrome(chromedriver_filepath)
    browser.get(login_url)

    # 로그인
    id = browser.find_element(By.NAME, "userid").send_keys(os.getenv("everytime_id"))
    password = browser.find_element(By.NAME, "password").send_keys(
        os.getenv("everytime_password")
    )
    login_button = browser.find_element(
        By.XPATH, "//*[@id='container']/form/p[3]/input"
    )
    login_button.click()

    # collection 생성 및 연결

    client = MongoClient(mongodb_uri)
    db = client[db_name]

    if not "everytime_taxi_articles" in db.list_collection_names():
        everytime_taxi_articles = db.create_collection("everytime_taxi_articles")
    everytime_taxi_articles = db["everytime_taxi_articles"]

    # html 페이지 크롤링
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

            if len(list(everytime_taxi_articles.find({"id": id}))) == 0:
                everytime_taxi_articles.insert_one(article)

        page_number += 1
