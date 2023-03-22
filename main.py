import os
import time
import re
from bs4 import BeautifulSoup
import requests
import pandas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


options = Options()
executable_path = os.path.join(os.getcwd(), 'chromedriver', 'chromedriver.exe')
browser = webdriver.Chrome(options=options, service=Service(executable_path=executable_path))
url = 'https://www.avito.ru/'


def get_html(url, params=None):
    html = requests.get(url, params=params)
    return html


def parse_url(url):
    search = input('Введите запрос поиска: ')
    min_price = input('Введите минимальную стоимость: ')
    max_price = input('Введите максимальную стоимость: ')
    html = get_html(url, params={'bt': 1, 'pmax': max_price, 'pmin': min_price, 'q': search, 's': '2', 'view': 'gallery'})
    url2 = html.url
    return url2


def parse(url):
    url2 = parse_url(url)
    browser.get(url2)
    time.sleep(1)

    soup = BeautifulSoup(browser.page_source, 'lxml')
    blocks = soup.find_all('div', class_=re.compile('iva-item-content'))
    data = []

    for block in blocks:
        data.append({
            "Наименование": block.find('h3', class_=re.compile('title-root')).get_text(strip=True),
            'Цена': block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace('\xa0', ''),
            'Город': block.find('a', class_=re.compile('link-link')).get('href').split('/')[1],
            'Ссылка': url + block.find('a', class_=re.compile('link-link')).get('href'),
        })
    return data


def save_excel(data):
    file_name = input('Введите название файла')
    df_data = pandas.DataFrame(data)
    data_clear = df_data.drop_duplicates('Ссылка')
    writer = pandas.ExcelWriter(f'{file_name}.xlsx')
    data_clear.to_excel(writer, f'{file_name}')
    writer.save()
    print(f'Данные сохранены в файл "{file_name}.xlsx"')


save_excel(parse(url))

