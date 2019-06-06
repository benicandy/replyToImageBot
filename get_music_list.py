# -*- coding: utf-8 -*-
import urllib.request as req
from bs4 import BeautifulSoup

url = "https://chunithm.gamerch.com/CHUNITHM%20AMAZON%20PLUS%20%E6%A5%BD%E6%9B%B2%E4%B8%80%E8%A6%A7%EF%BC%88Lv%E9%A0%86%EF%BC%89"  # chunithm楽曲一覧
res = req.urlopen(url)
soup = BeautifulSoup(res, "html.parser")
#print(soup)

td_list = soup.find_all("td")
#print(str(list))

music_list = []
for td in td_list:
    if td.find("a") != None:  # <td>内の<a>のテキストを取り出す
        a = td.find("a")
        text = a.string
        if str(text) != "None":  # "None"文字列を弾く
            print(str(text))
            music_list.append(str(text))

music_list_sorted = sorted(set(music_list), key=music_list.index)  # 重複を取り除く
fp = open("music_list.txt", 'w', encoding='utf-8')
for a in music_list_sorted:
    if a == "全曲一覧":
        break
    fp.write(a + '\n')
fp.close()
