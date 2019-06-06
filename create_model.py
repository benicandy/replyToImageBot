# twitterで収集した画像を機械学習用に整形するモジュール

from sklearn import model_selection
from PIL import Image
import os, glob
from datetime import datetime
import numpy as np

# 分類対象のラベルを指定する
root_dir = ".\\result_images\\"
categories = ["result_SSS", "result_notSSS", "noise"]
nb_classes = len(categories)
image_size = 50

# フォルダの画像データを読み込む
X = []  # 画像データ
Y = []  # ラベルデータ
for idx, cat in enumerate(categories):
    image_dir = root_dir + "\\" + cat
    files = glob.glob(image_dir + "\\*.jpg")
    print("---", cat, "を処理中...")
    for i, f in enumerate(files):
        img = Image.open(f)
        img = img.convert("RGB")  # カラーモードの変更
        img = img.resize((image_size, image_size))  # 画像サイズの変更
        data = np.asarray(img)
        X.append(data)
        Y.append(idx)
X = np.array(X)
Y = np.array(Y)

# 学習データとテストデータを分ける
X_train, X_test, y_train, y_test = model_selection.train_test_split(X, Y)
xy = (X_train, X_test, y_train, y_test)
filename = ".\\chunithm_model\\chunithm_SSS" + '_' + datetime.now().strftime("%Y%m%d_%H%M%S") + ".npy"  # ファイル名にチェック終了時間を追加
np.save(filename, xy)
print("ok,", len(Y))
