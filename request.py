# import requests
# from bs4 import BeautifulSoup

# url_ = requests.get("https://odium.kr", headers={'User-Agent':'Mozilla/5.0'})
# source = BeautifulSoup(url_.text, "html.parser")
# level = source.find('span',property='id')
# counts = source.select_one("#header > p").text
# print(counts)

from requests_html import HTMLSession
from bs4 import BeautifulSoup

session = HTMLSession()

r = session.get('http://odium.kr')

r.html.render()  # this call executes the js in the page
value = r.html.find('#header > p',first=True)
print(value.text)