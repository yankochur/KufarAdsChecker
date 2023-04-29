import requests
import sqlite3
from bs4 import BeautifulSoup as BS


# Буду максимально расписывать для собственного понимания кода.

def main():
    conn = sqlite3.connect('kufar_ads.db')
    cursor = conn.cursor()
    # new_database = """ CREATE TABLE IF NOT EXISTS kufar_ads (id INTEGER) """      # create database
    # cursor.execute(new_database)

    # add_column_in_database = """ ALTER TABLE kufar_ads ADD COLUMN sent INTEGER; """      # create column "sent"
    # cursor.execute(add_column_in_database)

    # add_column_status_in_database = """ ALTER TABLE kufar_ads ALTER COLUMN sent SET DEFAULT 'False'; """      # create column "sent"
    # cursor.execute(add_column_status_in_database)

    # cursor.execute("DELETE FROM kufar_ads")         # delete all from database

    url = 'https://re.kufar.by/l/brest/kupit/kvartiru?cnd=2&cur=USD'        # (with filter)
    has_next_page = True
    started = False
    while has_next_page:
        response = requests.get(url)    # get content from url
        html = BS(response.content, 'html.parser')       # put the content from response
        ads = html.find_all('a', class_='styles_wrapper__KkryZ')         # search in class_


        for ad in ads:
            # adress = ad.find('span', class_='styles_address__dfWQi').text
            # price = ad.find('span', class_='styles_price__byr__FKDpp').text
            # size = ad.find('div', class_='styles_parameters__p2sHq').text
            link = ad['href'].split("?")[0]         # split = split code on "?" symbol (like key[space])
            link_id = link.split("/")[-1]
            # print(adress, '|', price, '|', size, '|', link)

            select_query1 = """ SELECT id FROM kufar_ads WHERE id = ?; """
            cursor.execute(select_query1, (link_id,))
            result = cursor.fetchone()
            if not result:      # check for the existence of the next line in db
                ins_query = """ INSERT INTO kufar_ads (id, sent) VALUES (?, ?); """       # add values into db
                cursor.execute(ins_query, (link_id, 0))

            select_query2 = """SELECT id FROM kufar_ads WHERE sent=0"""              #
            cursor.execute(select_query2)                                            #
            rows = cursor.fetchall()                                                 #
            if len(rows) > 0:                                                        #
                update_query = """UPDATE kufar_ads SET sent=1 WHERE sent=0"""        # use data where sent=0 and assign them sent=1
                cursor.execute(update_query)
                conn.commit()

                # for row in rows:
                #     print(row[0])

        arrows = html.find_all('a', class_='styles_link__3MFs4 styles_arrow__r6dv_')        # step on next pages
        if len(arrows) == 1:                # if links 1 unit
            next_page_link = arrows[0]      # take first[0] link
            if started is False:
                started = True              # and start script
            else:
                break
        else:
            next_page_link = arrows[1]      # else take second[1] link

        if next_page_link:
            url = 'https://re.kufar.by' + next_page_link['href']
        else:
            has_next_page = False

if __name__ == '__main__':
    main()