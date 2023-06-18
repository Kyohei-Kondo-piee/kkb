# 1.standard

# 2.third_party
import numpy  as np
import pandas as pd

# 3.self_maid
from ..fsc import fsc

def data_processing(df, train_rc, n_rnn):
    """
    data processing to RNN
    Args:
        df(pandas.DataFrame): data to RNN
        train_rc(int): number of record to train
        n_rnn(int): number of RNN unit
    """
    # x_train,y_train(説明変数・目的変数)に用いるカラムを選択
    # ついでに件数も指定(元データをモデル作成用と予測テスト用に分ける)

    # ■入力項目■
    # object_col : 目的変数のカラム番号を指定
    # ※他は全て説明変数にするので、外したいカラムはpopするか
    #   そもそもSQLで取らないこと
    object_col = set([0,1,2,3])
    train_col  = set(range(len(df.columns))) ^ object_col
    object_col = list(object_col)
    train_col  = list(train_col)

    # ■入力項目■
    # train_rc : 学習用データに使用するレコード数を指定
    all_rc   = len(df)
    # train_rc = 200
    test_rc  = all_rc - train_rc

    # 後で比較に使用するために目的変数のDataFrameを退避させておく
    df_object = df.iloc[:,object_col]
    df_train  = df.iloc[train_rc:,train_col]

    # 目的変数カラムの値を過去方向に１レコードずらす
    # ・前日の説明変数と、今日の目的変数を紐づける
    for i in range(len(object_col)):
        df[df.columns[object_col[i]]] = df[df.columns[object_col[i]]].shift(-1)

    # ずらしてNanが生じたレコードを削除
    df = df.dropna(axis=0, how='any')

    # 学習用・検証用データセット作成
    df_x_train = df.iloc[0:train_rc,train_col]
    df_y_train = df.iloc[0:train_rc,object_col]
    df_x_test  = df.iloc[train_rc:,train_col]
    df_y_test  = df.iloc[train_rc:,object_col] # 検証用データはずらす前に作った方がよい？
    df_index   = df_x_test.index

    # ■予測用データ加工
    # kerasに渡すためにndarrayに変換する

    # 書き換え用listを宣言(要素数分の配列長が必要)
    x_train = [0]*len(df_x_train)
    y_train = [0]*len(df_y_train)
    x_test  = [0]*len(df_x_test)
    y_test  = [0]*len(df_y_test)

    i = 0
    while i < len(df_x_train):
        x_train[i] = np.array(df_x_train.iloc[i,:]).astype(np.float32)
        y_train[i] = np.array(df_y_train.iloc[i,:]).astype(np.float32)
        i += 1

    i = 0
    while i < len(df_x_test):
        x_test[i] = np.array(df_x_test.iloc[i,:]).astype(np.float32)
        i += 1

    i = 0
    while i < len(df_y_test):
        y_test[i] = np.array(df_y_test.iloc[i,:]).astype(np.float32)
        i += 1

    # kerasに渡す時はndarrayに変換する
    x_train = np.array(x_train)
    y_train = np.array(y_train)
    x_test  = np.array(x_test)
    y_test  = np.array(y_test)

    # RNN用処理
    # ・timestepsぶんのずらしデータを作成
    # n_rnn    = 15  # 時系列の数
    n_sample = len(df)-n_rnn  # サンプル数
    df_x = pd.DataFrame([])
    df_y = pd.DataFrame([])

    for i in range(0, n_sample):
        df_x = pd.concat([df_x, df.iloc[i:i+n_rnn,train_col]])
        df_y = pd.concat([df_y, df.iloc[i+1:i+n_rnn+1,object_col]])

    ary_x = df_x.to_numpy().reshape(n_sample, n_rnn, len(df_x.columns))
    ary_y = df_y.to_numpy().reshape(n_sample, n_rnn, len(df_y.columns))

    # 学習用・検証用データセット作成
    x_train = ary_x[0:train_rc]
    y_train = ary_y[0:train_rc]
    x_test  = ary_x[train_rc:]
    y_test  = ary_y[train_rc:]

    # Decimal型は禁止なので変換
    x_train = x_train.astype(np.float32)
    y_train = y_train.astype(np.float32)
    x_test  = x_test.astype(np.float32)
    y_test  = y_test.astype(np.float32)

    # 逆変換用のパラメータを記憶
    y_train_sol = [0,0]
    y_train_sol = [y_train[:,0].mean(axis=None, keepdims=True)
                   , np.std(y_train[:,0], axis=None, keepdims=True)]

    # 特徴量スケーリング(標準化)
    for i in range(x_train.shape[1]):
        x_train[:,i], x_train_mean, x_train_std = fsc.zscore(x_train[:,i])
    for i in range(x_test.shape[1]):
        x_test[:,i],  x_test_mean, x_test_std  = fsc.zscore(x_test[:,i])

    return df_object, df_train, x_test, y_test, x_train, y_train