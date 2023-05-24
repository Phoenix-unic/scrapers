import requests
import json
from bs4 import BeautifulSoup
from tqdm import tqdm


def get_soup_object(url: str) -> BeautifulSoup:
    """create and return bs4 object"""

    response = requests.get(url=url)
    response.encoding = 'utf-8'
    soup_object = BeautifulSoup(response.text, 'lxml')
    return soup_object


def get_item_data(soup: BeautifulSoup) -> dict:
    """collect and return complete item data """
    data = {}
    name, article = soup.select_one('.description').select('p')
    data.update({'name': name.text.strip(), 'article': article.text.split(':')[1].strip()})

    description = soup.select_one('#description')
    description_keys = [li.get('id') for li in description.select('li')]
    description_values = [li.text.split(':')[1].strip() for li in description.select('li')]
    data.setdefault(description.get('id'), dict(zip(description_keys, description_values)))

    in_stock = soup.select_one('#in_stock')
    data.setdefault(in_stock.get('id'), in_stock.text.split(':')[1].strip())

    data.setdefault(soup.select_one('#price').get('id'), soup.select_one('#price').text.strip())
    data.setdefault(soup.select_one('#old_price').get('id'), soup.select_one('#old_price').text.strip())
    return data


def write_to_json(file_name: str, some_data: list):
    """function writes some data to JSON file and allows you to choose file name"""

    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(some_data, file, indent=4, ensure_ascii=False)
    print(f'{file_name} was written successfully...')


def main():
    """main finc, collects all links in all categories on all pages;
        collects item data and writes it to JSON file"""
    url = 'https://parsinger.ru/html/index5_page_1.html'
    url_base = 'https://parsinger.ru/html/'
    json_data = []

    category_list = [url_base + a.get('href') for a in get_soup_object(url=url).select_one('.nav_menu').select('a')]
    for category in category_list:
        pagen_list = [url_base + a.get('href') for a in get_soup_object(url=category).select_one('.pagen').select('a')]
        for page in pagen_list:
            if requests.get(url=page).status_code == 200:
                page_soup = get_soup_object(url=page)
                items_links = [url_base + a.get('href') for a in page_soup.select_one('.item_card').select('.name_item')]

                for link in tqdm(items_links, desc=f'{page}...'):  # делаем профессиональный трекинг
                    # print(f'processing {link}...')  # трекинг для лохов
                    item_soup = get_soup_object(url=link)

                    compleat_item_data = {'category': link.split('/')[-3]}
                    compleat_item_data.update(get_item_data(soup=item_soup))
                    compleat_item_data.setdefault('link', link)
                    json_data.append(compleat_item_data)

    write_to_json(file_name='compleat_items_data.json', some_data=json_data)


if __name__ == '__main__':
    main()
