# -*- coding: utf-8 -*-
# bot実装モジュール
import json, os, sys, time, random
sys.path.append('path_to_packages')

from datetime import datetime, timezone, timedelta
from requests_oauthlib import OAuth1Session  # OAuthライブラリの読み込み
import urllib.request as req

import config_bot  # config_botモジュールの読み込み
import chunithm_checker  # 画像のラベル判定モジュール


# Twitter API Key の設定
CK = config_bot.CONSUMER_KEY
CS = config_bot.CONSUMER_SECRET
AT = config_bot.ACCESS_TOKEN
ATS = config_bot.ACCESS_TOKEN_SECRET

class SetTwitterAPI(object):
    # 認証処理を行うクラス
    def __init__(self):
        super().__init__()
        try:
            self.twitter = OAuth1Session(CK, CS, AT, ATS)
        except Exception as e:
            print("[-] Error:", e)
            self.twitter = None

    def twitter(self):
        return self.twitter

class FollowersIds(object):
    # フォロワー情報を扱う
    def __init__(self, twitter):
        super().__init__()
        print("GetFollowersIds.__init__()")
        self.end_point = "https://api.twitter.com/1.1/followers/ids.json"  # フォロワー情報のエンドポイントの設定
        self.twitter = twitter
        self.params = {
            "count": "5000",
            "stringify_ids": 'true',
            "screen_name": config_bot.SCREEN_NAME,
        }
        if not os.path.exists(config_bot.PER_FOLLOWERS):
            with open(config_bot.PER_FOLLOWERS, 'w') as fp:  fp.write("")

    def run(self):
        print("FollowersIds.run()")
        followers_his = self.read_followers_his()
        self.get_followers_ids()
        self.get_new_followers(followers_his)
        self.make_followers_his()
        return self.new_followers

    def read_followers_his(self):
        # hisのフォロワーを読み込んでリストを作成
        print("read_followers_his()")
        try:
            followers_his = []
            fname = config_bot.PER_FOLLOWERS
            with open(fname, 'r', encoding='utf-8') as fp:
                for line in fp:  # ファイルから1行ずつ読み込む
                    li = line.strip()  # 行から"\n"を削除
                    followers_his.append(li)  # リストにidを追加
            return followers_his
        except Exception as e:
            print("[f-1] Error: ", e)

    def get_followers_ids(self):
        # 現在のフォロワーidを読み込む
        print("get_followers_ids()")
        try:
            res = self.twitter.get(self.end_point, params=self.params)
            self.result = json.loads(res.text)
        except Exception as e:
            print("[f-2] Error: ", e)

    def get_new_followers(self, followers_his):
        # 現在のフォロワーと過去のフォロワーを比較して、新たに増えたフォロワーを調べる
        print("get_new_followers()")
        try:
            self.new_followers = []
            for current in self.result['ids']:
                for his in followers_his:
                    if not current == his:
                       self.new_followers.append(current)
        except Exception as e:
            print("[f-3] Error: ", e)

    def make_followers_his(self):
        # フォロワーのidをファイルに記録する
        print("make_followers_his()")
        try:
            fname = config_bot.PER_FOLLOWERS
            with open(fname, 'w', encoding='utf-8') as fp:
                for id in self.result['ids']:
                    fp.write(str(id) + "\n")
        except Exception as e:
            print("[f-4] Error: ", e)

class GetTimelineImages(object):
    # タイムライン上の画像とそれに付随する情報を取得するクラス
    def __init__(self, twitter):
        super().__init__()
        print("GetTimelineImages.__init__()")
        self.gain = str(config_bot.GAIN)  # 取得ツイート数の設定
        self.stream_url = "https://api.twitter.com/1.1/statuses/home_timeline.json"  # タイムライン取得エンドポイントの設定
        self.twitter = twitter
        #self.set_twitter_api()  # 認証処理
        self.params = {
            "count": self.gain,
            "trim_user": 'false',
            "include_entities": 'true',
            "exclude_replies": 'true',
        }  # リクエスト用パラメータ

    def run(self):
        # 実行関数
        print("GetTimelineImages.run()")
        try:
            self.init_list()  # 必要なリストを初期化
            uni_list = self.get_timeline()  # タイムラインから必要な情報を取得:self.uni_list = {key = "tweet_id", "user_id", "text", "img_url"}
            if uni_list == None:  return 0  # 画像urlを含む情報が空なら0を返す
            self.judge(uni_list)  # get_timeline()で得たリストから重複のないものを選別(self.valid_listを作る)
            print("downloading images in timeline...")
            for i, dict in enumerate(self.valid_list):
                filename = self.download(dict['img_url'])  # 画像をダウンロード/保存したファイル名を取得
                self.valid_list[i][
                    'filename'] = filename  # 保存ファイル名をdictに追加:{key = "name_id", "tweet_id", "user_id", "text", "img_url", "filename"}
        except Exception as e:
            print("[t-1] Error: ", e)

        return self.res, self.valid_list

    def init_list(self):
        # 初期化が必要なリストを全て初期化
        self.download_url_list = []  # ダウンロード候補画像urlリスト
        self.user_id_list = []  # ダウンロード候補画像のユーザIDリスト
        self.tweet_id_list = []  # ダウンロード候補画像のツイートIDリスト
        self.uni_list = []  # 上記3要素をdict化したもののリスト
        self.valid_list = []  # uni_listの中で過去にリプライを返したことがないもののリスト

    """
    def set_twitter_api(self):
        # 認証処理
        try:
            self.twitter = OAuth1Session(CK, CS, AT, ATS)
        except Exception as e:
            print("[1] Error:", e)
            self.twitter = None
    """

    def get_timeline(self):
        # タイムラインの情報取得
        print("get_timeline()")
        try:
            self.res = self.twitter.get(self.stream_url, params=self.params)  # GETリクエストのレスポンスを取得
            timeline = json.loads(self.res.text)  # json文字列をdictに変換
            for tweet in timeline:  # タイムライン上のツイートを取得
                #print(tweet['text'], tweet['id_str'])
                if 'media' in tweet['entities'].keys() and not 'retweeted_status' in tweet.keys():
                    # "'media'keyが存在"かつ"RTでない"なら実行
                    if tweet['in_reply_to_status_id'] == None:
                        # リプライ情報がnull(誰か宛のツイートでない)なら実行
                        # -------------アカウントID(@***)取得部---#
                        name_id = tweet['user']['screen_name']
                        # -------------ツイートID取得部-----------#
                        tweet_id = tweet['id_str']  # tweet_idを取り出す
                        self.tweet_id_list.append(tweet_id)
                        # -------------ユーザーID取得部-----------#
                        user_id = tweet['user']['id_str']  # user_idを取り出す
                        self.user_id_list.append(user_id)
                        #------------ツイート内容取得部-----------#
                        text = tweet['text']
                        # --------------画像url取得部-------------#
                        img_url = tweet['entities']['media'][0]['media_url_https']  # img_urlを取り出す
                        self.download_url_list.append(img_url)  # リストに'media_url_https'のvalueを格納
                        # -------------4要素リスト化部------------#
                        self.uni_list.append({'name_id': name_id, 'tweet_id': tweet_id, 'user_id': user_id, 'text': text, 'img_url': img_url})
                        # ----------------------------------------#
                        if tweet_id==None or user_id==None or img_url==None:
                            print("pop")
                            self.uni_list.pop()  # テキストを除き少なくとも一つ情報が欠けたリストが生成されたら消去
        except Exception as e:
            print("[t-2] Error: ", e)

        return self.uni_list

    def judge(self, uni_list):
        # user_idまたはimg_urlに重複のないツイートをリスト化
        print("judge()")
        DIR = config_bot.HIS_TL_DIR
        fname_id = config_bot.HIS_TL_FNAME_ID  # user_id格納場所
        fname_url = config_bot.HIS_TL_FNAME_URL  # img_url格納場所
        try:
            if not os.path.exists(DIR):
                os.makedirs(DIR)
            for dict in uni_list:
                if self.check_duplication(fname_id, dict['user_id']):
                    if self.check_duplication(fname_url, dict['img_url']):
                        # print(dict)
                        self.valid_list.append(dict)  # use_id,img_urlともに重複のないdictをリストに追加
        except Exception as e:
            print("[t-3] Error: ", e)

    def check_duplication(self, filename, info):
        # infoが過去に読み取られたかを調べる。一致infoが存在しなければ1を返す
        print("check_duplication()")
        try:
            c = 1  # チェック用の変数
            if not os.path.exists(filename):  # ファイルが存在しない場合あらたに作成
                with open(filename, 'w', encoding='utf-8') as fp:  fp.write("")
            with open(filename, 'r', encoding='utf-8') as fp:
                for line in fp:  # ファイルから1行ずつ読み込む
                    li = line.strip()  # "\n"を取り除く
                    if li == info:  # ファイル中のinfoと一致した場合実行
                        c = 0
                        break
            return c
        except Exception as e:
            print("[t-4] Error: ", e)

    def download(self, url):
        # 与えられたurlから画像を指定ディレクトリにダウンロードする
        print("download()")
        dir = config_bot.IMAGES_TL_DIR
        os.makedirs(dir, exist_ok=True)  # 設定ファイルで指定したディレクトリを作成
        filename = url.split('/')[-1]  # 画像url文字列の末尾から調べて最初に"/"が見つかる手前までを代入
        savepath = dir + '\\' + filename  # 指定したディレクトリのfilenameという名前のファイルへのパス
        print("savepath: ", savepath)
        try:
            response = req.urlopen(url)
            with open(savepath, 'wb') as f:
                f.write(response.read())
        except Exception as e:
            print("[t-5] Error:", e)

        return filename  # 保存したファイルの名前を返す

class GetSearchImages(object):
    def __init__(self, twitter):
        super().__init__()
        print("GetSearchImages.__init__()")
        self.keywords_list = config_bot.KEYWORDS_LIST  # 検索ワードリスト
        self.keywords_list_filtered = ["%s filter:images" % keyword for keyword in self.keywords_list]  # 画像検索フィルター
        self.gain = str(config_bot.SEARCH)
        self.search_url = "https://api.twitter.com/1.1/search/tweets.json"  # 検索結果取得エンドポイントの設定
        self.twitter = twitter
        self.media_url_list = []

    def run(self):
        print("GetSearchImages.run()")
        try:
            self.init_list()
            for keyword in self.keywords_list_filtered:
                self.max_id = None  # 初期化
                uni_list = self.search(
                    keyword)  # 検索結果から必要な情報を取得:self.uni_list = {key = "tweet_id", "user_id", "text", "img_url"}
                if uni_list == None:  pass  # 画像urlを含む情報が空ならpass
                valid_list = self.judge(uni_list)  # self.search()で得たリストからpost済みでないものを選別(self.valid_listを作る)
                print("downloading %s..." % keyword)
                i = 0  # 初期化
                for dict in valid_list:
                    filename = self.download(dict['img_url'])  # 画像をダウンロード/保存したファイル名を取得
                    valid_list[i][
                        'filename'] = filename  # 保存ファイル名をdictに追加:{key = "tweet_id", "user_id", "text", "img_url", "filename"}
                    i += 1  # 最後に1加算
                print("valid_list: ", valid_list)
                if valid_list != []:
                    self.valid_li_list.append(valid_list)  # self.valid_listを検索ワードごとに追加
            print("self.valid_li_list:", self.valid_li_list)
            if self.valid_li_list == None: return 0  # もし全ワード検索結果で画像が得られなければ0を返す

            return self.res, self.valid_li_list

        except Exception as e:
            print("[s-1] Error: ", e)

    def init_list(self):
        # 初期化が必要なリストを全て初期化
        self.download_url_list = []  # ダウンロード候補画像urlリスト
        self.user_id_list = []  # ダウンロード候補画像のユーザIDリスト
        self.tweet_id_list = []  # ダウンロード候補画像のツイートIDリスト
        self.uni_list = []  # 上記3要素をdict化したもののリスト
        self.valid_li_list = []  # 検索ワードごとのvalid_listを格納したリスト

    def search(self, keyword):
        # 検索用のパラメータ情報を入力
        print("search()")
        self.download_url_list.clear()  # ダウンロード候補画像urlリスト
        self.user_id_list.clear()  # ダウンロード候補画像のユーザIDリスト
        self.tweet_id_list.clear()  # ダウンロード候補画像のツイートIDリスト
        self.uni_list.clear()  # 上記3要素をdict化したもののリスト
        self.params = {
            'q': keyword,  # 検索ワード
            'count': self.gain,  # 取得ツイート数
            'result_type': 'recent',  # 最新のツイートを取得
            'lang': 'ja',  # 検索対象地域の言語コード
            'include_entities': 'true'  # ツイートオブジェクト内のentitiesプロパティを含めるか否か
        }
        try:
            if self.max_id:  # max_idが値を持っていれば実行
                self.params['max_id'] = self.max_id  # max_id(これ以前のツイートのIDを取得)を追加
            else:  # max_idが値を持たないとき(初回)実行
                pass
            self.res = self.twitter.get(self.search_url, params=self.params)  # GETリクエストを取得
            self.search_results = json.loads(self.res.text)  # json文字列をdict型に変換
            for tweet in self.search_results['statuses']:  # 'statuses'リスト内を順に取り出す
                #print(tweet['text'], tweet['id_str'])
                if 'media' in tweet['entities'].keys() and not 'retweeted_status' in tweet.keys():
                    # "'media'keyが存在"かつ"RTでない"なら実行
                    if tweet['user']['following'] == True:  pass  # botのフォローしているアカウントならパス
                    if tweet['in_reply_to_status_id'] == None:  # リプライ情報がnull(誰か宛のツイートでない)なら実行
                        # -------------ツイートID取得部-----------#
                        tweet_id = tweet['id_str']  # tweet_idを取り出す
                        self.tweet_id_list.append(tweet_id)
                        # -------------ユーザーID取得部-----------#
                        user_id = tweet['user']['id_str']  # user_idを取り出す
                        self.user_id_list.append(user_id)
                        #------------ツイート内容取得部-----------#
                        text = tweet['text']
                        # --------------画像url取得部-------------#
                        img_url = tweet['entities']['media'][0]['media_url_https']  # img_urlを取り出す
                        self.download_url_list.append(img_url)  # リストに'media_url_https'のvalueを格納
                        # -------------4要素リスト化部------------#
                        self.uni_list.append({'tweet_id': tweet_id, 'user_id': user_id, 'text': text, 'img_url': img_url})
                        # ----------------------------------------#
                        if tweet_id==None or user_id==None or img_url==None:
                            self.uni_list.pop()  # テキストを除き少なくとも一つ情報が欠けたリストが生成されたら消去
            return self.uni_list
        except Exception as e:
            print("[s-2] Error: ", e)

    def judge(self, uni_list):
        # user_idまたはimg_urlに重複のないツイートをリスト化
        print("judge()")
        valid_list = []
        DIR = config_bot.HIS_SEARCH_DIR
        fname_id = config_bot.HIS_SEARCH_FNAME_ID  # user_id格納場所
        fname_url = config_bot.HIS_SEARCH_FNAME_URL  # img_url格納場所
        try:
            if not os.path.exists(DIR):
                os.makedirs(DIR)
            for dict in uni_list:
                if self.check_duplication(fname_id, dict['user_id']):
                    if self.check_duplication(fname_url, dict['img_url']):
                        # print(dict)
                        valid_list.append(dict)  # use_id,img_urlともに重複のないdictをリストに追加
        except Exception as e:
            print("[s-3] Error: ", e)

        return valid_list

    def check_duplication(self, filename, info):
        print("check_duplication()")
        try:
            # infoが過去に読み取られたかを調べる。一致infoが存在しなければ1を返す
            c = 1  # チェック用の変数
            if not os.path.exists(filename):  # ファイルが存在しない場合あらたに作成
                with open(filename, 'w', encoding='utf-8') as fp:  fp.write("")
            with open(filename, 'r', encoding='utf-8') as fp:
                for line in fp:  # ファイルから1行ずつ読み込む
                    li = line.strip()  # "\n"を取り除く
                    if li == info:  # ファイル中のinfoと一致した場合実行
                        c = 0
                        break
            return c

        except Exception as e:
            print("[s-4] Error: ", e)

    def download(self, url):
        # 与えられたurlから画像を指定ディレクトリにダウンロードする
        print("download()")
        dir = config_bot.IMAGES_SEARCH_DIR
        os.makedirs(dir, exist_ok=True)  # 設定ファイルで指定したディレクトリを作成
        filename = url.split('/')[-1]  # 画像url文字列の末尾から調べて最初に"/"が見つかる手前までを代入
        savepath = dir + '\\' + filename  # 指定したディレクトリのfilenameという名前のファイルへのパス
        try:
            response = req.urlopen(url)
            with open(savepath, 'wb') as f:
                f.write(response.read())
        except Exception as e:
            print("[s-5] Error:", e)

        return filename  # 保存したファイルの名前を返す

class CheckImages(object):
    # SSSかつ"!"がtextに含まれるdictのリストを作成
    def __init__(self, valid_list, dir):
        super().__init__()
        print("CheckImages.__init__()")
        self.valid_list = valid_list
        self.dir = dir

    def run(self):
        print("CheckImages.run()")
        try:
            self.make_SSS_list()  # SSS画像名のリスト(self.SSS_fname_list)を作成
            if self.SSS_fname_list == []:  return 0  # SSS画像がなければ0を返す
            self.get_SSS_dict()  # SSS判定画像を持つdictのリストself.valid_SSS_listを作成
            self.check_excl()  # 上で得たリストのうち"鳥"を含んだツイートを持つdictのリストself.cand_listを作成
            if self.cand_list == []:  return 0
        except Exception as e:
            print("[c-1] Error: ", e)

        return self.cand_list

    def check_excl(self):
        # "鳥"の有無を判別し、リストを作成
        print("check_excl()")
        try:
            self.cand_list = []
            for dict in self.valid_SSS_list:
                text = dict['text']
                result_em = text.find("鳥")  # "鳥" 見つからなかった場合-1を返す
                result_en = text.find("鳥")  # "鳥" 見つからなかった場合-1を返す
                if result_em != -1 or result_en != -1:  # "鳥"を含むツイートをリストに追加
                    self.cand_list.append(dict)
        except Exception as e:
            print("[c-2] Error:", e)

    def get_SSS_dict(self):
        # SSSと判定された画像を持ったdictのリストを作成
        print("get_SSS_dict")
        self.valid_SSS_list = []
        try:
            for dict in self.valid_list:
                for fname in self.SSS_fname_list:
                    if dict['filename'] == fname:  # SSS判定の画像を持ったdictをリストに追加
                        self.valid_SSS_list.append(dict)
        except Exception as e:
            print("[c-3] Error: ", e)

    def make_SSS_list(self):
        # SSS画像名のリストを作成
        print("make_SSS_list()")
        fname_list = []
        self.SSS_fname_list = []
        try:
            for dict in self.valid_list:  # ファイル名のリストを作成
                fname_list.append(dict['filename'])
            self.check(fname_list, self.dir)  # 画像のラベルを判定→self.pre_listに情報が追加される
            for pre in self.pre_list:  # self.pre_list読み込み
                if pre[1] == 1:  # preのうちSSSのもの(cat_mum == 1)を選出
                    self.SSS_fname_list.append(pre[0])  # SSS画像名をリスト化
        except Exception as e:
            print("[c-4] Error: ", e)

    def check(self, fname_list, dir):
        # 画像のラベルを判定する
        print("check()")
        try:
            self.pre_list = chunithm_checker.check_image(fname_list,
                                                         dir)  # self.pre_list = [[files[i], cat_num[y]], ...]
            rename_dir = dir + '_' + datetime.now().strftime("%Y%m%d_%H%M%S")  # フォルダ名にチェック終了時間を追加
            os.rename(dir, rename_dir)  # チェック終了後、画像保存フォルダ名へ現在時刻を追加したものにリネームする
        except Exception as e:
            print("[c-5] Error: ", e)

class PostReact(object):
    # SSS画像ツイートにファボやリプライを送るクラス
    def __init__(self, twitter, data_set, dir, fav_num, level):
        super().__init__()
        print("PostReach.__init__()")
        self.post_reply_url = "https://api.twitter.com/1.1/statuses/update.json"  # エンドポイント(リプライ)
        self.post_fav_url = "https://api.twitter.com/1.1/favorites/create.json"  # エンドポイント(fav)
        self.twitter = twitter  # 認証処理の読み込み
        self.data_set = data_set  # データセットの読み込み:{key = 'name_id','tweet_id','user_id','text','img_url','filename'}のリスト
        self.dir = dir  # post済url/id記録ファイル保存先ディレクトリ
        self.fav_num = fav_num  # いいね専用枠数の指定
        self.level = level  # どこまでrunを実行するかの段階を指定 1:いいね専用枠にいいね 2:リプライ枠にいいね 3:リプライ枠にリプライ
        #self.set_twitter_api()

    def run(self):
        print("PostReact.run()")
        try:
            self.dicision()
            if self.level > 0:
                for dict in self.some_other_dict_list:  # いいね専用枠のツイートにいいねをつける
                    self.post_fav(dict['tweet_id'])
            if self.level > 1:
                self.post_fav_elected()  # リプライ枠ツイートにいいねを付ける
            if self.level > 2:
                self.post_reply_elected()  # リプライ枠ツイートにリプライを送る
        except Exception as e:
            print("[p-1] Error: ", e)

    """
    def set_twitter_api(self):
        # 認証処理
        try:
            self.twitter = OAuth1Session(CK, CS, AT, ATS)
        except Exception as e:
            print("[-] Error:", e)
            self.twitter = None
    """

    def dicision(self):
        # リプライ先・いいね先を決定する
        print("dicision()")
        len_data_set = len(self.data_set)  # データセットの個数
        rand_num_list = []
        try:
            for a in range(len_data_set): rand_num_list.append(a)  # 0~len_data_set-1の要素を代入
            random.shuffle(rand_num_list)  # リストの要素の順序をシャッフルする ex,rand_num_list=[3,2,0,1]
            self.elected_dict = self.data_set[rand_num_list[0]]  # リプライ用に選ばれたdict1つ
            self.some_other_dict_list = []  # リプライ用ではなくいいねだけを付けるdict用のリスト
            k = 1  # 初期化
            i = self.fav_num  # リプ用以外にいいねを付けるツイート数を指定
            while (len(self.data_set[k:]) > 0) and (i - k >= 0):  # k+1番目のデータが存在し、指定ツイート数を超えていなければループ
                self.some_other_dict_list.append(self.data_set[rand_num_list[k]])  # elected以外のdata_setを格納
                k += 1
        except Exception as e:
            print("[p-2-1] Error: ", e)

        try:
            DIR = self.dir
            fname_id = DIR + "\\user_id_posted.txt"  # DIRディレクトリにuser_idを保存
            fname_url = DIR + "\\media_url_posted.txt"  # DIRディレクトリにimg_urlを保存
            if not os.path.exists(DIR):
                os.makedirs(DIR)
            self.store_info(fname_id, self.elected_dict['user_id'])  # user_idをファイルに追加
            self.store_info(fname_url, self.elected_dict['img_url'])  # img_urlをファイルに追加
            for dict in self.some_other_dict_list:
                self.store_info(fname_id, dict['user_id'])  # user_idをファイルに追加
                self.store_info(fname_url, dict['img_url'])  # img_urlをファイルに追加
        except Exception as e:
            print("[p-2-2] Error: ", e)

    def post_fav_elected(self):
        # 選出されたツイートにいいねを付ける
        print("post_fav_elected()")
        params_fav = {
            "id": self.elected_dict['tweet_id']
        }
        try:
            print("timeline fav先：", self.elected_dict['name_id'], self.elected_dict['tweet_id'])
            self.twitter.post(self.post_fav_url, params_fav)
        except Exception as e:
            print("[p-3] Error: ", e)

    def post_reply_elected(self):
        # 選出されたツイートにリプライを送信する
        print("post_reply_elected")
        msg_list = config_bot.REPLY_MSG_LIST
        msg = msg_list[random.randrange(len(msg_list))]
        params_reply = {
            "status": "@" + self.elected_dict['name_id'] + " " + msg,
            "in_reply_to_status_id": self.elected_dict['tweet_id'],
        }
        try:
            print("リプライ送信先：", self.elected_dict['tweet_id'], self.elected_dict['text'])
            self.twitter.post(self.post_reply_url, params_reply)
        except Exception as e:
            print("[p-4] Error: ", e)

    def post_fav(self, tweet_id):
        # ツイートにいいねを付ける
        print("post_fav()")
        params_fav = {
            "id": tweet_id
        }
        print("fav先：", tweet_id)
        try:
            self.twitter.post(self.post_fav_url, params_fav)
        except Exception as e:
            print("[p-5] Error: ", e)


    def store_info(self, filename, info):
        # 情報をファイルに記録
        print("store_info()")
        try:
            if not os.path.exists(filename):  # ファイルが存在しない場合あらたに作成
                with open(filename, 'w', encoding='utf-8') as fp:  fp.write("")
            with open(filename, 'a', encoding='utf-8') as fp:
                fp.write(info + "\n")  # infoをファイルに追記
        except Exception as e:
            print("[p-7] Error: ", e)

class PostTweet(object):
    # ツイート実行に関するクラス
    def __init__(self, twitter, new_followers):
        super().__init__()
        print("PostTweet.__init__()")
        self.post_tweet_url = "https://api.twitter.com/1.1/statuses/update.json"  # エンドポイント(ツイート)
        self.twitter = twitter  # 認証処理の読み込み
        self.new_followers = new_followers

    def post_tweet_followers(self):
        # 新規フォロワー名をツイートする
        params = {
            "status": ""
        }


class APILimitStatus(object):
    # API制限を表現するクラス
    def __init__(self, res):
        super().__init__()
        self.res = res
        self.limit_status_url = "https://api.twitter.com/1.1/application/rate_limit_status.json"  # エンドポイントの設定

    """
    def set_twitter_api(self):
        # 認証処理
        try:
            self.twitter = OAuth1Session(CK, CS, AT, ATS)
        except Exception as e:
            print("[1] Error:", e)
            self.twitter = None
    """

    def run(self):
        self.tell_remaining()
        self.need_seconds_for_reset()
        self.reset_at()

    def sleep_to_reset_if_limit(self):
        # 制限に達していたらリセットされるまで待機
        if self.remaining <= 0:
            time.sleep(self.seconds_for_reset + 1)
        print(str(self.seconds_for_reset + 1) + "秒待機します。")

    def sleep_to_reset_if_limit_designate(self, value):
        # 指定のremaining未満なら制限がリセットされるまでスリープする
        if int(self.remaining) <= int(value):
            time.sleep(self.seconds_for_reset + 1)
        print(str(self.seconds_for_reset + 1) + "秒待機します。")

    def need_seconds_for_reset(self):
        # リクエスト可能残数リセットまでの残り秒数
        self.seconds_for_reset = int(self.res.headers['X-Rate-Limit-Reset']) - time.mktime(datetime.now().timetuple())  # UTCを秒数に変換
        print("リクエスト可能残数リセットまで残り" + str(self.seconds_for_reset) + "[s]")

    def reset_at(self):
        # リクエスト可能残数リセット時刻(loc)
        self.time_for_reset_UTC = self.res.headers['X-Rate-Limit-Reset']  # リクエスト可能残数リセットまでの時間(UTC)
        self.time_for_reset_JST = timezone(timedelta(hours=+9), 'JST')
        self.time_for_reset_loc = datetime.fromtimestamp(int(self.time_for_reset_UTC), self.time_for_reset_JST)
        print("リクエスト可能残数リセット時刻：" + str(self.time_for_reset_loc))

    def tell_remaining(self):
        # リクエスト可能残数の取得
        self.remaining = self.res.headers['X-Rate-Limit-Remaining']
        print("リクエスト可能残数：" + str(self.remaining))

def main():

    # ログファイル保存用ディレクトリの出力
    log_root_dir = ".\\stdout_log"
    log_dir = log_root_dir + "\\log" + "_" + datetime.now().strftime("%Y%m%d")
    if not os.path.exists(log_dir):  # フォルダが存在しない場合あらたに作成
        os.makedirs(log_dir)
    fname = log_dir + '\\log' + '_' + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"  # 標準出力をログに保存
    fo = open(fname, 'w', encoding='utf-8')
    sys.stdout = fo

    try:
        #-------認証処理----------------------------------#
        set = SetTwitterAPI()  # インスタンス化
        twitter = set.twitter  # 認証処理情報を取得

        #-------タイムライン画像の処理------------------#
        timeline = GetTimelineImages(twitter)  # インスタンス化
        result = timeline.run()  # (res, valid_list)を取得
        tl_fav_num = config_bot.TL_FAV_NUM  # いいねの数を指定
        tl_level = config_bot.TL_POST_LEVEL  # postの段階を指定
        if result != 0:  # タイムラインから画像が取得できていれば
            print("-------タイムライン画像処理中-------")
            checker = CheckImages(result[1], config_bot.IMAGES_TL_DIR)  # インスタンス化
            data_set = checker.run()  # SSS画像ツイートに関するデータを取得
            if data_set != 0:  # "!"を含むSSS画像が少なくとも一つ取得できていれば実行
                post = PostReact(twitter, data_set, config_bot.HIS_TL_DIR, tl_fav_num, tl_level)  # インスタンス化
                post.run()
            else:
                print("タイムラインに新規のSSS画像はありませんでした。")
                pass
        else:
            print("タイムラインに新規の画像はありませんでした。")
            pass

        #-------検索画像の処理---------------------------#
        search = GetSearchImages(twitter)  # インスタンス化
        se_result = search.run()  # (res, valid_li_list)を取得
        se_fav_num = config_bot.SEARCH_FAV_NUM
        se_post_level = config_bot.SEARCH_POST_LEVEL
        if se_result != 0:  # 検索結果に画像が存在すれば
            print("-------検索結果画像処理中-----------")
            valid_list = []
            for list in se_result[1]:  # [[dict1_1,dict1_2,...],[dict2_1,dict2_2,...],...]からリストを取り出す
                for dict in list:  # [dicti_1,dicti_2,...]からdictを取り出す
                    valid_list.append(dict)  # 複数の検索画像の情報を一つのリストにまとめる
            se_checker = CheckImages(valid_list, config_bot.IMAGES_SEARCH_DIR)
            se_data_set = se_checker.run()
            if se_data_set != 0:
                se_post = PostReact(twitter, se_data_set, config_bot.HIS_SEARCH_DIR, se_fav_num, se_post_level)
                se_post.run()
            else:
                print("検索結果に新規のSSS画像はありませんでした。")
        else:
            print("検索結果に新規の画像はありませんでした。")
            pass

        #-------API利用制限情報の表示------------------#
        print("タイムライン取得制限情報")
        limit_status_timeline = APILimitStatus(result[0])
        limit_status_timeline.run()  # 実行/制限情報を表示
        print("検索結果取得制限情報")
        limit_status_search = APILimitStatus(se_result[0])
        limit_status_search.run()

    except KeyboardInterrupt:
        pass

    fo.close()

if __name__ == '__main__':
    main()
