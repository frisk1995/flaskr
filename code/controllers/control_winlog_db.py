# This class Control Windows log database
import sqlite3
import time
from config import global_value as glv


class control_winlog_db():
    def __init__(self):
        print("call control_winlog_db")

    def init_db():
        # データベースを新規作成 or 読み込み
        con = sqlite3.connect(
            glv.WIN_DB_FILEPATH,
            isolation_level=None,
        )
        # テーブル初期化
        sql = """
        DROP TABLE IF EXISTS WINLOG
        """
        con.execute(sql)

        # テーブル作成用SQL
        sql = """
        CREATE TABLE IF NOT EXISTS WINLOG (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level VARCHAR(256),
            date VARCHAR(256),
            source VARCHAR(256),
            eventid INTEGER,
            category VARCHAR(256),
            data VARCHAR(256)
        );
        """
        con.execute(sql)  # sql文を実行
        con.commit()
        con.close()
        return con

    def open_log_file(filepath):
        con = sqlite3.connect(glv.WIN_DB_FILEPATH)
        db_err_flag = ""
        with open(filepath) as f:
            flag = False  # 行中にダブルクォーテーションが含まれない
            num = 0  # ヘッダースキップ用関数
            for line in f:
                # 改行コードの削除
                line = line.replace('\n', '')
                arrData = ""

                # 最終行
                if '\"' in line and flag == True:
                    long_data += '\n' + line.replace('\"', '')
                    flag = False
                    arrData = long_data.split(',')
                # 詳細カラムの改行後のデータの場合
                elif flag == True:
                    long_data += "\n" + line
                # 初回
                elif '\"' in line and flag == False:
                    flag = True
                    long_data = line.replace('\"', '')
                    num = 1
                    continue
                # 詳細カラムにダブルクォーテが含まれない
                else:
                    arrData = line.split(',')

                # 配列にデータがあれば処理する
                if arrData != "" and num != 0:
                    db_err_flag = control_winlog_db.insert_log_data(arrData, con)
                num = 1
        con.commit()
        con.close()
        return db_err_flag

    # sqliteへのinsert処理
    def insert_log_data(log_data, con):
        cur = con.cursor()
        flag = True
        # データベースにデータを挿入
        sql = 'INSERT INTO WINLOG (level, date, source, eventid, category, data) values (?,?,?,?,?,?)'
        try:
            cur.execute(sql, log_data)
        except:
            flag = False

        return flag

    # DBをテーブル表示
    def result_db():
        con = sqlite3.connect(glv.WIN_DB_FILEPATH)
        cur = con.cursor()
        sql = """
        SELECT * FROM WINLOG;
        """
        cur.execute(sql)
        data = cur.fetchall()
        con.close()
        return data

    def search_db(query, select_query):
        con = sqlite3.connect(glv.WIN_DB_FILEPATH)
        cur = con.cursor()
        if select_query == "":
            sql = """
            SELECT * FROM WINLOG WHERE
            level LIKE ? OR
            date LIKE ? OR
            source LIKE ? OR
            eventid LIKE ? OR
            category LIKE ? OR
            data LIKE ?
            """
            cur.execute(sql, ('%' + query + '%', '%' + query + '%', '%' + query +
                        '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
        else:
            sql = f"""
            SELECT * FROM WINLOG WHERE {select_query} LIKE ?
            """
            cur.execute(sql, ('%' + query + '%',))
        data = cur.fetchall()
        con.close()
        return data
