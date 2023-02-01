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
page_number_end = 1

chromedriver_filepath = os.getenv('chromedriver_filepath')

if __name__ == "__main__":
    
    browser = webdriver.Chrome(chromedriver_filepath)
    browser.get(login_url)

    # 로그인
    id = browser.find_element(By.NAME, "userid").send_keys(os.getenv('everytime_id'))
    password = browser.find_element(By.NAME, "password").send_keys(os.getenv('everytime_password'))
    login_button = browser.find_element(By.XPATH, "//*[@id='container']/form/p[3]/input")
    login_button.click()
    
    # localhost의 mongoDB 연결
    client = MongoClient(host='localhost', port=27017)
    print(client.list_database_names())

    # DB 접근
    local = client['local']
    print(local.list_collection_names())

    if "everytime_taxi_articles" in local.list_collection_names():
        pass
    else:
        # taxi_articles collection 생성
        everytime_taxi_articles = local.create_collection('everytime_taxi_articles')
        print(local.list_collection_names())
    
    everytime_taxi_articles = local["everytime_taxi_articles"]
    
    # 택시 게시판 html 요청
    for page_number in range(page_number_end + 1):
        taxi_url = taxi_url_prefix + str(page_number)
        browser.get(taxi_url)
        taxi_page =  browser.page_source
        
        soup = BeautifulSoup(taxi_page, "html5lib")
        
        wrap_articles = soup.find("div", attrs = {"class":"wrap articles"})
        raw_articles = wrap_articles.find_all("article")
        
        for raw_article in raw_articles:
            upload_time = raw_article.find("time").text
            context = raw_article.find("p", attrs = {"class":"medium"}).text
            
            article = { "upload_time": upload_time, "context": context }
            everytime_taxi_articles.insert_one(article)
        
        



