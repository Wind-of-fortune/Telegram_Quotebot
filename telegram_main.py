import random
import logging
import time

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from read_parsed_file import quotes, authors
import parsing_user_data_slow_but_full
import secret


bot = telegram.Bot(token=secret.token)
bot.setWebhook()
updater = Updater(token=secret.token, request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, workers=4)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class MyPages:
    user = {}


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Это бот отправляет  вам цитаты основываясь на вводных данных,'
                         ' на 1 запрос он выдает 1 цитату.\n\n'
                         'Для получения цитат больше  чем  1, на заданную вами тему, в одном запросе,'
                         '  просто введите символ * и количество цитат,  например - “ясный день” – 1 цитата,'
                         '  “ясный день *7 ” – 7 цитат.\n\nЕсли вы хотите найти цитату не просто содержащую'
                         ' заданный вами текст, а цитату из какой-то книги, фильма,  сериала…, то вам нужно'
                         ' ввести контекст с помощью символа #.Например – отправив сообщение “#южный парк”'
                         ' вы получите цитату из книги “Ричард Хэнли. Южный Парк и Философия”.\n\n'
                         ' Если это не то что вы искали, вам нужно уточнить ваш контекст введя еще раз символ #'
                         ' и ключевое  слово - “#южный парк#мульт” - вы получите цитату из мультфильма южный парк,'
                         ' и конечно можно вывести несколько сообщений используя *  -  “#южный парк#мульт*15”,'
                         '   “#южный парк*8”.\n\nCписок ключевых слов которые можно указывать в качестве'
                         ' дополнительного параметра после ввода 2-го символа #:\n'
                         '1 - человек, автор, деятель, писатель, поэт, музыкант, коипозитор\n'
                         '2 - фильм\n'
                         '3 - сериал\n'
                         '4 - тв, tv, телешоу, передача, шоу, телек, зомбоящик\n'
                         '5 - персонаж, герой\n'
                         '6 - музыка, группа, песня, исполнитель, певец\n'
                         '7- мульт, мультфильм\n'
                         '8 - игра\n'
                         '9 - стихи, поэзия\n'
                         '10- комиксы, комикс\n'
                         '11- притчи, притча\n\n'
                         'Попробуйте сами!!!'
                    )

@run_async
def quote(bot, update):
    def find_star(searh_data):
        searh_number = searh_data.split('*')
        try:
            searh_data = searh_number[0]
            searh_number = int(searh_number[-1])
            if searh_number > 20:
                bot.sendMessage(chat_id=update.message.chat_id, text='Извините но вы ввели слишком большое число,'
                                                                     ' предел это 20 сообщений')
                return False, False
        except Exception:
            bot.sendMessage(chat_id=update.message.chat_id, text='Извините но вы не соблюли формат ввода данных -\n'
                                                                 ' "sometext"\n'
                                                                 ' "sometext*5"\n'
                                                                 ' "#someteg"\n'
                                                                 ' "#someteg*5"\n'
                                                                 ' "#someteg#specialword"\n'
                                                                 ' "#someteg#specialword*5"\n')
            return False, False
        return searh_data, searh_number

    def data_cleaner(data):
        data = data.strip(' ')
        try:
            if data.find('*') != -1:
                searh_data = data.split('*')
                new_data = []
                for i in searh_data:
                    k = i.strip(' ')
                    new_data.append(k)
                data = new_data[0] + '*' + new_data[1]
        except Exception:
            pass

        if data.count('#') > 1:
            data = data[1:]
            try:
                if data.find('#') > 0:
                    searh_data = data.split('#')
                    new_data = []
                    for i in searh_data:
                        k = i.strip(' ')
                        new_data.append(k)
                    data = '#' + new_data[0] + '#' + new_data[1]
            except Exception:
                pass
        return data

    def find_star_user_message(searh_data):
        searh_number = searh_data.split('*')
        searh_data = searh_number[0]
        return searh_data

########################## main ##########################

    def quote_main(user_key):
        print('chat id  --- ', update.message.chat_id)
        searh_data = data_cleaner(str(update.message.text))
        s_data = searh_data

        if user_key is True:
            if searh_data.find('*') != -1:
                s_data = find_star_user_message(searh_data)

            if s_data == MyPages.user[update.message.chat_id]:
                pages_to_ignore = MyPages.user[update.message.chat_id + 999999999]
                pages_ending_dict = MyPages.user[update.message.chat_id + 111111111]
            else:
                pages_to_ignore = []
                pages = []
                pages_ending_dict = {}
        else:
            pages_to_ignore = []
            pages = []
            pages_ending_dict = {}

            if searh_data.find('*') != -1:
                s_data = find_star_user_message(searh_data)


        MyPages.user[update.message.chat_id] = s_data

        searh_number = 1

        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')

        if searh_data[0] == '#':
            searh_data = searh_data[1:]
            if searh_data.find('*') != -1:
                searh_data, searh_number = find_star(searh_data)
            if searh_data is False and searh_number is False:
                return None
            tegs_urls_dict = parsing_user_data_slow_but_full.search_by_teg(searh_data)

            if len(tegs_urls_dict) > 0 and tegs_urls_dict != 'no_links':
                if searh_data.find('#') == -1:
                    try:
                        for key, val in tegs_urls_dict.items():
                            teg = key
                            break
                        url_link = parsing_user_data_slow_but_full.transform_val_back(teg, tegs_urls_dict)
                        quote_dict, pages, pages_ending_dict = parsing_user_data_slow_but_full.main_func(
                                                                                            url_link,
                                                                                            searh_number,
                                                                                            pages_to_ignore,
                                                                                            pages_ending_dict)
                        MyPages.user[update.message.chat_id + 111111111] = pages_ending_dict
                        if pages == 'Вы прочитали все цитаты':
                            MyPages.user[update.message.chat_id + 999999999] = 'Вы прочитали все цитаты'
                        else:
                            pages_to_ignore = set(pages_to_ignore)
                            pages = set(pages)
                            union_pages = list(pages_to_ignore | pages)
                            pages_to_ignore = list(pages_to_ignore)
                            pages = list(pages)
                            MyPages.user[update.message.chat_id + 999999999] = union_pages
                    except Exception:
                        rand = random.randint(0, len(quotes))
                        random_quote = quotes[rand]
                        quote_author = authors[rand]
                        bot.send_message(chat_id=update.message.chat_id,
                                         text='Извините, но я не нашел цитат по вашему запросу, ' +
                                              'отправлю вам одну из моих любимых цитат, '
                                              'чтобы вы не расстраивались :\n \n \n' +
                                              random_quote + '\n' + '\n' + quote_author
                                         )
                        return None
                    item = []
                    try:
                        for key, val in quote_dict.items():
                            i = key + '\n' + '\n' + val
                            item.append(i)
                    except Exception:
                        pass

                    try:
                        if pages == 'Вы прочитали все цитаты' and pages_ending_dict == {}:
                            MyPages.user[update.message.chat_id + 999999999] = []
                            pages = []
                            for i in range(len(item)):
                                if len(item[i].encode('utf8')) >= 512:
                                    bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                    if i != len(item) - 1:
                                        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                        time.sleep(5)
                                        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                        time.sleep(5)
                                    else:
                                        time.sleep(5)
                                else:
                                    bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                if i != len(item) - 1:
                                    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                    time.sleep(4)
                            bot.send_message(chat_id=update.message.chat_id,
                                             text='#########################################\n'
                                                  'Вы прочитали все цитаты по данному запросу, '
                                                  'при аналогичном запросе цитаты будут повторяться,'
                                             )
                            return None
                    except Exception:
                        pages = []

                    if searh_number > 0 and len(item) > 0:
                        if len(item) <= searh_number:
                            for i in range(len(item)):
                                if len(item[i].encode('utf8')) >= 512:
                                    bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                    if i != len(item) - 1:
                                        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                        time.sleep(5)
                                        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                        time.sleep(5)
                                    else:
                                        time.sleep(5)
                                else:
                                    bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                if i != len(item) - 1:
                                    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                    time.sleep(4)
                    else:
                        rand = random.randint(0, len(quotes))
                        random_quote = quotes[rand]
                        quote_author = authors[rand]
                        bot.send_message(chat_id=update.message.chat_id,
                                         text='Извините, но я не нашел цитат по вашему запросу, ' +
                                              'отправлю вам одну из моих любимых цитат, '
                                              'чтобы вы не расстраивались :\n \n \n' +
                                              random_quote + '\n' + '\n' + quote_author
                                         )

                    t2 = time.perf_counter()
                    # print('TIME   -----> ', t2 - t1)
                    return quote_dict

                else:
                    teg = searh_data.split('#')
                    teg = teg[-1]
                    for key, val in tegs_urls_dict.items():
                        if key.find(teg + ',') != -1:
                            try:
                                url_link = parsing_user_data_slow_but_full.transform_val_back(teg + ',',
                                                                                              tegs_urls_dict)

                                quote_dict, pages, pages_ending_dict = parsing_user_data_slow_but_full.main_func(
                                                                                                url_link,
                                                                                                searh_number,
                                                                                                pages_to_ignore,
                                                                                                pages_ending_dict)
                                MyPages.user[update.message.chat_id + 111111111] = pages_ending_dict
                                if pages == 'Вы прочитали все цитаты':
                                    MyPages.user[update.message.chat_id + 999999999] = 'Вы прочитали все цитаты'
                                else:
                                    pages_to_ignore = set(pages_to_ignore)
                                    pages = set(pages)
                                    union_pages = list(pages_to_ignore | pages)
                                    pages_to_ignore = list(pages_to_ignore)
                                    pages = list(pages)
                                    MyPages.user[update.message.chat_id + 999999999] = union_pages
                            except Exception:
                                rand = random.randint(0, len(quotes))
                                random_quote = quotes[rand]
                                quote_author = authors[rand]
                                bot.send_message(chat_id=update.message.chat_id,
                                                 text='Извините, но я не нашел цитат по вашему запросу, ' +
                                                      'отправлю вам одну из моих любимых цитат, '
                                                      'чтобы вы не расстраивались :\n \n \n' +
                                                      random_quote + '\n' + '\n' + quote_author
                                                 )
                                return None

                            item = []
                            try:
                                for key, val in quote_dict.items():
                                    i = key + '\n' + '\n' + val
                                    item.append(i)
                            except Exception:
                                pass

                            try:
                                if pages == 'Вы прочитали все цитаты' and pages_ending_dict == {}:
                                    MyPages.user[update.message.chat_id + 999999999] = []
                                    pages = []
                                    for i in range(len(item)):
                                        if len(item[i].encode('utf8')) >= 512:
                                            bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                            if i != len(item) - 1:
                                                bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                                time.sleep(5)
                                                bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                                time.sleep(5)
                                            else:
                                                time.sleep(5)
                                        else:
                                            bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                        if i != len(item) - 1:
                                            bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                            time.sleep(4)
                                    bot.send_message(chat_id=update.message.chat_id,
                                                     text='#########################################\n'
                                                          'Вы прочитали все цитаты по данному запросу, '
                                                          'при аналогичном запросе цитаты будут повторяться,'
                                                     )
                                    return None
                            except Exception:
                                pages = []

                            if searh_number > 0 and len(item) > 0:
                                if len(item) <= searh_number:
                                    for i in range(len(item)):
                                        if len(item[i].encode('utf8')) >= 512:
                                            bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                            if i != len(item) - 1:
                                                bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                                time.sleep(5)
                                                bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                                time.sleep(5)
                                            else:
                                                time.sleep(5)
                                        else:
                                            bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                                        if i != len(item) - 1:
                                            bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                                            time.sleep(4)
                            else:
                                rand = random.randint(0, len(quotes))
                                random_quote = quotes[rand]
                                quote_author = authors[rand]
                                bot.send_message(chat_id=update.message.chat_id,
                                                 text='Извините, но я не нашел цитат по вашему запросу, ' +
                                                      'отправлю вам одну из моих любимых цитат, '
                                                      'чтобы вы не расстраивались :\n \n \n' +
                                                      random_quote + '\n' + '\n' + quote_author
                                                 )

                            t2 = time.perf_counter()
                            # print('TIME   -----> ', t2 - t1)
                            return quote_dict
            else:
                rand = random.randint(0, len(quotes))
                random_quote = quotes[rand]
                quote_author = authors[rand]
                bot.send_message(chat_id=update.message.chat_id,
                                 text='Извините, но я не нашел цитат по вашему запросу, ' +
                                      'отправлю вам одну из моих любимых цитат, '
                                      'чтобы вы не расстраивались :\n \n \n' +
                                      random_quote + '\n' + '\n' + quote_author
                                 )
                return None

        if searh_data.find('*') != -1:
            searh_data, searh_number = find_star(searh_data)
        if searh_data is False and searh_number is False:
            return None
        ##########################
        try:
            quote_dict, pages, pages_ending_dict = parsing_user_data_slow_but_full.main_func(
                'search/site/' + searh_data,
                searh_number,
                pages_to_ignore,
                pages_ending_dict)
            MyPages.user[update.message.chat_id + 111111111] = pages_ending_dict
            if pages == 'Вы прочитали все цитаты':
                MyPages.user[update.message.chat_id + 999999999] = 'Вы прочитали все цитаты'
            else:
                pages_to_ignore = set(pages_to_ignore)
                pages = set(pages)
                union_pages = list(pages_to_ignore | pages)
                pages_to_ignore = list(pages_to_ignore)
                pages = list(pages)
                MyPages.user[update.message.chat_id + 999999999] = union_pages
        except Exception:
            rand = random.randint(0, len(quotes))
            random_quote = quotes[rand]
            quote_author = authors[rand]
            bot.send_message(chat_id=update.message.chat_id,
                             text='Извините, но я не нашел цитат по вашему запросу, ' +
                                  'отправлю вам одну из моих любимых цитат, '
                                  'чтобы вы не расстраивались :\n \n \n' +
                                  random_quote + '\n' + '\n' + quote_author
                             )
            return None

        item = []
        try:
            for key, val in quote_dict.items():
                i = key + '\n' + '\n' + val
                item.append(i)
        except Exception:
            pass

        try:
            if pages == 'Вы прочитали все цитаты' and pages_ending_dict == {}:
                MyPages.user[update.message.chat_id + 999999999] = []
                pages = []
                for i in range(len(item)):
                    if len(item[i].encode('utf8')) >= 512:
                        bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                        if i != len(item) - 1:
                            bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                            time.sleep(5)
                            bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                            time.sleep(5)
                        else:
                            time.sleep(5)
                    else:
                        bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                    if i != len(item) - 1:
                        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                        time.sleep(4)
                bot.send_message(chat_id=update.message.chat_id,
                                 text='#########################################\n'
                                      'Вы прочитали все цитаты по данному запросу, '
                                      'при аналогичном запросе цитаты будут повторяться,'
                                 )
                return None
        except Exception:
            pages = []

        if searh_number > 0 and len(item) > 0:
            if len(item) <= searh_number:
                for i in range(len(item)):
                    if len(item[i].encode('utf8')) >= 512:
                        bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                        if i != len(item) - 1:
                            bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                            time.sleep(5)
                            bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                            time.sleep(5)
                        else:
                            time.sleep(5)
                    else:
                        bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
                    if i != len(item) - 1:
                        bot.sendChatAction(chat_id=update.message.chat_id, action='typing')
                        time.sleep(4)
        else:
            rand = random.randint(0, len(quotes))
            random_quote = quotes[rand]
            quote_author = authors[rand]
            bot.send_message(chat_id=update.message.chat_id,
                             text='Извините, но я не нашел цитат по вашему запросу, ' +
                                  'отправлю вам одну из моих любимых цитат, '
                                  'чтобы вы не расстраивались :\n \n \n' +
                                  random_quote + '\n' + '\n' + quote_author
                             )
        t2 = time.perf_counter()
        # print('TIME   -----> ', t2 - t1)
        return quote_dict

###### ------ sub_functions ends ----------------- #####

    try:
        id = MyPages.user[update.message.chat_id]
        quote_main(True)
    except KeyError:
        quote_main(False)


   #####################################################################################################


def unknown(bot, update):
    rand = random.randint(0, len(quotes))
    random_quote = quotes[rand]
    quote_author = authors[rand]
    bot.send_message(chat_id=update.message.chat_id, text='Извините, но я могу искать только текст, ' +
                                                          'отправлю вам одну из моих любимых цитат, '
                                                          'чтобы вы не расстраивались :\n \n \n' +
                                                          random_quote + '\n' + '\n' + quote_author)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

quote_handler = MessageHandler(Filters.text, quote)
dispatcher.add_handler(quote_handler, group=0)

unknown_handler = MessageHandler(Filters.all, unknown)
dispatcher.add_handler(unknown_handler, group=0)


app = updater.start_polling()
