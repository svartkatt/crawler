import csv
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://www.work.ua/'
city = 'kyiv'
query = 'junior+python+developer'
url = urljoin(BASE_URL, f'jobs-{city}-{query}')


def get_soup(response):
    return BeautifulSoup(response.text, 'lxml')


def get_links_on_page(page_link):
    response = requests.get(page_link)
    soup = get_soup(response)
    offers = soup.find_all('div', class_='card card-hover card-visited wordwrap job-link')
    links = []
    for offer in offers:
        details_tag = offer.find('a')
        details_link = details_tag.attrs['href']
        links.append(urljoin(BASE_URL, details_link))
    return links


def write_to_csv_file(filename, links):
    with open(filename, mode='w') as f:
        header = ['Title', 'Company', 'Address', 'Conditions & requirements', 'URL']
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for link in links:
            process_offer(writer, link)


def process_offer(writer, offer_link):
    response = requests.get(offer_link)
    soup = get_soup(response)

    title = soup.find('h1')
    title_tag = title.text.strip()

    company = soup.find('b', class_='')
    company_tag = company.text

    address = soup.find('p', class_='text-indent add-top-sm')
    address_text = address.text.strip()
    ad = address_text.split('\n')
    address_tag = ad[0]

    cond_req = soup.find_all('p', 'text-indent add-top-sm')
    cond_req_tag = None
    for i in cond_req:
        if i.find('span', 'glyphicon glyphicon-tick text-black glyphicon-large'):
            cond_req_text = i.text.strip()
            cond_req_tag = ' '.join(cond_req_text.split())

    writer.writerow({
        'Title': title_tag,
        'Company': company_tag,
        'Address': address_tag,
        'Conditions & requirements': cond_req_tag,
        'URL': offer_link
    })


links = get_links_on_page(url)

filename = f'{query}.csv'
write_to_csv_file(filename, links)
