from flask import Flask, render_template, request, redirect, url_for, session
from view_winlog import view_winlog_module
from view_a10log import view_a10log_module
from controllers import control_winlog_db as cwd
from config import global_value as glv
import sqlite3
import glob

# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = '/code/data/uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

app = Flask(__name__, static_folder='/code/static/', static_url_path="/")

app.register_blueprint(view_winlog_module)
app.register_blueprint(view_a10log_module)

# sessionで使う暗号化キーの定義
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def index():
    winlog_uploads_files = glob.glob(glv.UPLOADS_DIR+"/winlog/*")
    a10log_uploads_files = glob.glob(glv.UPLOADS_DIR+"/a10log/*")

    return render_template('index.html', win_file_list=winlog_uploads_files, a10_file_list=a10log_uploads_files)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
