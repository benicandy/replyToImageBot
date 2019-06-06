# 整形済み画像を読み込んでラベルを予測し、予測に応じた応答をするモジュール
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense
import os
from PIL import Image
import numpy as np

import config_bot

def check_image(fnames, dir):
    print("chunithm_checker.check_image()")
    os.chdir(dir)  # カレントディレクトリを画像が保存されているフォルダに変更
    hdf5_dir = "path_to_hdf5file"
    image_size = 50
    categories = [
        "result_SSS", "result_notSSS", "noise"]
    cat_num = [1, 0, -1]
    nb_classes = len(categories)

    # 入力画像をNumpyに変換
    X = []
    files = []
    try:
        for fname in fnames[0:]:
            img = Image.open(fname)
            img = img.convert("RGB")
            img = img.resize((image_size, image_size))
            in_data = np.asarray(img)
            X.append(in_data)
            files.append(fname)
        X = np.array(X)
    except Exception as e:
        print("[1_] Error: ", e)

    # CNNのモデルを構築
    model = build_model(X.shape[1:], nb_classes)
    model.load_weights(hdf5_dir)

    # データを予測
    print("データを予測")
    pre = model.predict(X)
    pre_list = []
    input = []
    judge = []
    try:
        for i, p in enumerate(pre):
            y = p.argmax()
            #print("+ input:", files[i])
            input.append(files[i])
            #print("| judge:", categories[y])
            judge.append(categories[y])
            # print("| comment:", comments[y])
            pre_list.append([files[i], cat_num[y]])
    except Exception as e:
        print("[2_] Error: ", e)

    # ラベル判定の記録データファイルの作成
    print("ラベル判定の記録データファイルの作成")
    filename = "_judge_his.txt"
    try:
        if not os.path.exists(filename):
            with open(filename, "w", encoding='utf-8') as fp:
                fp.write("")
        with open(filename, "a", encoding='utf-8') as fp:
            for j in range(len(pre_list)):
                text = input[j] + ": " + judge[j] + "\n"
                fp.write(text)
    except Exception as e:
        print("[3_] Error: ", e)

    os.chdir("path_to_bot_script")  # カレントディレクトリを元に戻す

    return pre_list  # SSS:1, notSSS:0, noise:-1

# モデルを構築
def build_model(in_shape, nb_classes):
    print("build_model()")
    try:
        model = Sequential()
        model.add(Conv2D(32, (3, 3),
                         padding='same',
                         input_shape=in_shape))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))
        model.add(Conv2D(64, (3, 3), padding='same'))
        model.add(Activation('relu'))
        model.add(Conv2D(64, (3, 3)))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(512))
        model.add(Activation('relu'))
        model.add(Dropout(0.5))
        model.add(Dense(nb_classes))
        model.add(Activation('softmax'))
        model.compile(loss='binary_crossentropy',
                      optimizer='rmsprop',
                      metrics=['accuracy'])
        return model
    except Exception as e:
        print("[4_] Error: ", e)
