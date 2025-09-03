import os
import datetime
import datetime
from time import time
import pyodbc

from flask import Flask, request, render_template, g, redirect

PORT  = 5959 # Port to run the Flask app
DEBUG = True # Set to True to enable debug mode

MAX        = 100

TABLE = "Table_1"

class DatabaseManager:
    def __init__(self):
        try:
            self.conn = pyodbc.connect  (
                                            'DRIVER={ODBC Driver 17 for SQL Server};'  # Or another appropriate driver
                                            'SERVER=SDUMBRAV-LT;'
                                            'DATABASE=Test1;'
                                            # 'UID=your_username;'  # Omit for Trusted_Connection=yes
                                            # 'PWD=your_password'   # Omit for Trusted_Connection=yes
                                            'Trusted_Connection=yes;' # Use for Windows authentication
                                        )
            self.cursor = self.conn.cursor()
        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None

    def search_records(self, table_name, columns, search_term, limit):
        if self.conn == None:
            return [None, 0]
        try:

            conditions = []
            for col in columns:
                conditions.append(f"{col} LIKE ?")
            where_clause = " OR ".join(conditions)

            # Construct the full SQL query
            sql_query = f"SELECT TOP {limit} * FROM {table_name} WHERE {where_clause} "

            # Prepare parameters for the query (one for each column in the OR clause)
            params = [f"%{search_term}%"] * len(columns)

            self.cursor.execute(sql_query, params)
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
        columns =['Name']
        if   request.form['type'] == 'both':
            columns = ['Name', 'Path']
        elif request.form['type'] == 'files':
            columns = ['Name']
        elif request.form['type'] == 'folders':
            columns = ['Path']
        rv = search_records(TABLE, columns, request.form['search'], max)
        if rv[0] != None:
            if rv[1] == max:
                count = MAX
            else:
                count = rv[1]
            return render_template('index.html', rows=rv[0], count=count, mess = request.form['search'], max=max, post = "true")
        else:
            return '<h1  style="color: red;">Database is down</h1>'

@app.route('/test_search' , methods=['GET'])
def test_search():
    max = MAX
    # val_search = "END TIME"
    val_search = "END TIME"
    columns = ['Name', 'Path']
    rv = search_records(TABLE, columns, val_search, max)
    if rv[0] != None:
        if rv[1] == max:
            count = MAX
        else:
            count = rv[1]
        return render_template('index.html', rows=rv[0], count=count, mess = val_search, max=max, post = "true")
        # return redirect('/')
    else:
        warning = ""
        return '<h1  style="color: red;">Database is down</h1>'

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=PORT, debug=DEBUG)
