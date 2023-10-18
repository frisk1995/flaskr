from flask import Flask, render_template, request, redirect, url_for, session, Blueprint, flash
from controllers import control_othlog_db as cwd
import sqlite3
import os
import datetime
import glob
from config import global_value as glv

app = Flask(__name__)

view_othlog_module = Blueprint("view_othlog", __name__)

# sessionで使う暗号化キーの定義
app.config['SECRET_KEY'] = 'secret_key'

# othdows用クラスのインスタンス化
ctlothDB = cwd.control_othlog_db

# othdows用ログページの呼び出し


@view_othlog_module.route("/othlog")
def othlog():
    othlog_uploads_files = getFilelist("othlog")
#    ctlothDB.init_db()
    return render_template('othlog/othlog.html', oth_file_list=othlog_uploads_files)


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


@view_othlog_module.route("/othlog_view")
def othlog_view():
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = ctlothDB.result_db()[offset:offset + table_limit]
    table_headers = ctlothDB.get_table_columns()
    table_headers.pop(0)
    total_pages = (len(ctlothDB.result_db()) +
                   table_limit - 1) // table_limit  # 総ページ数の計算
    return render_template('othlog/othlog_view.html', tables=tables, table_headers=table_headers, limit=table_limit, page=page, total_pages=total_pages)

# 検索結果表示用ページのルーティング


@view_othlog_module.route("/othlog_search")
def othlog_search():
    query = session["query"]
    select_query = session["select_query"]
    table_data = ctlothDB.search_db(query, select_query)
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = table_data[offset:offset + table_limit]
    table_headers = ctlothDB.get_table_columns()
    table_headers.pop(0)
    total_data_length = len(ctlothDB.search_db(query, select_query))
    total_pages = (total_data_length + table_limit - 1) // table_limit
    return render_template('othlog/othlog_search.html', tables=tables, table_headers=table_headers, limit=table_limit, page=page, total_pages=total_pages, tdl=total_data_length)

# ファイルアップロード処理


@view_othlog_module.route("/upload_othlog", methods=["POST"])
def upload():
    file = request.files["datafile"]
    filepath = glv.OTH_CSV_FILEPATH + file.filename
    file.save(filepath)
    ctlothDB.init_db(filepath)
    # ファイルアップロードしてDBを作成する関数の呼び出し
    flag = ctlothDB.open_log_file(filepath)
    return render_template('othlog/othlog.html')

# 検索結果文字列を取得してセッションに格納する


@view_othlog_module.route("/othlog_view_search")
def othlog_view_search():
    query = request.args.get('query', '')  # リクエストパラメータから検索クエリを取得
    select_query = request.args.get('select-query', '')
    session["query"] = query
    session["select_query"] = select_query
    return redirect(url_for('view_othlog.othlog_search', query=query, select_query=select_query))

# ログファイルを開く


@view_othlog_module.route("/othlog_open_file")
def othlog_open_file():
    othlog_openfile = glv.OTH_CSV_FILEPATH+request.args.get('openfile', '')
    ctlothDB.init_db(othlog_openfile)
    flag = ctlothDB.open_log_file(othlog_openfile)
    print(othlog_openfile)
    return redirect(url_for('view_othlog.othlog_view'))

# ファイル削除のルーティング


@view_othlog_module.route("/othlog_delete_file")
def othlog_delete_file():
    othlog_deletefile = glv.OTH_CSV_FILEPATH+request.args.get('deletefile', '')
    ctlothDB.init_db(othlog_deletefile)
    flag = ctlothDB.deleteFile(othlog_deletefile)
    return redirect(url_for('view_othlog.othlog'))
