# replyToImageBot

// Twitte rのタイムライン上で特定の画像を見つけたらリプライをつける bot です

// Twitter 上で，音楽ゲーム CHUNITHM のリザルト画像にいいねやリプライをつける bot のスクリプトです．

// bot が画像を判定するためには，前提として学習モデルを生成しておく必要があります．


＊開発環境

OS: Windows 10

Language: Python3.6 (Anaconda3)


＊bot の機能

1. 特定の曲名を Twitter 上で検索し，その中から SSS 画像を見つけたらいいねをつける．

2. タイムライン上で画像を探し，その中から SSS 画像を見つけたらいいねをつけ，そのうちいくつかのツイートにはリプライをつける．


bot_script.py を実行すると，上記の2つを行います．主な設定は config_bot.py でできるようになってます．



＊学習モデルの生成

自分でラベル付けした画像データから create_model.py で CNN のモデルを生成します．

モデルができたら，chunithm_checker.py で新規画像のラベル予測ができるようになります．

chunithm_checker.py は bot_script.py で使用されています．


現在稼働中の bot アカウント -> @chupenbot
