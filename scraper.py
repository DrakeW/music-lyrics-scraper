from bs4 import BeautifulSoup
import urllib2

while (True):
    # read from user keyboard input, multiple songs are separated by ','
    songs = raw_input('Enter song name: ').split(',')

    base_url = "http://search.azlyrics.com/search.php?q="

    # song_list = ['I Feel Fine', 'Come See About Me']
    song_list = []
    song_list.extend(songs)

    search_url_hash = {}
    lyric_url_hash = {}
    result = {}

    def song_name_preprocess(name):
        return "+".join(name.split())

    for song_name in song_list:
        full_url = base_url + song_name_preprocess(song_name)
        search_url_hash[song_name] = full_url

    def grab_lyric_link(url):
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all('a', {'target': '_blank'})[0]['href']


    for k in search_url_hash:
        lyric_url_hash[k] = grab_lyric_link(search_url_hash[k])

    def grab_content(url):
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')
        lyric_container = soup.find('div', {'class': 'col-xs-12 col-lg-8 text-center'})
        return lyric_container.find_all('div')[7]

    for k in lyric_url_hash:
        print lyric_url_hash[k]
        result[k] = grab_content(lyric_url_hash[k])

    print result
