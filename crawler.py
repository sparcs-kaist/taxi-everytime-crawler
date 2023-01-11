
# pip install selenium
# setup chromedriver by your chrome version

from selenium import webdriver

# change chromedriver url by your local environment
chromedriver_url = "./chromedriver_win32/chromedriver.exe"

browser = webdriver.Chrome(chromedriver_url)

url = "https://everytime.kr"

browser.get(url)

# chrome 종료 방지
while True:
    pass




