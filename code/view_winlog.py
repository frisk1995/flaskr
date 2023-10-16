from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, flash
from controllers import control_winlog_db as cwd
import sqlite3
import os
import datetime
import glob
from config import global_value as glv

app = Flask(__name__)

view_winlog_module = Blueprint("view_winlog", __name__)

# sessionで使う暗号化キーの定義
app.config['SECRET_KEY'] = 'secret_key'

# Windows用クラスのインスタンス化
ctlWinDB = cwd.control_winlog_db

# windows用ログページの呼び出し


@view_winlog_module.route("/winlog")
def winlog():
    winlog_uploads_files = getFilelist("winlog")
    ctlWinDB.init_db()
    return render_template('winlog/winlog.html', win_file_list=winlog_uploads_files)


def getFilelist(target):
    result = []
    log_list = glob.glob(glv.UPLOADS_DIR+"/"+target+"/*")
    for file in log_list:
        tmp_array = []
        file_timestamp = datetime.datetime.fromtimestamp(
            os.path.getmtime(file))
        tmp_array.append(file_timestamp.strftime('%Y/%m/%d-%H:%M:%S'))
        tmp_array.append(file.split("/")[5])
        result.append(tmp_array)
    return result
# 初回の結果表示用プログラム


@view_winlog_module.route("/winlog_view")
def winlog_view():
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = ctlWinDB.result_db()[offset:offset + table_limit]
    total_pages = (len(ctlWinDB.result_db()) +
                   table_limit - 1) // table_limit  # 総ページ数の計算
    return render_template('winlog/winlog_view.html', tables=tables, limit=table_limit, page=page, total_pages=total_pages)

# 検索結果表示用ページのルーティング


@view_winlog_module.route("/winlog_search")
def winlog_search():
    query = session["query"]
    select_query = session["select_query"]
    table_data = ctlWinDB.search_db(query, select_query)
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = table_data[offset:offset + table_limit]
    total_data_length = len(ctlWinDB.search_db(query, select_query))
    total_pages = (total_data_length + table_limit - 1) // table_limit
    return render_template('winlog/winlog_search.html', tables=tables, limit=table_limit, page=page, total_pages=total_pages, tdl=total_data_length)

# ファイルアップロード処理


@view_winlog_module.route("/upload_winlog", methods=["POST"])
def upload():
    ctlWinDB.init_db()
    file = request.files["datafile"]
    filepath = glv.WIN_CSV_FILEPATH + file.filename
    file.save(filepath)
    # ファイルアップロードしてDBを作成する関数の呼び出し
    flag = ctlWinDB.open_log_file(filepath)
    return render_template('winlog/winlog.html')

# 検索結果文字列を取得してセッションに格納する


@view_winlog_module.route("/winlog_view_search")
def winlog_view_search():
    query = request.args.get('query', '')  # リクエストパラメータから検索クエリを取得
    select_query = request.args.get('select-query', '')
    session["query"] = query
    session["select_query"] = select_query
    return redirect(url_for('view_winlog.winlog_search', query=query, select_query=select_query))
