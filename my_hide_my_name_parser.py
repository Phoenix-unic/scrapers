import undetected_chromedriver as undetected
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as e_c
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


def next_page_generator(driver: undetected.Chrome, domain: str, url: str) -> list:
    driver.get(url=url)
    WebDriverWait(driver=driver, timeout=10).until(e_c.presence_of_element_located((By.CLASS_NAME, 'pagination')))
    soup = BeautifulSoup(markup=driver.page_source, features='lxml')
    pagination = soup.select_one('.pagination').select('li')

    if len(pagination) == 1:
        yield url
    else:
        proxy_type = url[-1]
        pages = (int(soup.select_one('li.next_array').previous_sibling.text) - 1) * 64  # some numbers hardcoding here and there))
        for i in range(0, pages + 1, 64):
            link = f'{domain}/ru/proxy-list/?type={proxy_type}&start={i}'
            yield link


def get_proxies_from_page(url: str, driver: undetected.Chrome) -> list:
    proxies = []
    driver.get(url=url)
    WebDriverWait(driver=driver, timeout=10).until(e_c.presence_of_element_located((By.CLASS_NAME, 'pagination')))
    soup = BeautifulSoup(markup=driver.page_source, features='lxml')
    rows = soup.select_one('tbody').select('tr')

    for tr in rows:
        ip, port = [x.text for x in tr.select('td')[:2]]
        proxies.append(f'{ip}:{port}')
    return proxies


def write_to_txt(file_name: str, data: iter) -> None:
    with open(file_name, 'w', encoding='utf-8') as file:
        for line in data:
            print(line, file=file)
    print(f'{file_name} was written successfully...')


def main():
    hide_my_name_http = 'https://hidemy.name/ru/proxy-list/?type=h'
    hide_my_name_https = 'https://hidemy.name/ru/proxy-list/?type=s'
    hide_my_name_socks4 = 'https://hidemy.name/ru/proxy-list/?type=4'
    hide_my_name_socks5 = 'https://hidemy.name/ru/proxy-list/?type=5'
    hide_my_name_domain = 'https://hidemy.name'
    data = list()

    with undetected.Chrome() as driver:
        driver.set_window_size(1200, 800)
        driver.implicitly_wait(10)

        for link in next_page_generator(driver=driver, domain=hide_my_name_domain, url=hide_my_name_https):
            try:
                proxies = get_proxies_from_page(driver=driver, url=link)
                data.extend(proxies)
            except Exception as ex_:
                print(ex_)
                continue

    write_to_txt(file_name='https.txt', data=data)  # <<<---


if __name__ == '__main__':
    main()





























































