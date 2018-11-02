import io
import random

f = io.open(r'quotes_filtering.txt', 'r',  encoding="utf-8")

read_data = f.read()
data=[]
quotes = []
authors = []
a = ''

for i in read_data:
    if i != '\n':
        a += i
    else:
        data.append(a)
        a = ''

f.close()
a = 0

for i in data:
    a += 1
    if a % 2:
        quotes.append(i)
    else:
        authors.append(i)

if __name__ == '__main__':
    print(quotes)
    print(authors)
