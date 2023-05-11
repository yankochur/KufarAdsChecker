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

bot = telebot.TeleBot(bot_token)

def main():
    conn = sqlite3.connect('kufar_ads.db')
    cursor = conn.cursor()

    # cursor.execute("DELETE FROM kufar_ads")         # delete all from database

    url = 'https://re.kufar.by/l/brest/kupit/kvartiru?cnd=2&cur=USD&oph=1'
    has_next_page = True
    started = False

    cursor.execute("SELECT id FROM kufar_ads")
    database_content = set(row[0] for row in cursor.fetchall())
    ads_on_page = set()

    while has_next_page:
        response = requests.get(url)    # get content from url
        html = BS(response.content, 'html.parser')       # put the content from response
        ads = html.find_all('a', class_='styles_wrapper__KkryZ')

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
            ads_on_page.add(link_id)

            if not result:
                ins_query = """ INSERT INTO kufar_ads (id, sent) VALUES (?, ?); """
                bot.send_photo(chat_id, photo, full_info, parse_mode='html')
                cursor.execute(ins_query, (link_id, 1))
                conn.commit()
                ads_on_page.add(link_id)


        arrows = html.find_all('a', class_='styles_link__3MFs4 styles_arrow__r6dv_')        # step on next pages
        if len(arrows) == 1:
            next_page_link = arrows[0]
            if started is False:        #
                started = True          #

            else:                       #
                break                   # break cycle on last page

        else:
            next_page_link = arrows[1]

        if next_page_link:
            url = 'https://re.kufar.by' + next_page_link['href']
        else:
            has_next_page = False

    # ids_to_remove = database_content.intersection(ids_on_page)

    ads_on_page = set(map(int, ads_on_page))
    ads_to_remove = database_content - ads_on_page

    # print(database_content)
    # print(ads_on_page)
    # print(ads_to_remove)          test

    delete_query = """DELETE FROM kufar_ads WHERE id IN ({})""".format(','.join("'" + str(id) + "'" for id in ads_to_remove))
    cursor.execute(delete_query)
    conn.commit()

if __name__ == '__main__':
    main()







