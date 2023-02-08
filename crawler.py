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
chromedriver_filepath = os.getenv('chromedriver_filepath')
page_number_end = 40

if __name__ == "__main__":
    
    browser = webdriver.Chrome(chromedriver_filepath)
    browser.get(login_url)

    # 로그인
    id = browser.find_element(By.NAME, "userid").send_keys(os.getenv('everytime_id'))
    password = browser.find_element(By.NAME, "password").send_keys(os.getenv('everytime_password'))
    login_button = browser.find_element(By.XPATH, "//*[@id='container']/form/p[3]/input")
    login_button.click()
    
    # localhost의 mongoDB 연결
    
    # TODO: python scheduler 사용 시 리팩토링
    client = MongoClient(host=os.getenv('hostname'), port=int(os.getenv('port')))

    # DB 접근
    local = client['local']

    if not "everytime_taxi_articles" in local.list_collection_names():
        everytime_taxi_articles = local.create_collection('everytime_taxi_articles')
        
    everytime_taxi_articles = local["everytime_taxi_articles"]
    
    # 택시 게시판 html 요청
    page_number = 1
    while True:
        taxi_url = taxi_url_prefix + str(page_number)
        browser.get(taxi_url)
        taxi_page =  browser.page_source
        
        soup = BeautifulSoup(taxi_page, "html5lib")
        wrap_articles = soup.find("div", attrs = {"class":"wrap articles"})
        
        if wrap_articles.find("article", attrs={"class": "dialog"}) != None:
            break
        
        raw_articles = wrap_articles.find_all("article")
        
        for raw_article in raw_articles:
            id = raw_article.find("a", attrs={"class": "article"})['href'][-9:]
            date, time = raw_article.find("time").text.split(" ")
            context = raw_article.find("p", attrs = {"class":"medium"}).text
    
            # TODO: 글의 고유 id가 collection 안에 존재 시 insert x
            article = { "id": id, "date": date, "time": time, "context": context }
            everytime_taxi_articles.insert_one(article)
        
        page_number += 1       



