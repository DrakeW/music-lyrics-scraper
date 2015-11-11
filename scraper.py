from bs4 import BeautifulSoup
import urllib2
import re
import json

# STEP1: grab song names + artists from billboard top 100 (1965-2015). approx. 5000 songs
song_list = []

billboard_base_url_prefix = "http://www.billboard.com/archive/charts/"
billboard_base_url_postfix = "/hot-100"
year_range = xrange(1965, 2016)

song_list = {}
for i in year_range:
    song_list[i] = []
    billboard_full_url = billboard_base_url_prefix + str(i) + billboard_base_url_postfix
    response = urllib2.urlopen(billboard_full_url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    song_tds = soup.find_all('td', {'class': 'views-field-field-chart-item-song'} )
    artist_tds = soup.find_all('td', {'class': 'views-field-field-chart-item-artist'} )
    for j in xrange(len(song_tds)):
        song_list[i].append({"name": " ".join(song_tds[j].text.split()), "artist": artist_tds[j].text, "lyric": None})

# print(song_list)

# DEBUG
# song_list = {1965: [{'name': 'I Feel Fine', 'artist': 'The Beatles ', 'lyric': None}]}

# STEP2: grab lyric url from song names

# use metrolyrics as our lyric source
site_base_url = "http://www.lyricsfreak.com/"
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
    return lyric_container.text

for year in xrange(1965, 2016):
    with open('song_{0}.json'.format(year), 'w') as fp:
        for song in song_list[year]:
            song['lyric'] = grab_content(lyric_url_hash[song['name']])
        json.dump(song_list[year], fp)

# print song_list

# save data into json file
# with open('song.json', 'w') as fp:
#     json.dump(song_list, fp)
