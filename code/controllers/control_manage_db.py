# This class Control Windows log database
import sqlite3
import time
from config import global_value as glv

class control_manage_db():
    def __init__(self):
        print("call control_mng_db")

    def init_db():
        # データベースを新規作成 or 読み込み
        con = sqlite3.connect(
            glv.UPLOADS_MNG_DB,
            isolation_level=None,
        )
        # テーブル初期化
        sql = """
        DROP TABLE IF EXISTS manage
        """
        con.execute(sql)

        # テーブル作成用SQL
        sql = """
        CREATE TABLE IF NOT EXISTS manage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            filename TEXT
        );
        """
        con.execute(sql)  # sql文を実行
        con.commit()
        con.close()
        return con
