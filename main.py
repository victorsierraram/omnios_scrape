import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
from currency_converter import CurrencyConverter

url_base = "http://books.toscrape.com"

data_book = {"title":None,
        "price": None,
        "img_url": None,
        "stars": None}
list_books = list()

logger = logging.getLogger('Log')
logger.setLevel(logging.DEBUG)

def scrape_data(url):

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    page_books = soup.find_all(class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    for book in page_books:
        title = book.find("h3").find("a").get("title")
        price = book.find(class_="price_color").text[1:]
        img_url = book.find("a").find("img").get('src')
        stars = book.find("p").get("class")[1]
        print(url, title, price, img_url, stars)

        data = data_book.copy()
        data["title"] = title
        data["price"] = price
        data["img_url"] = img_url
        data["stars"] = stars

        list_books.append(data)

    try:
        next_page_url = soup.find(class_="pager").find(class_="next").find("a").get("href")
        next = url_base+'/'+next_page_url
        if "catalogue" not in next:
            next = url_base+'/catalogue/'+next_page_url
        scrape_data(next)
    except:
        return 0


def get_text(text):
    headers = {
        'api-key': 'c59290ab-bd4f-4ab5-a24d-6b06cb12b22a',
    }

    files = {
        'text': text,
    }

    response = requests.post('https://api.deepai.org/api/text-generator', headers=headers, files=files).json()
    return response.get("output")


def execute():
    c = CurrencyConverter()
    #Below lines are for scrap the information into result.csv
    '''
    scrape_data(url=url_base)
    df = pd.DataFrame(list_books)
    '''
    df = pd.read_csv("result.csv")
    df["pounds"] = df["price"].str.replace(u"\xA3", "")
    df["euros"] = df["pounds"].apply(lambda x: c.convert(x, "GBP", "EUR"))
    df["text"] = df["title"].apply(lambda x: get_text(x))
    df.to_csv("result_text.csv", index=True)

if __name__ == '__main__':
    execute()
