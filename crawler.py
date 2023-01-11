import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

login_url = "https://everytime.kr/user/login"
taxi_url = "https://everytime.kr/514512"

params = {
    "userid" : os.getenv('id_antaechan'),
    "password" : os.getenv('pw_antaechan'),
    "redirect" : "/"
}

headers = {
    "User-Agent": os.getenv('user-agent')
}

res = requests.post(login_url, params = params, headers = headers)
res.raise_for_status()

if __name__ == "__main__":
    res = requests.get(taxi_url, headers=headers)
    res.raise_for_status()
    
    soup = BeautifulSoup(res.text, "lxml")
    print(soup.prettify())





