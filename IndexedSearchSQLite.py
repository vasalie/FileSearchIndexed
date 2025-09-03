
import os
import datetime
import sqlite3
import datetime
from time import time

from flask import Flask, request, render_template, g

PORT  = 5656 # Port to run the Flask app
DEBUG = True # Set to True to enable debug mode

MAX        = 10000

# Paths
PATH_APP = os.path.abspath(os.path.dirname(__file__))
PATH_DB  = os.path.join(PATH_APP, 'instance')
if not os.path.exists(PATH_DB):
    os.makedirs(PATH_DB)

class DatabaseManager:
    def __init__(self, db_path):
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def create_tbl_sql(self, table_sql):
        if self.conn is not None:
            try:
                cursor = self.cursor
                cursor.execute(table_sql)
            except sqlite3.Error as e:
                print(f"Error creating table: {e}")
        else:
            print("Database connection not established.")

    def search_records(self, table_name, columns, search_term, limit):
        try:

            set_clause = " OR ".join([f"{x} LIKE ?" for x in columns])
            query = f"SELECT * FROM {table_name} WHERE {set_clause} LIMIT {limit}"
            print(query)
            lst_search = [f"%{search_term}%" for _ in columns]
            self.cursor.execute(query, lst_search)
            rows = self.cursor.fetchall()
            count = len(rows)
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

# --------------------------------------------------------------------
# DB File_SIZE
DB_FILE       = "File_List.db"
DB_FILE_PATH  = os.path.join(PATH_DB, DB_FILE)
# -------------------------
# Table TestEng
TABLE_TESTENG_NAME = "List_Files_OpsFs"
TABLE_TESTENG_SQL  = f'''
                    CREATE TABLE IF NOT EXISTS {TABLE_TESTENG_NAME} (
                        id INTEGER PRIMARY KEY,
                        FILE_NAME    TEXT NOT NULL
                        FILE_PATH    TEXT NOT NULL
                    )
                    '''
TABLE_TESTENG = (DB_FILE_PATH, TABLE_TESTENG_NAME, TABLE_TESTENG_SQL)
# -------------------------

# Create DB and Tables
def create_db_tbl():
    db_manager = DatabaseManager(DB_FILE_PATH)
    db_manager.create_tbl_sql(TABLE_TESTENG_SQL)
    db_manager.close_conn()

def search_records(table, columns, search_term, limit):
    db_manager = DatabaseManager(table[0])
    rv = db_manager.search_records(table[1], columns, search_term, limit)
    db_manager.close_conn()
    return rv

app = Flask(__name__)

# Create DB and Tables
create_db_tbl()

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
        rv = search_records(TABLE_TESTENG, columns, request.form['search'], max)
        if rv[1] == max:
            count = MAX
        else:
            count = rv[1]
        return render_template('index.html', rows=rv[0], count=count, mess = request.form['search'], max=max, post = "true")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
