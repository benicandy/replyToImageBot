# replyToImageBot

// Twitterのタイムライン上で特定の画像を見つけたらリプライをつけるbotです

// Twitter上で，音楽ゲームCHUNITHMのリザルト画像にいいねやリプライをつけるbotのスクリプトです．

// botを一般化するのが非常に面倒だったので，とりあえず元のbotのコードをほぼそのまま公開しています．

// いろいろな機能を雑に実装しています．

// botが画像を判定するためには，前提として学習モデルを生成しておく必要があります．


＊開発環境

OS: Windows 10

Language: Python3.6 (Anaconda3)


＊botの機能

1. 特定の曲名をTwitter上で検索し，その中からSSS画像を見つけたらいいねをつける．

2. タイムライン上で画像を探し，その中からSSS画像を見つけたらいいねをつけ，そのうちいくつかのツイートにはリプライをつける．


bot_script.pyを実行すると，上記の2つを行います．主な設定はconfig_bot.pyでできるようになってます．



＊学習モデルの生成

自分でラベル付けした画像データからcreate_model.pyでCNNのモデルを生成します．

モデルができたら，chunithm_checker.pyで新規画像のラベル予測ができるようになります．

chunithm_checker.pyはbot_script.pyで使用されています．
