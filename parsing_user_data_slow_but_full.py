import requests
import re
import math

from bs4 import BeautifulSoup

import secret

# ------ function block -------

def deleting_html(string):
    def deleting_one_elem(string):
        start = 0
        end = 0
        count = 0
        new_string = ''

        for i in string:
            if i == '<':
                start = count
            if i == '>':
                end = count
                break
            count += 1
        new_string = string[:start] + string[end+1:]
        return new_string

    counter = 0
    for i in string:
        if i == '<':
            counter += 1

    new_str = string

    if counter > 0:
        for i in range(counter):
            new_str = deleting_one_elem(new_str)

    return new_str

def deleting_others(string):
    string = string.replace(u'\xa0', u' ')
    string = string.replace(u'\n', u'. ')
    return string

def del_authors_dop(string):
    string = string.replace('<', '')
    string = string.replace('>', '')
    return string

def quotes_explanation(string):
    string = string.replace('Пояснение к цитате', '  - Пояснение к цитате')
    return string


def page_data(url, proxies):
    r = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(r.content, features="html.parser")

    quotes = soup.find('div', {'class': 'search-results -results'}).findAll('article')
    filterted_quotes = []
    string = ''
    # -- quotes filtering -----
    for i in quotes:
        k = str(i)
        for j in k:
            if j != '\n':
                string += j
        filterted_quotes.append(string)
        string = ''

    quotes = filterted_quotes
    filterted_quotes = []
    authors = []
    a_list = []

    for i in quotes:
        k = str(i)
        data_quote = re.findall(r'<p>.*</p>', k)

        if data_quote != []:
            filterted_quotes.append(data_quote[0])

        if re.findall(r'Автор неизвестен', k) != []:
            data_authors = re.findall(r'Автор неизвестен', k)
            authors.append(data_authors[0])
        else:
            data_authors = re.findall(r'title=".{0,100}"', k)
            for j in data_authors:
                s = re.findall(r'title="Поделиться"', j)
                if s == []:
                    a_list.append(j)
                else:
                    authors.append(a_list)
                    a_list = []
                    break

    new_quotes = list(map(deleting_html, filterted_quotes))
    new_quotes = list(map(deleting_others, new_quotes))
    new_quotes = list(map(quotes_explanation, new_quotes))

    # -- authors filtering -----
    a_list = authors
    authors = []
    k = ''

    for i in a_list:
        if i != 'Автор неизвестен':
            k = k.join(i)
            authors.append(k)
            k = ''
        else:
            authors.append(i)

    a_list = authors
    authors = []
    ab_list = []

    for i in a_list:
        if i != 'Автор неизвестен':
            k = re.findall(r'>[^</>]*<', i)
            ab_list = []
            for j in k:
                if j != '><':
                    ab_list.append(j)
            authors.append(ab_list)
        else:
            authors.append(i)

    a_list = authors
    authors = []
    k = ''

    for i in a_list:
        if i != 'Автор неизвестен':
            if len(i) > 1:
                if len(i[1]) > 4:
                    i[0] = i[0] + ' - '

    for i in a_list:
        if i != 'Автор неизвестен':
            k = k.join(i)
            authors.append(k)
            k = ''
        else:
            authors.append(i)

    authors = list(map(del_authors_dop, authors))

    return (dict(zip(new_quotes, authors)))


# ------ end function block -------

# ------ main block -------

def main_func(param, quotes_quantity):

    quotes_quantity = math.floor(quotes_quantity / 10)

    proxies = secret.proxies

    url = secret.url + param

    # ---how many pages ---

    last_page = 10

    try:
        r = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(r.content, features="html.parser")
        if soup.find('h2') is None:
            last_page = 1
            try:
                r = requests.get(url + '?page=1', proxies=proxies)
                soup = BeautifulSoup(r.content, features="html.parser")
                if soup.find('h2') is None:
                    last_page = 2
            except Exception:
                pass
        else:
            last_page = 0

    except Exception as err:
        print('ERROR  --- ', err)

    quote_dict = {}

    if last_page > 0:
        if last_page > 0:
            url = secret.url + param
            quote_dict.update(page_data(url, proxies))

    if last_page > 1:
        new_url = url + '?page=' + str(100000)
        print(new_url)
        r = requests.get(new_url, proxies=proxies)
        soup = BeautifulSoup(r.content, features="html.parser")
        last_page = soup.find('ul', {'class': 'pager pager-regular'}).findAll('a')
        last_page = list(map(deleting_html, last_page[-1]))

        try:
            last_page = int(last_page[0]) + 1
        except Exception:
            print('last page  ----- IS NOT A NUMBER')

    # ---how many pages end ---
    try:
        if last_page < quotes_quantity:
            for i in range(1, last_page):
                url = secret.url + param + '?page=' + str(i)
                quote_dict.update(page_data(url,proxies))
        elif last_page >= quotes_quantity:
            for i in range(1, quotes_quantity):
                url = secret.url + param + '?page=' + str(i)
                quote_dict.update(page_data(url, proxies))
    except Exception:
        print('LAST PAGE ERROR')

    return quote_dict
