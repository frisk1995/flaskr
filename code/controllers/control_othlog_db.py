# This class Control othdows log database
import sqlite3
import time
from config import global_value as glv
import os
import re


class control_othlog_db():
    def __init__(self):
        print("call control_othlog_db")

    def init_db(filepath):
        header_list = control_othlog_db.getHeaders(filepath)
        # データベースを新規作成 or 読み込み
        con = sqlite3.connect(
            glv.OTH_DB_FILEPATH,
            isolation_level=None,
        )
        # テーブル初期化
        sql = """
        DROP TABLE IF EXISTS OTHLOG
        """
        con.execute(sql)

        # テーブル作成用SQL
        columns = ", ".join([f"{header} TEXT" for header in header_list])
        sql = f"""
        CREATE TABLE OTHLOG (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns}
        );
        """
        con.execute(sql)  # sql文を実行
        con.commit()
        con.close()
        return con

    def open_log_file(filepath):
        con = sqlite3.connect(glv.OTH_DB_FILEPATH)
        db_err_flag = ""
        with open(filepath) as f:
            flag = False  # 行中にダブルクォーテーションが含まれない
            num = 0  # ヘッダースキップ用関数
            for line in f:
                # 改行コードの削除
                line = line.replace('\n', '')
                arrData = line.split(',')

                # 配列にデータがあれば処理する
                if arrData != "" and num != 0:
                    db_err_flag = control_othlog_db.insert_log_data(
                        arrData, con)
                num = 1

        con.commit()
        con.close()
        return db_err_flag

    # sqliteへのinsert処理
    def insert_log_data(log_data, con):
        cur = con.cursor()
        flag = True
        # データベースにデータを挿入
        table_headers = control_othlog_db.get_table_columns()
        table_headers.pop(0)
        if len(log_data) != len(table_headers):
            print("Error: log_data and table_headers must have the same length.")
            return False

        # データベースにデータを挿入
        placeholders = ', '.join(['?'] * len(log_data))
        columns = ', '.join(table_headers)

        # SQLクエリを修正
        sql = f'INSERT INTO OTHLOG ({columns}) VALUES ({placeholders})'

        try:
            cur.execute(sql, log_data)
        except sqlite3.Error as e:
            print(f"Error executing SQL query: {e}")
            flag = False

        return flag

    # DBをテーブル表示
    def result_db():
        con = sqlite3.connect(glv.OTH_DB_FILEPATH)
        cur = con.cursor()
        sql = """
        SELECT * FROM OTHLOG;
        """
        cur.execute(sql)
        data = cur.fetchall()
        con.close()
        return data

    def search_db(query, select_query):
        con = sqlite3.connect(glv.OTH_DB_FILEPATH)
        cur = con.cursor()
        table_headers = control_othlog_db.get_table_columns()
        table_headers.pop(0)
        if select_query == "":
            columns = "OR ".join(
                [f"{header} LIKE ?" for header in table_headers])
            placeholders = '%' + query + '%'
            sql = f"""
            SELECT * FROM OTHLOG WHERE {columns}
            """
            # クエリ実行時に正しいプレースホルダーを指定します
            cur.execute(sql, ([placeholders] * len(table_headers)))
        else:
            sql = f"""
            SELECT * FROM OTHLOG WHERE {select_query} LIKE ?
            """
            cur.execute(sql, ('%' + query + '%',))

        data = cur.fetchall()
        con.close()
        return data


# ファイルを削除する関数

    def deleteFile(filepath):
        os.remove(filepath)

    def getHeaders(filepath):
        with open(filepath, "r") as file:
            first_line = file.readline()
        list = first_line.split(',')
        header_list = [re.sub(r'\s+', '', item) for item in list]
        return header_list

    # DBからテーブルのカラムのみ取得

    def get_table_columns():
        # SQLiteデータベースに接続
        conn = sqlite3.connect(glv.OTH_DB_FILEPATH)
        cursor = conn.cursor()

        # テーブルのカラム情報を取得
        cursor.execute(f"PRAGMA table_info(OTHLOG)")
        columns = cursor.fetchall()

        # カラム名を抽出して配列に格納
        column_names = [column[1] for column in columns]

        # 接続を閉じる
        conn.close()
        header_list = []
        for str in column_names:
            header_list.append(str.replace('id', '#'))
        return header_list
