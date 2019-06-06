# -*- coding: utf-8 -*-

# 指定ユーザ名
SCREEN_NAME = "hoge"  # botのtwitterのID

# 取得ツイート数
GAIN = 150  # 1～200で指定(タイムライン)
SEARCH = 10  # 1～200で指定(1ワード当たり検索結果数)

# botのリプライメッセージの種類
REPLY_MSG_LIST = ["hoge", "fuga", "foo", "bar"]

# postの段階を指定(1:いいね専用枠にいいね, 2:リプ枠にいいね, 3:リプ枠にリプ)
TL_POST_LEVEL = 3
SEARCH_POST_LEVEL = 1

# いいねを付ける数を指定
TL_FAV_NUM = 3  # タイムラインに対して
SEARCH_FAV_NUM = 3  # 検索結果全体に対して

# 取得したい画像の検索ワード用リスト
KEYWORDS_LIST = []
# ワードリストの読み込み
li_word = "hogehoge.txt"
with open(li_word, 'r', encoding='utf-8') as fp:
    for line in fp:
        li = line.strip()
        #print(li)
        KEYWORDS_LIST.append(li)


# 恒常的履歴の保存先ディレクトリ/保存先ファイル名
PER_ROOT = '.\\per'
PER_FOLLOWERS = PER_ROOT + '\\followers.txt'  # フォロワーid保存用ファイル

# 下記のディレクトリ群のルートディレクトリ
ROOT = '.\\one_day_dir'

# 画像の保存先ディレクトリ
IMAGES_TL_ROOT_DIR = ROOT + '\\timeline_images'  # 画像保存ディレクトリのルートディレクトリ
IMAGES_TL_DIR = IMAGES_TL_ROOT_DIR + '\\images'  # 画像保存ディレクトリ
IMAGES_SEARCH_ROOT_DIR = ROOT + '\\search_images'  # 検索画像保存ディレクトリのルートディレクトリ
IMAGES_SEARCH_DIR = IMAGES_SEARCH_ROOT_DIR + '\\images'  # 検索画像保存ディレクトリ

# 一時的履歴の保存先ディレクトリ/保存ファイル名
HIS_TL_DIR = ROOT + '\\timeline_his'  # タイムラインに関する履歴
HIS_TL_FNAME_ID = HIS_TL_DIR + '\\user_id_posted.txt'  # 反応済みのid履歴
HIS_TL_FNAME_URL = HIS_TL_DIR + '\\media_url_posted.txt'  # 反応済みのmedia_url履歴
HIS_SEARCH_DIR = ROOT + '\\search_his'  # 検索結果に関する履歴
HIS_SEARCH_FNAME_ID = HIS_SEARCH_DIR + '\\user_id_posted.txt'  # 反応済みのid履歴
HIS_SEARCH_FNAME_URL = HIS_SEARCH_DIR + '\\media_url_posted.txt'  # 反応済みのmedia_url履歴



# Twitter API Key の設定
# APIを使用するアカウントのAPI Key
CONSUMER_KEY = "hogehoge"
CONSUMER_SECRET = "fugafuga"
ACCESS_TOKEN = "foofoo"
ACCESS_TOKEN_SECRET = "barbar"
