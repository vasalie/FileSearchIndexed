
import os
import datetime
import datetime
from time import time
import psycopg2

from flask import Flask, request, render_template, g, redirect

PORT  = 5858 # Port to run the Flask app
DEBUG = True # Set to True to enable debug mode

MAX        = 10000

HOST  ="127.0.0.1"
USER  ="lv"
PASS  ="lv"
DB    ="db_test"
TABLE = "tbl_serial"

class DatabaseManager:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                            host     = HOST,
                            user     = USER,
                            password = PASS,
                            database = DB
                        )
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def search_records(self, table_name, columns, search_term, limit):
        if self.conn == None:
            return [None, 0]
        try:

            set_clause = " OR ".join([f"{x} ILIKE %s" for x in columns])
            query = f"SELECT * FROM {table_name} WHERE {set_clause} LIMIT {limit}"
            lst_search = [f"%{search_term}%" for _ in columns]
            # query = f"SELECT * FROM list_files_opsfs WHERE name LIKE '%{search_term}%' LIMIT {limit};"
            # print(query)
            # print(lst_search)
            self.cursor.execute(query, lst_search)
            # self.cursor.execute(query)
            rows = self.cursor.fetchall()
            if rows:
                count = len(rows)
            else:
                count = 0
            # print(count)
            return rows, count

        except Exception as e:
            print(f"Error executing query: {e}")
            return [None, 0]

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
        return render_template('index.html', post = "false")
    else:
        columns =['name']
        if   request.form['type'] == 'both':
            columns = ['name', 'path']
        elif request.form['type'] == 'files':
            columns = ['name']
        elif request.form['type'] == 'folders':
            columns = ['path']
        rv = search_records(TABLE, columns, request.form['search'], max)
        if rv[0] != None:
            if rv[1] == max:
                count = MAX
            else:
                count = rv[1]
            return render_template('index.html', rows=rv[0], count=count, mess = request.form['search'], max=max, post = "true")
        else:
            return redirect('/')

@app.route('/test_search' , methods=['GET'])
def test_search():
    max = MAX
    # val_search = "END TIME"
    val_search = "END TIME"
    columns = ['name', 'path']
    rv = search_records(TABLE, columns, val_search, max)
    if rv[0] != None:
        if rv[1] == max:
            count = MAX
        else:
            count = rv[1]
        return render_template('index.html', rows=rv[0], count=count, mess = val_search, max=max, post = "true")
        # return redirect('/')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=PORT, debug=DEBUG)
