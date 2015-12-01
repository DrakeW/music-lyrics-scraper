from bs4 import BeautifulSoup
import urllib2
import re
import json
import sys
print sys.argv

START_YEAR = int(sys.argv[1])
END_YEAR = START_YEAR + 1

print "{0}-{1}".format(START_YEAR, END_YEAR)

# STEP1: grab song names + artists from billboard top 100 (1965-2015). approx. 5000 songs
song_list = []

billboard_base_url_prefix = "http://www.billboard.com/archive/charts/"
billboard_base_url_postfix = "/hot-100"
year_range = xrange(START_YEAR, END_YEAR)

song_list = {}
for i in year_range:
    song_list[i]       = []
    billboard_full_url = billboard_base_url_prefix + str(i) + billboard_base_url_postfix
    response           = urllib2.urlopen(billboard_full_url)
    html               = response.read()
    soup               = BeautifulSoup(html, 'html.parser')
    # song_tds = soup.find_all('td', {'class': 'views-field-field-chart-item-song'} )
    # artist_tds = soup.find_all('td', {'class': 'views-field-field-chart-item-artist'} )
    # for j in xrange(len(song_tds)):
    #     song_list[i].append({"name": " ".join(song_tds[j].text.split()), 
    #                          "artist": artist_tds[j].text, 
    #                          "lyric": None})
    odd_dates    = soup.find_all('tr', {'class': 'odd'})
    even_dates   = soup.find_all('tr', {'class': 'even'})
    lst          = list(sum(zip(odd_dates, even_dates), ()))
    if len(odd_dates) > len(even_dates):
        lst.append(odd_dates[len(odd_dates)-1])
    song         = None;
    artist       = None;
    song_index   = -1
    for tr in lst:
        song_td = tr.find('td', {'class': 'views-field-field-chart-item-song'})
        artist_td = tr.find('td', {'class': 'views-field-field-chart-item-artist'})
        if song_td or artist_td:
            song_index += 1
            song_list[i].append({"name": " ".join(song_td.text.split()), 
                                 "artist": artist_td.text, 
                                 "lyric": None,
                                 "num_of_weeks": 1})
        else:
            song_list[i][song_index]["num_of_weeks"] += 1


# print(song_list)

# DEBUG
# song_list = {1965: [{'name': 'I Feel Fine', 'artist': 'The Beatles ', 'lyric': None}]}

# STEP2: grab lyric url from song names

# use metrolyrics as our lyric source
site_base_url = "http://www.lyricsfreak.com"
lyric_base_url = "http://www.lyricsfreak.com/search.php?a=search&type=song&q="

search_url_hash = {}
lyric_url_hash = {}
result = {}

def song_name_preprocess(name):
    return "+".join(name.split())

for year in song_list:
    songs = song_list[year]
    for song_info in songs:
        full_url = lyric_base_url + song_name_preprocess(song_info['name'])
        search_url_hash[song_info['name']] = {"url": full_url, "artist": song_info['artist']}

def grab_lyric_link(url, artist_name):
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    songs_container = soup.find('div', {'class': 'colortable'})
    # if can't find song
    if songs_container:
        songs_container_inside = songs_container.find('tbody')
        # double guard for null value failure
        if songs_container_inside:
            songs_info_list = songs_container_inside.find_all('tr')
            for song_info in songs_info_list:
                info = song_info.find_all('td')
                artist = " ".join(info[0].text.split()[1:])
                # TODO: if no match append results of next page to songs_info_list
                if artist in artist_name:
                    song_url = info[1].find('a')['href']
                    return site_base_url + song_url
    return None

for k in search_url_hash:
    lyric_url_hash[k] = grab_lyric_link(search_url_hash[k]['url'], search_url_hash[k]['artist'])

# print lyric_url_hash

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# STEP 3: grab content
def grab_content(url):
    if not url:
        return "Not Found"
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    lyric_container = soup.find('div', {'id': 'content_h'})
    if not lyric_container:
        return
    # replace <br> with " "
    content_str = re.sub('<br>', ' ', str(lyric_container))
    # replace none word char with space and strip html tags
    content_str = " ".join(re.sub('\W', ' ', strip_tags(content_str)).split())
    return content_str

for year in xrange(START_YEAR, END_YEAR):
    with open('song_{0}.json'.format(year), 'w') as fp:
        for song in song_list[year]:
            song['lyric'] = grab_content(lyric_url_hash[song['name']])
        json.dump(song_list[year], fp)

# print song_list
