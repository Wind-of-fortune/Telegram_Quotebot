import random
import logging
import time

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from read_parsed_file import quotes, authors
import parsing_user_data_slow_but_full
import parsing_user_data_fast_but_not_full
import secret

bot = telegram.Bot(token=secret.token)
updater = Updater(token=secret.token)
dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class MyState(object):
    q_dict = {}
    user_last_message = ''

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Просто введите любое слово или словосочетание ' +
                    'и я отправлю вам цитату на заданную вами тему'
                    )

def quote(bot, update):
    t1 = time.perf_counter()

    q_dict = MyState.q_dict
    user_last_message = MyState.user_last_message

    searh_data = str(update.message.text)
    searh_number = 0

    bot.sendChatAction(chat_id=update.message.chat_id, action='typing')

    if searh_data.find('*') != -1:
        searh_number = searh_data.split('*')
        try:
            searh_data = searh_number[0]
            searh_number = int(searh_number[-1])
            if searh_number > 29:
                bot.sendMessage(chat_id=update.message.chat_id, text='Извините но вы ввели слишком большое число,'
                                                                     ' предел это 29 сообщений')
                return None
        except Exception:
            bot.sendMessage(chat_id=update.message.chat_id, text='Извините но вы не соблюли формат ввода данных -,'
                                                                 ' "sometext *5"')
            return None

    if user_last_message == update.message.text:
        if len(q_dict) > 0:
            item = []
            try:
                for key, val in q_dict.items():
                    i = key + '\n' + '\n' + val
                    item.append(i)
            except Exception:
                pass
            if len(item) > 0:
                it = item[random.randint(0, len(item)-1)]
                bot.sendMessage(chat_id=update.message.chat_id, text=it)
            else:
                rand = random.randint(0, len(quotes))
                random_quote = quotes[rand]
                quote_author = authors[rand]
                bot.send_message(chat_id=update.message.chat_id, text='Извините, но я не нашел цитат по вашему запросу, ' +
                                                                      'отправлю вам одну из моих любимых цитат, '
                                                                      'чтобы вы не расстраивались :\n \n \n' +
                                                                      random_quote + '\n' + '\n' + quote_author
                                 )

            t2 = time.perf_counter()
            print('TIME   -----> ', t2 - t1)
            MyState.q_dict = q_dict
            return q_dict

    ##########################

    try:
        if searh_number < 10:
            quote_dict = parsing_user_data_fast_but_not_full.main_func(searh_data)
        else:
            quote_dict = parsing_user_data_slow_but_full.main_func(searh_data, searh_number)
    except Exception:
        rand = random.randint(0, len(quotes))
        random_quote = quotes[rand]
        quote_author = authors[rand]
        bot.send_message(chat_id=update.message.chat_id, text='Извините, но я не нашел цитат по вашему запросу, ' +
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

    if searh_number > 0 and len(item) > 1:
        if len(item) <= searh_number:
            for i in range(len(item)):
                bot.sendMessage(chat_id=update.message.chat_id, text=item[i])
        else:
            for i in range(searh_number-1):
                bot.sendMessage(chat_id=update.message.chat_id, text=item[i])

    if len(item) > 0:
        it = item[random.randint(0, len(item)-1)]
        bot.sendMessage(chat_id=update.message.chat_id, text=it)
    else:
        rand = random.randint(0, len(quotes))
        random_quote = quotes[rand]
        quote_author = authors[rand]
        bot.send_message(chat_id=update.message.chat_id, text='Извините, но я не нашел цитат по вашему запросу, ' +
                                                              'отправлю вам одну из моих любимых цитат, '
                                                              'чтобы вы не расстраивались :\n \n \n' +
                                                              random_quote + '\n' + '\n' + quote_author
                        )

    q_dict = quote_dict
    MyState.q_dict = q_dict
    MyState.user_last_message = searh_data
    t2 = time.perf_counter()
    print('TIME   -----> ', t2 - t1)

    return q_dict


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


updater.start_polling()