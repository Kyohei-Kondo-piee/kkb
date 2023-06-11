# 1.標準ライブラリ
from   datetime import datetime as dt
import configparser as cp
import os
import logging

# 2.サードパーティ製ライブラリ
import pandas as pd
import psycopg2
from   psycopg2 import extras


def execute_sql(logger, config, sql, command, data):
    """
    args:
        logger : log用オブジェクト
        config : setting.ini読込結果
        sql    : SQL文(str)
        command: CRUD等の区別(詳細は本モジュールのソース参照)
        data   : INSERT,UPDATE等のデータ(OPTIONAL)
    """
    # ﾃﾞﾊﾞｯｸﾞ用
    logger.log(20, '{}'.format(sql))
    logger.log(20, '{}'.format(data))

    try:
        # 接続
        conn = psycopg2.connect(
            host       = config['DWH']['HOSTNAME']
            , port     = config['DWH']['PORT']
            , dbname   = config['DWH']['DBNAME']
            , user     = config['DWH']['USER']
            , password = config['DWH']['PASSWORD']
        )

        # クエリ種別ごとの処理
        if command == 'select':
            # SQL実行
            cur = conn.cursor()
            cur.execute(sql)
            get_data = cur.fetchall()
            
            # 終了処理
            try:
                cur.close()
            except:
                pass
            conn.close()
            
            return get_data

        elif command in ['insert', 'delete', 'alter']:
            # SQL実行
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            
            # 終了処理
            try:
                cur.close()
            except:
                pass
            conn.close()

            return

        elif command == 'bulk_insert':
            """
            ・バルクインサートにはpsycopg2.extras を使用すること
            ・dfのままだとindexが邪魔なのでlist化してから渡すこと
            ・upsertも可。この関数に渡すSQL文で実装すること
            """
            logger.log(20,'bulk_insert STRAT')

            # SQL実行
            cur = conn.cursor()
            extras.execute_values(cur, sql, data)
            conn.commit()

            # 終了処理
            try:
                logger.log(20,'bulk_insert CURSOR_CLOSE')
                cur.close()
            except Exception as e:
                logger.log(100,'bulk_insert CURSOR_CLOSE ERROR {}'.format(e))
                pass
            
            conn.close()
            logger.log(20,'bulk_insert CONN_CLOSE')

            return

        else:
            try:
                cur.close()
            except:
                pass
            conn.close()
    except Exception as e:
        logger.log(100, 'エラーです {}'.format(e))

    return