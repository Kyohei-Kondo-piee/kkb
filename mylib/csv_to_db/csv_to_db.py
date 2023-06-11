# 1. 標準ライブラリ
import glob
import os
import re
import sys

# 2. サードパーティ製
import pandas as pd
import psycopg2

# 3.自作ライブラリ
sys.path.append('../')
from   mylib.prepro_csv   import prepro_csv as ppc
from   mylib.psycopg2_ext import psycopg2_ext

def csv_to_db(config, logger):
    """
    insert "invest.com" csv file into db
    """
    # read csv file
    # ・don't put file apart from csv

    # change current directory to csv folder
    # os.chdir(r'{0}\kabu_data'.format(config['CSV']['PATH']))
    # os.chdir(csv_path)
    os.chdir(config['CSV']['PATH'])
    current_dir=os.path.abspath(".")
    current_dir=os.getcwd()

    # 対象フォルダにある、拡張子がcsvのファイル名を取得しリスト化
    tbl_data_file=os.path.join(current_dir, '*.csv')
    tbl_data_files=glob.glob(tbl_data_file)

    # デバッグ用_読み込んだファイル名出力
    # for i in range(len(tbl_data_files)):
    #     print(tbl_data_files[i])

    # csvファイルごとにDataFrameにしてからリスト化
    csv_data_list = []
    for i in range(len(tbl_data_files)):
        csv_data_list.append(pd.read_csv(tbl_data_files[i],parse_dates=[0]))

    # 読み込んだcsvファイルのファイル名を加工して取得
    # ・拡張子を除去
    # ・半角スペース以後(過去データ等の文字列)を除去
    # ・いったん日本語のまま(そのうち変えるかも)
    csv_name_list = []
    for f in os.listdir(current_dir):
        if os.path.isfile(os.path.join(current_dir,f)):
            ff=re.search(r'\S+\s\S+\.',f)
            # print(ff)
            fff=ff.group()
            csv_name_list.append(fff[:-1].replace(' 先物の過去データ','' \
                                        ).replace(' 過去データ','')+'_日足')

    # カレントディレクトリを実行フォルダに戻す
    # os.chdir(path_pro)

    # CSVファイルごとにバルクインサート
    for i in range(len(csv_data_list)):

        # SQL文作成
        sql = r"""
               insert into public."{}" values %s on conflict do nothing
               """.format(csv_name_list[i])

        # insert用にデータ整形(Investing.comデータ専用モジュール)
        insert_data = ppc.prepro_csv_inv(csv_data_list[i], logger)

        # SQL実行
        psycopg2_ext.execute_sql(logger, config, sql, 'bulk_insert'
                             , insert_data.to_numpy().tolist())
