# 2.サードパーティ製ライブラリ
import pandas as pd

def calc_day_to_week(df_daily):
    """
    日次データを週次データに集計する    
    """
    # カラム名付与
    col_name = list(map(str,list(range(1, len(df_daily.columns)+1))))
    df_daily.columns = col_name

    # 週次への変換
    # ■入力項目■
    # ・SQL結果から、更に必要なカラムだけを指定
    # ・カラムごとに集計方法を指定(基本的に固定)
    # ・手間なので何かやり方を考えたい
    df_weekly = df_daily.resample("W")\
                        .agg({"1":"last",  "2":"first",  "3":"max",  "4":"min"
                             ,"7":"last",  "8":"first",  "9":"max",  "10":"min"
                             ,"13":"last", "14":"first", "15":"max", "16":"min"
                             ,"19":"last", "20":"first", "21":"max", "22":"min"
                             ,"25":"last", "26":"first", "27":"max", "28":"min"
                             ,"30":"last", "31":"first", "32":"max", "33":"min"
                             ,"35":"last", "36":"first", "37":"max", "38":"min"
                             ,"40":"last", "41":"first", "42":"max", "43":"min"
                             ,"45":"last", "46":"first", "47":"max", "48":"min"
                             ,"51":"last", "52":"first", "53":"max", "54":"min"
                             ,"57":"last", "58":"first", "59":"max", "60":"min"
                             })

    # １件もデータが無かった週を削除
    df_weekly = df_weekly.dropna(axis=0, how='any')

    return df_weekly