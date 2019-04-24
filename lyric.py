import requests
from lxml import etree
import simplejson
import re
import operator
from functools import reduce

ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
headers = {
    'User-agent': ua
}


class CrawlerLyric:
    def __init__(self):
        self.author_name = ""

    def get_url_html(self, url):
        with requests.Session() as session:
            response = session.get(url, headers=headers)
            text = response.text
            html = etree.HTML(text)
        return html

    def get_url_json(self, url):

        with requests.Session() as session:
            response = session.get(url, headers=headers)
            text = response.text
            text_json = simplejson.loads(text)
        return text_json

    def parse_song_id(self, html):

        song_ids = html.xpath("//ul[@class='f-hide']//a/@href")
        song_names = html.xpath("//ul[@class='f-hide']//a/text()")
        self.author_name = html.xpath('//title/text()')
        song_ids = [ids[9:len(ids)] for ids in song_ids]
        return self.author_name, song_ids, song_names

    def parse_lyric(self, text_json):
        try:
            lyric = text_json.get('lrc').get('lyric')
            regex = re.compile(r'\[.*\]')
            final_lyric = re.sub(regex, '', lyric).strip()
            return final_lyric
        except AttributeError as k:
            print(k)
            pass

    def get_album(self, html):
        album_ids = html.xpath("//ul[@id='m-song-module']/li/p/a/@href")
        album_names = html.xpath("//ul[@id='m-song-module']/li/p/a/text()")
        album_ids = [ids.split('=')[-1] for ids in album_ids]
        return album_ids, album_names

    def get_top50(self, sing_id):
        url_singer = 'https://music.163.com/artist?id=' + str(sing_id)  # 陈奕迅
        html_50 = self.get_url_html(url_singer)
        author_name, song_ids, song_names = self.parse_song_id(html_50)
        # print(author_name, song_ids, song_names)
        for song_id, song_name in zip(song_ids, song_names):
            url_song = 'http://music.163.com/api/song/lyric?' + 'id=' + str(song_id) + '&lv=1&kv=1&tv=-1'
            json_text = self.get_url_json(url_song)
            print(song_name)
            print(self.parse_lyric(json_text))
            print('-' * 30)

    def get_all_song_id(self, album_ids):

        with requests.Session() as session:
            all_song_ids, all_song_names = [], []
            for album_id in album_ids:
                one_album_url = "https://music.163.com/album?id=" + str(album_id)
                response = session.get(one_album_url, headers=headers)
                text = response.text
                html = etree.HTML(text)
                album_song_ids = html.xpath("//ul[@class='f-hide']/li/a/@href")
                album_song_names = html.xpath("//ul[@class='f-hide']/li/a/text()")
                album_song_ids = [ids.split('=')[-1] for ids in album_song_ids]

                all_song_ids.append(album_song_ids)
                all_song_names.append(album_song_names)

        return all_song_ids, all_song_names

    def get_all_song_lyric(self, singer_id):
        album_url = "https://music.163.com/artist/album?id=" + str(singer_id) + "&limit=150&offset=0"
        html_album = self.get_url_html(album_url)
        album_ids, album_names = self.get_album(html_album)
        all_song_ids, all_song_names = self.get_all_song_id(album_ids)
        all_song_ids = reduce(operator.add, all_song_ids)
        all_song_names = reduce(operator.add, all_song_names)
        print(all_song_ids)
        print(all_song_names)
        for song_id, song_name in zip(all_song_ids, all_song_names):
            url_song = 'http://music.163.com/api/song/lyric?' + 'id=' + str(song_id) + '&lv=1&kv=1&tv=-1'
            json_text = self.get_url_json(url_song)
            print(song_name)
            try:
                with open('D:/lyric/陈奕迅/' + str(song_name) + ".txt", 'w+') as f:
                    f.write(self.parse_lyric(json_text))
                    # print(song_name)
                    # print(self.parse_lyric(json_text))
                    # print('-' * 30)
            except Exception as e:
                pass


if __name__ == "__main__":
    sing_id = '2116'  # 陈奕迅
    sing_id_chenli = '1007170'  # 陈粒
    c = CrawlerLyric()
    c.get_all_song_lyric(sing_id_chenli)
