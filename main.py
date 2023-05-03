import requests
import sqlite3
import configparser
import telebot
from telebot import types
from bs4 import BeautifulSoup as BS


# Буду максимально расписывать для собственного понимания кода.

config = configparser.ConfigParser()
config.read('config.txt')           # make config.txt:
                                    # [DEFAULT]
                                    # bot_token={your_token}
                                    # chat_id={your_chat_id}



bot_token = config.get('DEFAULT', 'bot_token')
chat_id = config.get('DEFAULT', 'chat_id')

bot = telebot.TeleBot('bot_token')

def main():

    print(bot_token, chat_id, 'a')
    conn = sqlite3.connect('kufar_ads.db')
    cursor = conn.cursor()
    # new_database = """ CREATE TABLE IF NOT EXISTS kufar_ads (id INTEGER) """      # create database
    # cursor.execute(new_database)

    # add_column_in_database = """ ALTER TABLE kufar_ads ADD COLUMN sent INTEGER; """      # create column "sent"
    # cursor.execute(add_column_in_database)

    # add_column_status_in_database = """ ALTER TABLE kufar_ads ALTER COLUMN sent SET DEFAULT 'False'; """      # create column "sent"
    # cursor.execute(add_column_status_in_database)

    # cursor.execute("DELETE FROM kufar_ads")         # delete all from database

    url = 'https://re.kufar.by/l/brest/kupit/kvartiru?cnd=2&cur=USD&gbx=b%3A23.605041639404277%2C51.84106358705331%2C24.01702894409179%2C52.1880572948453&oph=1&size=30'        # (with filter)
    has_next_page = True
    started = False
    while has_next_page:
        response = requests.get(url)    # get content from url
        html = BS(response.content, 'html.parser')       # put the content from response
        ads = html.find_all('a', class_='styles_wrapper__KkryZ')         # search in class_

        for ad in ads:
            photo = ad.find('img', class_='styles_image--blur__qdvGq lazyload')['data-src']
            adress = ad.find('span', class_='styles_address__dfWQi').text
            price = ad.find('span', class_='styles_price__byr__FKDpp').text
            size = ad.find('div', class_='styles_parameters__p2sHq').text
            link = ad['href'].split("?")[0]         # split = split code on "?" symbol (like key[space])
            link_id = link.split("/")[-1]
            full_info = (f'НОВОЕ ОБЪЯВЛЕНИЕ: \n\n<b>{price}</b>\n\n{adress}\n\n{size}\n\n{link}')
            # print(full_info)
            # print(photo)

            select_query1 = """ SELECT * FROM kufar_ads WHERE id = ?; """
            cursor.execute(select_query1, (link_id,))
            result = cursor.fetchone()

            if not result:
                ins_query = """ INSERT INTO kufar_ads (id, sent) VALUES (?, ?); """       # add values into db
                bot.send_photo(chat_id, photo, full_info, parse_mode='html')            # A request to the Telegram API was unsuccessful. Error code: 404. Description: Not Found
                print(full_info)
                cursor.execute(ins_query, (link_id, 1))
                conn.commit()

            # select_query2 = """SELECT * FROM kufar_ads WHERE sent=1"""
            # cursor.execute(select_query2)
            # result = cursor.fetchall()
            #
            # for row in result:
            #     bot.send_photo(chat_id, photo, full_info, parse_mode='html')
            #     print(full_info)
            #     update_query = """UPDATE kufar_ads SET sent=0 WHERE id=?"""
            #     cursor.execute(update_query, (row[0],))
            #     conn.commit()                                      this code incorrect

        print(full_info)
        arrows = html.find_all('a', class_='styles_link__3MFs4 styles_arrow__r6dv_')        # step on next pages
        if len(arrows) == 1:                # if links 1 unit
            next_page_link = arrows[0]      # take first[0] link
            if started is False:
                started = True              # and start script
            else:
                pass
        else:
            next_page_link = arrows[1]      # else take second[1] link

        if next_page_link:
            url = 'https://re.kufar.by' + next_page_link['href']
        else:
            has_next_page = False

if __name__ == '__main__':
    main()