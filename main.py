import requests
from bs4 import BeautifulSoup as BS


# Буду максимально расписывать для собственного понимания кода.


url = 'https://re.kufar.by/l/brest/kupit/kvartiru?cnd=2&cur=USD'        # (with filter)


response = requests.get(url)    # get content from url
html = BS(response.content, 'html.parser')       # put the content from response
ads = html.find_all('a', class_='styles_wrapper__KkryZ')         # search in class_


for ad in ads:
    adress = ad.find('span', class_='styles_address__dfWQi').text
    price = ad.find('span', class_='styles_price__byr__FKDpp').text
    size = ad.find('div', class_='styles_parameters__p2sHq').text
    print(adress, '|', price, '|', size)