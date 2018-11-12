import requests
import re
import math
import random

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

    if url.find('search') == -1:
        quotes = soup.find('div', {'class': 'view-content'}).findAll('article')
    else:
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
            data_authors = re.findall(r'title=".*"', k)
            for j in data_authors:
                k = j
                k = k.split('title="Поделиться"')
                k = k[0]
                try:
                    k = k.split('node__')
                    authors.append(k[0])
                except Exception:
                    authors.append(k)

    new_quotes = list(map(deleting_html, filterted_quotes))
    new_quotes = list(map(deleting_others, new_quotes))
    new_quotes = list(map(quotes_explanation, new_quotes))

    # -- authors filtering -----
    if authors == [[]]*len(authors) or authors == ['']*len(authors):
        try:
            author = soup.find('h1')
            author = list(map(deleting_html, author))
            for i in range(len(authors)):
                authors[i] = author[0]
        except Exception as err:
            print('ERR ---', err)
            pass
    else:
        a_list = authors
        authors = ['']
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
                        i[0] = i[0] + ' & '
                    if len(i) > 2:
                        i[1] = i[1] + ' & '
                    if len(i) > 3:
                        i[2] = i[2] + ' & '
                    if len(i) > 4:
                        i[3] = i[3] + ' & '
                    if len(i) > 5:
                        i[4] = i[4] + ' & '
                    if len(i) > 6:
                        i[5] = i[5] + ' & '

        for i in a_list:
            if i != 'Автор неизвестен':
                k = k.join(i)
                authors.append(k)
                k = ''
            else:
                authors.append(i)

    authors.pop(0)
    authors = list(map(del_authors_dop, authors))

    return (dict(zip(new_quotes, authors)))


def pages_quantity(url, proxies):
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
        last_page = 0
        print('ERROR  --- ', err)

    try:
        if last_page > 1:
            new_url = url + '?page=' + str(100000)
            # print(new_url)
            r = requests.get(new_url, proxies=proxies)
            soup = BeautifulSoup(r.content, features="html.parser")
            last_page = soup.find('ul', {'class': 'pager pager-regular'}).findAll('a')
            last_page = list(map(deleting_html, last_page[-1]))

            try:
                last_page = int(last_page[0]) + 1
            except Exception:
                print('last page  ----- IS NOT A NUMBER')
    except Exception:
        last_page = 0
    # print('last_page ---', last_page)
    return last_page

# ------ end function block -------

# ------ main block -------


def search_by_teg(param):
    proxies = secret.proxies
    url = secret.url + 'search/site/' + param

    r = requests.get(url, proxies=proxies)
    soup = BeautifulSoup(r.content, features="html.parser")

    links_list = []
    new_list = []
    new_dict = {}
    quote_dict = {}
    count = 0

    try: # search__results
        for i in soup.find('div', {'class': 'search__results'}).findAll('a'):
            if 'href' in i.attrs:
                # print(i.attrs['href'])
                links_list.append( i.attrs['href'])

        for i in links_list:
            k = i[1:]
            k = k.split('/')
            k[1] = i
            new_list.append(k)

        for i in new_list:
            if count == 0:
                new_dict[i[0]] = i[1]
            else:
                try:
                    some = new_dict[i[0]]
                except KeyError:
                    new_dict[i[0]] = i[1]
            count += 1

        for key, val in new_dict.items():
            nkey = key
            if key == 'man':
                nkey = 'человек, автор, деятель, писатель, поэт, музыкант, режиссер, композитор,'
            if key == 'film':
                nkey = 'фильм,'
            if key == 'serial':
                nkey = 'сериал,'
            if key == 'tv':
                nkey = 'тв, tv, телешоу, передача, шоу, телек, зомбоящик,'
            if key == 'character':
                nkey = 'персонаж, герой,'
            if key == 'music':
                nkey = 'музыка, группа, песня, исполнитель, певец,'
            if key == 'book':
                nkey = 'книга,'
            if key == 'anime':
                nkey = 'аниме,'
            if key == 'mult':
                nkey = 'мульт, мультфильм,'
            if key == 'game':
                nkey = 'игра,'
            if key == 'poetry':
                nkey = 'стихи, поэзия,'
            if key == 'comics':
                nkey = 'комиксы, комикс,'
            if key == 'pritchi':
                nkey = 'притчи, притча,'
            quote_dict[nkey] = val

    except Exception as err:
        print(err)
        return 'no_links'

    return quote_dict

def transform_val_back(teg, di):
    for key, val in di.items():
        if key.find(teg) != -1:
            return val

def random_choice(last_page):
    if last_page > 0:
        random_page = random.randint(0, last_page - 1)
    else:
        random_page = 0

    if random_page == last_page - 1:
            random_choice(last_page)
            random_page = last_page - 1
    return random_page



def page_compare (random_last, last_page):
    exeption = 0
    if len(random_last) == last_page:
        return 'Вы прочитали все цитаты', exeption

    k=0

    if last_page > 2:
        random_page = random.randint(0, last_page - 2)
    else:
        random_page = random.randint(0, last_page - 1)


    if last_page - 1 > len(random_last):
        while k != len(random_last):
            random_page = random.randint(0, last_page - 2)
            if len(random_last) > 0:
                for i in random_last:
                    k += 1
                    if i == random_page:
                        k=0
    else:
        random_page = last_page - 1
        exeption = 'Вы прочитали все цитаты'

    return random_page, exeption


def main_func(param, quotes_quantity, pages_to_ignore, pages_ending_dict):

    proxies = secret.proxies
    url = secret.url + param

    last_page = pages_quantity(url, proxies)

    quote_dict = {}

    quotes_quantity_ceil = int(math.ceil(quotes_quantity/10))
    random_last = pages_to_ignore
    # print('R_LAST === ', random_last)

    # print('LAST PAGE', last_page, 'quotes_quantity_ceil  ---- ', quotes_quantity_ceil)
    for i in range(0, quotes_quantity_ceil):
        random_page = 999
        #random_page = random_choice(last_page)
        try:
            if random_last == 'Вы прочитали все цитаты':
                quote_dict = pages_ending_dict
                new_quote_dict = {}
                pages_ending_dict = {}

                # print('LEN_QUOTE_Dict', len(quote_dict))
                if len(quote_dict) < quotes_quantity:
                    return quote_dict, random_last, pages_ending_dict
                else:
                    for key, val in quote_dict.items():
                        if len(new_quote_dict) < quotes_quantity:
                            new_quote_dict[key] = val
                        else:
                            pages_ending_dict[key] = val
                    return new_quote_dict, random_last, pages_ending_dict

            random_page, exeption = page_compare(random_last, last_page)
            if random_page == 0:
                url = secret.url + param
                quote_dict.update(page_data(url, proxies))
            else:
                url = secret.url + param + '?page=' + str(random_page)
                quote_dict.update(page_data(url, proxies))
            # print('RANDOM PAGE  - ', random_page)
            # print('exeption  -- ',exeption)

            if random_page == 'Вы прочитали все цитаты' or exeption == 'Вы прочитали все цитаты':
                random_page = 'Вы прочитали все цитаты'

                quote_dict.update(pages_ending_dict)
                new_quote_dict = {}
                pages_ending_dict = {}
                if len(quote_dict) < quotes_quantity:
                    return quote_dict, random_page, pages_ending_dict
                else:
                    for key, val in quote_dict.items():
                        if len(new_quote_dict) < quotes_quantity:
                            new_quote_dict[key] = val
                        else:
                            pages_ending_dict[key] = val
                    # print('new_qoute dict  --  ', len(new_quote_dict))
                    # print('pages_ending_dict --  ', len(pages_ending_dict))
                    return new_quote_dict, random_page, pages_ending_dict

            random_last.append(random_page)

            if len(quote_dict) > quotes_quantity:
                break
        except Exception:
            random_last.append(random_page)

    new_quote_dict = {}
    # print('random_last  ---- ', random_last)

    for key, val in quote_dict.items():
        if len(new_quote_dict) < quotes_quantity:
            new_quote_dict[key] = val
        else:
            pages_ending_dict[key] = val

    # print('quote_dict --- ', len(quote_dict))
    # print('new_quote_dict  ---- ', len(new_quote_dict))
    # print('pages_ending_dict  ---  ', len(pages_ending_dict))
    # print('quotes_quantity ---- ', quotes_quantity)
    return new_quote_dict, random_last, pages_ending_dict

