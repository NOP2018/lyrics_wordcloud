# coding:utf-8
# 引入相关库包
import requests
import sys
import re
import os
import jieba
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image # PIL不支持python3.x, 安装pillow，但仍调用PIL
from lxml import etree

# 请求头 （开发者工具->network->点击name的第一项）
headers = {
    'Host': 'music.163.com',
    'Origin': 'https://music.163.com',
    'Referer': 'https://music.163.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
}

# 获取指定歌手页面热门歌曲id，歌曲名称
def get_songs(artist_id):
    page_url = 'https://music.163.com/artist?id=' + artist_id
    res = requests.request('GET', page_url, headers=headers)
    html = etree.HTML(res.text)
    # xpath解析html
    id_xpath = "//*[@id='hotsong-list']//a/@href"
    name_xpath = "//*[@id='hotsong-list']//a/text()"
    ids = html.xpath(id_xpath)
    names = html.xpath(name_xpath)
    song_ids = []
    song_names = []
    for id, name in zip(ids, names):
        song_ids.append(id[9:])
        song_names.append(name)
        print(id, '  ', name)

    return song_ids, song_names

# 获取歌词
def get_song_lyric(headers, lyric_url):
    res = requests.request('GET', lyric_url, headers=headers)
    if 'lrc' in res.json():
        lyric = res.json()['lrc']['lyric']
        # 删除歌词时间信息
        new_lyric = re.sub(r'[\d:.[\]]','',lyric)
        return new_lyric
    else:
        return ''
        print(res.json())

# 去掉停用词
def remove_stop_words(f):
	stop_words = ['作词', '作曲', '编曲', 'Arranger', '录音', '混音', '人声', 'Vocal', '弦乐', 'Keyboard', '键盘', '编辑', '助理', 'Assistants', 'Mixing', 'Editing', 'Recording', '音乐', '制作', 'Producer', '发行', 'produced', 'and', 'distributed']
	for stop_word in stop_words:
		f = f.replace(stop_word, '')
	return f

# 生成词云
def create_word_cloud(f):
	print('根据词频，开始生成词云!')
	f = remove_stop_words(f)
	cut_text = " ".join(jieba.cut(f,cut_all=False, HMM=True))
	wc = WordCloud(
        # 字体文件需要放入项目目录中，否则报OSError
		font_path="SimHei.ttf",
		max_words=100,
		width=2000,
		height=1200,
    )
	print(cut_text)
	wordcloud = wc.generate(cut_text)
	wordcloud.to_file("wordcloud.jpg")
	plt.imshow(wordcloud)
	plt.axis("off")
	plt.show()

# 设置歌手id，周杰伦id=6452
artist_id = '6452'
[song_ids, song_names] = get_songs(artist_id)

# 所有歌词
all_word = ''
# 获取每首歌歌词
for (song_id, song_name) in zip(song_ids, song_names):
	# 歌词API URL
	lyric_url = 'http://music.163.com/api/song/lyric?os=pc&id=' + song_id + '&lv=-1&kv=-1&tv=-1'
	lyric = get_song_lyric(headers, lyric_url)
	all_word = all_word + ' ' + lyric
	print(song_name)

#根据词频 生成词云
create_word_cloud(all_word)