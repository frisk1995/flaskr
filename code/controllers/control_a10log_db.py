# This class Control Windows log database
import sqlite3
import time
from config import global_value as glv
import re


class control_a10log_db():
    def __init__(self):
        print("call control_a10log_db")

    def init_db():
        # データベースを新規作成 or 読み込み
        con = sqlite3.connect(
            glv.A10_DB_FILEPATH,
            isolation_level=None,
        )
        # テーブル初期化
        sql = """
        DROP TABLE IF EXISTS a10log
        """
        con.execute(sql)

        # テーブル作成用SQL
        sql = """
        CREATE TABLE IF NOT EXISTS a10log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            type TEXT,
            response TEXT,
            from_add TEXT,
            to_add TEXT,
            to_domain TEXT,
            to_url TEXT
        );
        """
        con.execute(sql)  # sql文を実行
        con.commit()
        con.close()
        return con

    def open_log_file(filepath):
        con = sqlite3.connect(glv.A10_DB_FILEPATH)
        with open(filepath) as f:
            flag = False  # 行中にダブルクォーテーションが含まれない
            for line in f:
                arrData = []
                # 改行コードの削除
                tmpArr = line.split('Proxy')
                date = control_a10log_db.getDate(tmpArr[0])
                value_type = control_a10log_db.getType(tmpArr[1])
                value_response = control_a10log_db.getResponse(tmpArr[1])
                value_fromadd = control_a10log_db.getFromAdd(tmpArr[1])
                value_toadd = control_a10log_db.getToAdd(tmpArr[1])
                value_todomain = control_a10log_db.getToDomain(tmpArr[1])
                value_toUrl = control_a10log_db.getToUrl(tmpArr[1])
                arrData.append(date)
                arrData.append(value_type)
                arrData.append(value_response)
                arrData.append(value_fromadd)
                arrData.append(value_toadd)
                arrData.append(value_todomain)
                arrData.append(value_toUrl)
                control_a10log_db.insert_log_data(arrData, con)

        con.commit()
        con.close()

    # sqliteへのinsert処理
    def insert_log_data(log_data, con):
        cur = con.cursor()
        # データベースにデータを挿入
        sql = 'INSERT INTO a10log (date, type, response, from_add, to_add, to_domain, to_url) values (?,?,?,?,?,?,?)'
        cur.execute(sql, log_data)

    # DBをテーブル表示
    def result_db():
        con = sqlite3.connect(glv.A10_DB_FILEPATH)
        cur = con.cursor()
        sql = """
        SELECT * FROM a10log;
        """
        cur.execute(sql)
        data = cur.fetchall()
        con.close()
        return data

    def search_db(query, select_query):
        con = sqlite3.connect(glv.A10_DB_FILEPATH)
        cur = con.cursor()
        if select_query == "":
            sql = """
            SELECT * FROM a10log WHERE
            date LIKE ? OR
            type LIKE ? OR
            response LIKE ? OR
            from_add LIKE ? OR
            to_add LIKE ? OR
            to_domain LIKE ? OR
            to_url LIKE ?
            """
            cur.execute(sql, ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query +
                        '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
        else:
            sql = f"""
            SELECT * FROM a10log WHERE {select_query} LIKE ?
            """
            cur.execute(sql, ('%' + query + '%',))
        data = cur.fetchall()
        con.close()
        return data

# dateを取得する関数
    def getDate(str):
        date = str.split(' ')[0]+" "+str.split(' ')[1] + \
            " "+str.split(' ')[2]+" "+str.split(' ')[3]
        return date

# typeを取得する関数
    def getType(str):
        result = re.search(r'([^\[]+)', str)
        value_type = result.group(1)if result else ""
        return value_type

# Responseを取得する関数
    def getResponse(str):
        result = re.search(r'\[([^\]]+)\]', str)
        response = result.group(1)if result else ""
        return response

# FromAddressを取得する関数
    def getFromAdd(str):
        result = re.search(r'from (.*?),', str)
        fromAdd = result.group(1) if result else ""
        return fromAdd

# ToAddressを取得する関数
    def getToAdd(str):
        result = re.search(r'to (\S+)', str)
        toAdd = result.group(1) if result else ""
        return toAdd

# ToDomainを取得する関数
    def getToDomain(str):
        result = re.search(r'\]:([^ ]+)', str)
        toDomain = result.group(1) if result else ""
        return toDomain

# ToURLを取得する関数
    def getToUrl(str):
        result = re.search(r'url (\S+)', str)
        toUrl = result.group(1) if result else ""
        return toUrl
