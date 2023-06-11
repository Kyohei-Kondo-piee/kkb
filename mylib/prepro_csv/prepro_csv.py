# 1.標準ライブラリ
from   datetime import datetime as dt
import os
import re

# 2.サードパーティ製ライブラリ
import pandas as pd


def prepro_csv_inv(csv, logger):

    """
    Investing.comから取得したcsvファイル専用の前処理関数
    
    parameter
    -----------
    csv : DataFrame
    
    """

    # 日付がtimestamp型ではない(str)場合は変換フラグを立てる
    if csv.iloc[0,0] is str:
        # 日付のフォーマットを判定
        if   len(re.findall(r'\b\d{4}年\d+月\d+日\b', csv.iloc[0,0])) > 0:
            mode = 1
        elif len(re.findall(r'\b\d{4}-\d+-\d+\b',     csv.iloc[0,0])) > 0:
            mode = 2
        elif len(re.findall(r'\b\d{4}/\d+/\d+\b',     csv.iloc[0,0])) > 0:
            mode = 3
        else:
            mode = 9
    else:
        mode = 0

    # 出来高を数値に変換
    for i in range(len(csv)):

        try:
            # 日付が文字列の場合はtimestampに変換
            # ※銘柄によってCSVのフォーマットが微妙に異なる模様
            if mode == 0:
                pass
            elif mode == 1:
                csv.iloc[i,0] = dt.strptime(csv.iloc[i,0], '%Y年%m月%d日')
            elif mode == 2:
                csv.iloc[i,0] = dt.strptime(csv.iloc[i,0], '%Y-%m-%d')
            elif mode == 3:
                csv.iloc[i,0] = dt.strptime(csv.iloc[i,0], '%Y/%m/%d')
            elif mode == 9:
                pass

            # 終値～安値のカンマを削除
            # ・改造作業中
            #   CSVの価格のカラムがダブルコーテーション囲みの場合と数値の場合があった
            #   数値の場合はreplace不要(不可)でエラーになるので分岐が必要
            if type(csv.iloc[i,1]) == str:
                csv.iloc[i,1] = csv.iloc[i,1].replace(',','')
            if type(csv.iloc[i,2]) == str:
                csv.iloc[i,2] = csv.iloc[i,2].replace(',','')
            if type(csv.iloc[i,3]) == str:
                csv.iloc[i,3] = csv.iloc[i,3].replace(',','')
            if type(csv.iloc[i,4]) == str:
                csv.iloc[i,4] = csv.iloc[i,4].replace(',','')

            # 出来高を数値に変換
            # NULL値はNoneにする
            if pd.isna(csv.iloc[i,5]) == True:
                csv.iloc[i,5] = None

            elif csv.iloc[i,5][-1] == 'B':
                csv.iloc[i,5] = str(float(csv.iloc[i,5][:-1])*1000000)

            elif csv.iloc[i,5][-1] == 'M':
                csv.iloc[i,5] = str(float(csv.iloc[i,5][:-1])*1000)

            elif csv.iloc[i,5][-1] == 'K':
                csv.iloc[i,5] = csv.iloc[i,5][:-1]

            elif csv.iloc[i,5][-1] == '-':
                csv.iloc[i,5] = None


            # 前日比からパーセントを削除
            csv.iloc[i,6] = csv.iloc[i,6][:-1]

        except Exception as e:
            logger.log(100, csv.iloc[i])
            logger.log(100, e)

    return csv