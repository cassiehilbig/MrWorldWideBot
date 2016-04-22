import requests
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup


def gizoogleit(to_translate):
    resource = 'http://www.gizoogle.net/textilizer.php'
    #to_translate = 'I have figured out the solution to this problem'
    res = requests.post(resource, data={'translatetext': to_translate})
    soup = BeautifulSoup(res.text, 'html.parser')
    translated = soup.find_all('form')[0].contents[2]

    return translated

# """
# Example:
# import gizoogle
# print(gizoogle.translate('Hey, How are you?'))
# # Will print 'Yo, how tha fuck is yo slick ass?'
# """
# from BeautifulSoup import BeautifulSoup
# import requests
# import json
# URL = 'http://www.gizoogle.net/textilizer.php'
#
# def translate(text):
#     html = requests.post(URL, data={'translatetext': text}).text
#     return BeautifulSoup(html).textarea.contents[0].strip()
#
# print(translate('Hey, How are you?'))

