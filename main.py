import os
import json
import time
import requests
from bs4 import BeautifulSoup
import datetime
import csv

start_time = time.time()

headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0"
    }


def get_data():
    cur_date = datetime.datetime.now().strftime('%d-%m-%Y_%H:%M')

    # Створюємо папку для данніх
    os.mkdir(f'data_{cur_date}')

    # Створюємо csv файл на запис
    with open(f'data_{cur_date}/result.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'Назва товару',
                'Ціна',
                'Стан',
                'Дата публікації',
                'Місто',
                'Район',
                'Координати на карті',
                "Продавець",
                'Магазин',
                'Посилання на оголошення',
            )
        )

    # Лінк для останньої цифри пагінації
    url = 'https://www.olx.ua/d/hobbi-otdyh-i-sport/sport-otdyh/velo/q-gravel/?currency=UAH&search%5Border%5D=filter_float_price%3Aasc&search%5Bfilter_enum_subcategory%5D%5B0%5D=velosipedy'

    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    # Забираємо останню цифру пагінації на сторінці
    pagination_list = soup.find('ul', class_='pagination-list').find_all('li')
    pages_count = int(pagination_list[-1].find('a').text)
    extreme_offset = (pages_count - 1) * 40

    # Проходимо по всім лінкам з json api у яких змінюється параметр offset на 40
    result_list = []
    for offset in range(0, extreme_offset + 40, 40):
        response = requests.get(url=f"https://www.olx.ua/api/v1/offers/?offset={offset}&limit=40&query=gravel&category_id=574&currency=UAH&sort_by=filter_float_price%3Aasc&filter_enum_subcategory[0]=velosipedy&filter_refiners=&sl=1807480a7bax345cab07", headers=headers)
        data = response.json()
        items = data['data']

        # Збираємо данні з json
        for item in items:
            title = item['title'].strip()
            price = item['params'][0]['value']['label']

            try:
                state = item['params'][2]['value']['label']
            except:
                state = 'Невідомо'

            created_date = item['created_time'].split('T')[0]
            city = item['location']['city']['name']

            try:
                area = item['location']['district']['name']
            except:
                area = ''

            map_lat = item['map']['lat']
            map_lon = item['map']['lon']
            map_coordinates = f'{map_lat}, {map_lon}'

            if item['user']['company_name'] == '':
                shop = ''
            elif len(item['user']['company_name']) >= 30:
                shop_long = item['user']['company_name']
                shop = shop_long[:25] + '...'
            else:
                shop = item['user']['company_name']

            seller_name = item['user']['name']

            photos_urls = []
            photos_all = item['photos']
            for i in range(0, len(photos_all)):
                change_link = photos_all[i]['link'].rstrip('{width}x{height}')
                photos_urls.append(change_link)

            url_post = item['url']

            # Дадаємо данні у перелік
            result_list.append(
                {
                    'title': title,
                    'price': price,
                    'state': state,
                    'created_date': created_date,
                    'city': city,
                    'area': area,
                    'map': map_coordinates,
                    'seller_name': seller_name,
                    'shop': shop,
                    'photos_urls': photos_urls,
                    'url': url_post,
                }
            )

            # Записужмо данні у csv файл
            with open(f'data_{cur_date}/result.csv', 'a') as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        title,
                        price,
                        state,
                        created_date,
                        city,
                        area,
                        map_coordinates,
                        seller_name,
                        shop,
                        url_post
                    )
                )

            print(f'[+] Successfully: {title}')

    # Створюємо та записуємо json файл
    with open(f'data_{cur_date}/result.json', 'w') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)


def main():
    get_data()
    finish_time = time.time() - start_time
    print(f'Час виконання скрипту: {finish_time}')


if __name__ == '__main__':
    main()