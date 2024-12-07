import json
import time
import requests
from bs4 import BeautifulSoup


page = 1
filename = 'carro.json'


def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)

    with open(filename, 'w') as f:
        json.dump(data, f, **kwargs)


def get_soup(url, **kwargs):
    response = requests.get(url, **kwargs)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
    else:
        soup = None
    return soup


def crawl_products(pages_count):
    urls = []
    fmt = 'https://carro.ru/used?page={page}'

    for page_n in range(1, 1 + pages_count):
        print('page: {}'.format(page_n))
        
        page_url = fmt.format(page=page_n)
        soup = get_soup(page_url)
        if soup is None:
            break

        for tag in soup.select('.catalog__title-link'):
            href = tag.attrs['href']
            url = 'https://carro.ru/{}'.format(href)
            urls.append(url)

    return urls


def parse_products(urls):
    data = []

    for url in urls:
        print('\tproduct: {}'.format(url))

        soup = get_soup(url)
        if soup is None:
            break

        name = soup.select_one('.heading-group--offer').text.strip()
        price = soup.select_one('.car__price').text.strip()
        price_old = soup.select_one('.car__price-old').text.strip()
        diler = soup.find("span", class_="heading-group__label").text.strip()
        rating = soup.find("div", class_="rating").text.strip()
        metro = [li.text.strip() for li in soup.find_all("li", class_="features__item") if "м." in li.text][0]

        tech_specs = {}
        for li in soup.select("ul.tech li.tech__item"):
            label = li.select_one(".tech__label").text.strip()
            value = li.select_one(".car__tech-content").text.strip()
            tech_specs[label.replace(": ", "")] = value
        item = {
            'name': name,
            'price': price,
            'price_old': price_old,
            'tech_specs': tech_specs,
            'diler': diler,
            'url': url,
            'rating': rating,
            'metro': metro
        }
        data.append(item)

    return data

def main():
    urls = crawl_products(page)
    data = parse_products(urls)
    dump_to_json(filename, data)

if __name__ == '__main__':
    main()
