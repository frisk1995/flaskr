from flask import Flask, render_template, request, redirect, url_for, session
from controllers import control_winlog_db as cwd
from view import view_module
import sqlite3
app = Flask(__name__)

app.register_blueprint(view_module)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
