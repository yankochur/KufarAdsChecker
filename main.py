import os
from dotenv import load_dotenv
import sqlite3
import telebot
import requests
from bs4 import BeautifulSoup as BS

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")


def initialize_database():
    conn = sqlite3.connect('kufar_ads.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kufar_ads (
            id TEXT PRIMARY KEY,
            sent INTEGER DEFAULT 0
        );
    ''')
    conn.commit()
    conn.close()


class BotManager:
    def __init__(self, bot_token):
        self.bot_token = bot_token

        self.bot = telebot.TeleBot(self.bot_token)

class KufarScraper:
    def __init__(self, db_file, bot_manager, chat_id):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.bot_manager = bot_manager


    def scrape(self):
        url = 'https://re.kufar.by/l/brest/snyat/kvartiru'
        has_next_page = True
        started = False

        self.cursor.execute("SELECT id FROM kufar_ads")
        database_content = set(row[0] for row in self.cursor.fetchall())
        ads_on_page = set()

        while has_next_page:
            print('has_next_page')
            response = requests.get(url)
            html = BS(response.content, 'html.parser')
            ads = html.find_all('a', class_='styles_wrapper__Q06m9')

            for ad in ads:
                try:
                    photo = ad.find('img', class_='styles_image__ZPJzx')['src']
                except:
                    photo = 'https://i.pinimg.com/280x280_RS/03/c0/f1/03c0f1485e3be504b0557c0a5d504e64.jpg'
                address = ad.find('span', class_='styles_address__l6Qe_').text
                price = ad.find('span', class_='styles_price__byr__lLSfd').text
                size = ad.find('div', class_='styles_parameters__7zKlL').text
                link = ad['href'].split("?")[0]
                link_id = link.split("/")[-1]
                print(photo, address, price, size, link)
                full_info = (f'НОВОЕ ОБЪЯВЛЕНИЕ: \n\n<b>{price}</b>\n\n{address}\n\n{size}\n\n{link}')


                select_query = """ SELECT * FROM kufar_ads WHERE id = ?; """
                self.cursor.execute(select_query, (link_id,))
                result = self.cursor.fetchone()
                ads_on_page.add(link_id)

                if not result:
                    ins_query = """ INSERT INTO kufar_ads (id, sent) VALUES (?, ?); """
                    self.bot_manager.bot.send_photo(chat_id, photo, full_info, parse_mode='html')
                    self.cursor.execute(ins_query, (link_id, 1))
                    self.conn.commit()
                    ads_on_page.add(link_id)

            arrows = html.find_all('a', class_='styles_link__8m3I9 styles_arrow__LNoLG')
            if len(arrows) == 1:
                next_page_link = arrows[0]
                if not started:
                    started = True
                else:
                    break
            else:
                next_page_link = arrows[1]

            if next_page_link:
                url = 'https://re.kufar.by' + next_page_link['href']
            else:
                has_next_page = False

        ads_on_page = set(map(int, ads_on_page))
        ads_to_remove = database_content - ads_on_page

        delete_query = """DELETE FROM kufar_ads WHERE id IN ({})""".format(','.join("'" + str(id) + "'" for id in ads_to_remove))
        self.cursor.execute(delete_query)
        self.conn.commit()

if __name__ == '__main__':
    initialize_database()
    bot_manager = BotManager(bot_token)
    kufar_scraper = KufarScraper('kufar_ads.db', bot_manager, chat_id)

    kufar_scraper.scrape()
