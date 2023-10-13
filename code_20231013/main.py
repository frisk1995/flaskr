# ==========================================================================
# 検索の前にタグを用意する
#
#
# ==========================================================================

from flask import Flask, render_template, request, redirect, url_for, session
from lib import control_winlog_db as cwd
import sqlite3
app = Flask(__name__)
# sessionで使う暗号化キーの定義
app.config['SECRET_KEY'] = 'secret_key'
# Windows用クラスのインスタンス化
ctlWinDB = cwd.control_winlog_db

# indexページの呼び出し


@app.route("/")
def index():
    return render_template('index.html')

# windows用ログページの呼び出し


@app.route("/winlog")
def winlog():
    ctlWinDB.init_db()
    return render_template('winlog.html')


@app.route("/winlog_view")
def winlog_view():
    winlog_data = ctlWinDB.result_db()

    print(winlog_data)
    return render_template('winlog_view.html', winlog_data=winlog_data)


@app.route("/sample_view")
def sample_view():
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = ctlWinDB.result_db()[offset:offset + table_limit]
    total_pages = (len(ctlWinDB.result_db()) +
                   table_limit - 1) // table_limit  # 総ページ数の計算
    return render_template('sample.html', tables=tables, limit=table_limit, page=page, total_pages=total_pages)

# 検索結果表示用ページのルーティング


@app.route("/sample_search")
def sample_search():
    query = session["query"]
    select_query = session["select_query"]
    table_data = ctlWinDB.search_db(query, select_query)
    table_limit = 10  # 表示上限を10に設定
    page = int(request.args.get('page', 1))  # リクエストパラメータからページ番号を取得
    offset = (page - 1) * table_limit
    tables = table_data[offset:offset + table_limit]
    total_data_length = len(ctlWinDB.search_db(query, select_query))
    total_pages = (total_data_length + table_limit - 1) // table_limit
    return render_template('sample_search.html', tables=tables, limit=table_limit, page=page, total_pages=total_pages, tdl=total_data_length)

# ファイルアップロード処理


@app.route("/upload_winlog", methods=["POST"])
def upload():
    ctlWinDB.init_db()
    f = request.files["datafile"]
    f.save("/code/inputfile/winlog.csv")
    # ファイルアップロードしてDBを作成する関数の呼び出し
    ctlWinDB.open_log_file()
    return render_template('winlog.html')


@app.route("/sample_view_search")
def sample_view_search():
    query = request.args.get('query', '')  # リクエストパラメータから検索クエリを取得
    select_query = request.args.get('select-query', '')
    session["query"] = query
    session["select_query"] = select_query
    return redirect(url_for('sample_search', query=query, select_query=select_query))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
