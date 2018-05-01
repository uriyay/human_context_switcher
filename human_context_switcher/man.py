import urllib
import bs4

MAN_PAGES_URL = 'http://man.he.net/?topic={0}&section={1}'

def get_man_page(topic, section=None):
    if section is None:
        section = 'all'
    else:
        section = str(section)
    data = urllib.request.urlopen(MAN_PAGES_URL.format(topic, section)).read()
    soup = bs4.BeautifulSoup(data, 'html.parser')
    return soup.getText()
