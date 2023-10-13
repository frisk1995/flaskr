from flask import Flask, render_template, request, redirect, url_for, session, Blueprint
from controllers import control_a10log_db as cwd
import sqlite3
from config import global_value as glv

app = Flask(__name__)

view_a10log_module = Blueprint("view_a10log", __name__)

# sessionで使う暗号化キーの定義
app.config['SECRET_KEY'] = 'secret_key'

# Windows用クラスのインスタンス化
ctlA10DB = cwd.control_a10log_db

# windows用ログページの呼び出し


@view_a10log_module.route("/a10log")
def a10log():
    ctlA10DB.init_db()
    return render_template('a10log/a10log.html')

# 初回の結果表示用プログラム


@view_a10log_module.route("/a10log_view")
def a10log_view():
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = ctlA10DB.result_db()[offset:offset + table_limit]
    total_pages = (len(ctlA10DB.result_db()) +
                   table_limit - 1) // table_limit  # 総ページ数の計算
    return render_template('a10log/a10log_view.html', tables=tables, limit=table_limit, page=page, total_pages=total_pages)

# 検索結果表示用ページのルーティング


@view_a10log_module.route("/a10log_search")
def a10log_search():
    query = session["query"]
    select_query = session["select_query"]
    table_data = ctlA10DB.search_db(query, select_query)
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = table_data[offset:offset + table_limit]
    total_data_length = len(ctlA10DB.search_db(query, select_query))
    total_pages = (total_data_length + table_limit - 1) // table_limit
    return render_template('a10log/a10log_search.html', tables=tables, limit=table_limit, page=page, total_pages=total_pages, tdl=total_data_length)

# ファイルアップロード処理


@view_a10log_module.route("/upload_a10log", methods=["POST"])
def upload():
    ctlA10DB.init_db()
    f = request.files["datafile"]
    f.save(glv.A10_CSV_FILEPATH)
    # ファイルアップロードしてDBを作成する関数の呼び出し
    ctlA10DB.open_log_file()
    return render_template('a10log/a10log.html')

# 検索結果文字列を取得してセッションに格納する


@view_a10log_module.route("/a10log_view_search")
def a10log_view_search():
    query = request.args.get('query', '')  # リクエストパラメータから検索クエリを取得
    select_query = request.args.get('select-query', '')
    session["query"] = query
    session["select_query"] = select_query
    return redirect(url_for('view_a10log.a10log_search', query=query, select_query=select_query))
