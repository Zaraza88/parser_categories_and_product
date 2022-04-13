import csv
import time
import json
import requests
from bs4 import BeautifulSoup

from parser_home import pars_categories


HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}
HOST = 'https://mobistore.by'


def view_category():
    """Вызываем парсер категорий для предоставления списка категорий"""

    categories = pars_categories()

    for category in enumerate(categories, start=1):
        print(*category)

    get_url = input('Введите название требуемой категории: ').capitalize()

    for _ in categories:
        if get_url not in categories:
            print(
                '[Error] Вы допустили ошибку, попробуйте снова [Error]'
                )
            time.sleep(2)
            return view_category() 
    return categories[get_url]    


url_category = view_category()  


URL = f'https://mobistore.by/{url_category}/'


def choice():
    """Выбор способа сохранения данных"""

    input_format = input(
        """
        [Выберите способ сохранения файла]: \
        \nПарсинг в json формат. Введите - json \
        \nПарсинг в csv формат. Введите - csv
        """
        )
    if input_format != 'json' and input_format != 'csv':
        print('[НЕВЕРНОЕ ЗНАЧЕНИЕ]\n[Повторите попытку]')
        return choice()
    return f'{input_format}'


choice = choice()


def get_pages():
    """
    Получаем всем страницы. 
    Если есть пагинация, парсим страницы, 
    если пагинации нет, значит парсим первую страницу
    """

    response = requests.get(url=URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')

    pagination = soup.find('ul', class_='pagination')

    if pagination:
        return int(pagination.find_all('li')[-2].text)
    return 1


def parse_each_page(pages):
    """Парсер каждого блока с продуктом"""

    for page in range(1, pages + 1):
        url = f'{HOST}/{url_category}?page={page}'

        response = requests.get(url=url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')

        block_content = soup.find_all('div', class_='product text-center')

        data = []

        #вызываем функцию парсинга конкретного продукта
        parse_block(block_content, page, data)

        #сохраняем данные на каждой итерации в отдельный файл
        save_data(data, page)


def parse_block(block_content, page, data):
    """Парсинг конкретного продукта"""
    
    for product in block_content:
        
        try:
            sticker = product.find('div', class_='product__sticker').get_text()
        except AttributeError:
            sticker = 'Нет стикера'

        try:
            price = product.find('span', class_='price') \
                .get_text().strip().replace('от', '').split()
            new_price = f'{price[1]}p.'
            old_price = f'{price[0]}p.'
        except AttributeError:
            new_price = 'Нет цены'
            old_price = 'Нет цены'
            
        title = product.find('a', class_='product-name').get_text().strip()
        href = HOST + product.find('a', class_='image').get('href')

        data.append({
            'title': title,
            'href': href,
            'sticker': sticker,
            'old_price': old_price,
            'new_price': new_price,
        })

    print(f'Парсинг страници номер {page}')


def save_data(data, page):
    """Сохраняем данные либо в json либо csv"""

    if choice == 'json':
        with open(f'data_{page}.json', 'w') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    if choice == 'csv':
        with open(f'file_{page}.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=' ')
            writer.writerow(
                [
                'Название',
                'Ссылка',
                'Стикер',
                'Старая цена', 
                'Новая цена'
                ]
            )
            for item in data:
                writer.writerow(
                    [
                    item['title'],
                    item['href'],
                    item['sticker'], 
                    item['old_price'], 
                    item['new_price']
                    ]
                )


if __name__ == '__main__':
    pages = get_pages()
    parse_each_page(pages)
