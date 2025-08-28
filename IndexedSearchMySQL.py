
import os
import datetime
import sqlite3
import datetime
from time import time
import mysql.connector

from flask import Flask, request, render_template, g

PORT  = 5757 # Port to run the Flask app
DEBUG = True # Set to True to enable debug mode

MAX        = 10000

HOST  ="127.0.0.1"
USER  ="lv"
PASS  ="123456"
DB    ="db_test"
TABLE = "list_files_opsfs"

class DatabaseManager:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                            host     = HOST,
                            user     = USER,
                            password = PASS,
                            database = DB
                        )
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def search_records(self, table_name, columns, search_term, limit):
        try:

            set_clause = " OR ".join([f"{x} LIKE %s" for x in columns])
            query = f"SELECT * FROM {table_name} WHERE {set_clause} LIMIT {limit}"
            lst_search = [f"%{search_term}%" for _ in columns]
            # query = f"SELECT * FROM list_files_opsfs WHERE FILE_NAME LIKE '%{search_term}%' LIMIT {limit};"
            print(query)
            print(lst_search)
            self.cursor.execute(query, lst_search)
            # self.cursor.execute(query)
            rows = self.cursor.fetchall()
            count = len(rows)
            print(count)
            return rows, count

        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def close_conn(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()

def timestamp():
    return datetime.datetime.now().strftime("%Y_%m%d_%H%M_%S")


def search_records(table, columns, search_term, limit):
    db_manager = DatabaseManager()
    rv = db_manager.search_records(table, columns, search_term, limit)
    db_manager.close_conn()
    return rv

app = Flask(__name__)

@app.before_request
def before_request_func():
    g.request_start_time = time()

@app.after_request
def after_request_func(response):
    time_val     = str(datetime.datetime.now().strftime("%Y-%m-%d*%H:%M:%S"))
    duration_val = str(time() - g.request_start_time)[:5]
    path_val     = str(request.path)
    val_log = time_val + ' --- ' + duration_val + ' --- ' + path_val
    print("--------------------")
    print(val_log)
    print("--------------------")
    return response

@app.route('/' , methods=['GET','POST'])
def index():
    max = MAX
    if request.method == 'GET':
        return render_template('index.html', post = "flase")
    else:
        columns =['FILE_NAME']
        if   request.form['type'] == 'both':
            columns = ['FILE_NAME', 'FILE_PATH']
        elif request.form['type'] == 'files':
            columns = ['FILE_NAME']
        elif request.form['type'] == 'folders':
            columns = ['FILE_PATH']
        rv = search_records(TABLE, columns, request.form['search'], max)
        if rv[1] == max:
            count = MAX
        else:
            count = rv[1]
        return render_template('index.html', rows=rv[0], count=count, mess = request.form['search'], max=max, post = "true")

@app.route('/test_search' , methods=['GET'])
def test_search():
    max = MAX
    val_search = "END TIME"
    columns = ['FILE_NAME', 'FILE_PATH']
    rv = search_records(TABLE, columns, val_search, max)
    if rv[1] == max:
        count = MAX
    else:
        count = rv[1]
    return render_template('index.html', rows=rv[0], count=count, mess = val_search, max=max, post = "true")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
