from flask import Flask, render_template, request, redirect, url_for, session
from view_winlog import view_winlog_module
from view_a10log import view_a10log_module
from controllers import control_winlog_db as cwd

import sqlite3
app = Flask(__name__)

app.register_blueprint(view_winlog_module)
app.register_blueprint(view_a10log_module)

# sessionで使う暗号化キーの定義
app.config['SECRET_KEY'] = 'secret_key'

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
