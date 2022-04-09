from bs4 import BeautifulSoup
import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}

URL = f'https://mobistore.by/catalog-main'
HOST = 'https://mobistore.by'


def pars_categories():
    """Получаем все категории для дальнейшего парсинга"""
    
    response = requests.get(url=URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')

    block_cat = soup.find_all('div', 'catalog-menu__subcat-list_c')

    dict_categories = {}

    #вложенный цикл что бы распоковать html
    for block in block_cat:
        categories = block.find_all('a', class_='catalog-menu__subcat-list__item__name'),
        for category in categories:
            for cat in category:
                for k in cat:
                    dict_categories[k] = cat.get('href')
    
    return dict_categories
 
    
