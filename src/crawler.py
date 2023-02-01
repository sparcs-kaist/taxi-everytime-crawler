import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

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
    
    # 택시 게시판 html 요청
    for page_number in range(page_number_end + 1):
        taxi_url = taxi_url_prefix + str(page_number)
        browser.get(taxi_url)
        taxi_page =  browser.page_source
        browser.quit()
        
        soup = BeautifulSoup(taxi_page, "html5lib")
        
        wrap_articles = soup.find("div", attrs = {"class":"wrap articles"})
        articles = wrap_articles.find_all("article")
                
        for article in articles:
            new_articles = [article.text for article in articles]
            
        print(new_articles)
        
        while True:
            continue



