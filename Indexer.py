import os
import shutil
import sqlite3
import datetime

formatted_date = datetime.datetime.now().strftime("%Y_%m%d_%H%M")
print(formatted_date)

DB_FILE   = "File_List.db"
TABLE     = "List_Files_OpsFs"

source_path1 = r"\\opsfs\Shared"
val_len1 = len(source_path1)

source_path2 = r"\\opsfs\TestEng"
val_len2 = len(source_path2)

# DataBase connection
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create a table
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {TABLE} (
        id INTEGER PRIMARY KEY,
        FILE_NAME  TEXT NOT NULL,
        FILE_PATH  TEXT NOT NULL
    )
''')

# insert time and path in table at first row
cursor.execute(f'INSERT INTO {TABLE} (FILE_NAME, FILE_PATH) VALUES ("START TIME is:", "{formatted_date}")')
cursor.execute(f'INSERT INTO {TABLE} (FILE_NAME, FILE_PATH) VALUES ("PATH is:", "{source_path1}")')
cursor.execute(f'INSERT INTO {TABLE} (FILE_NAME, FILE_PATH) VALUES ("PATH is:", "{source_path2}")')
conn.commit()

# this is used to overwrite the print file line
empty_string = ""
length = 120
for i in range(length):
    empty_string += " "     # Appending a space

# search for files that match extension criteria
lst_files = []
val_incr = 0

print("\nPath is: " + source_path1 + "\n")
for root, dirs, files in os.walk(source_path1, topdown=True, onerror=None, followlinks=False):
    for name in files:
        val_incr = val_incr + 1
        file_path = os.path.join(root, name)
        lst_files.append(file_path)
        print(empty_string, end='\r')
        print(f"   {str(val_incr)} File: {str(name[0:80])}", end='\r')
        cursor.execute(f'INSERT INTO {TABLE} (FILE_NAME, FILE_PATH) VALUES ("{name}", "{root}")')
        # Commit each 1000 files
        if (val_incr % 10000 == 0):
            conn.commit()
print(empty_string, end='\r')
print()

print("\nPath is: " + source_path2 + "\n")
for root, dirs, files in os.walk(source_path2, topdown=True, onerror=None, followlinks=False):
    for name in files:
        val_incr = val_incr + 1
        file_path = os.path.join(root, name)
        lst_files.append(file_path)
        print(empty_string, end='\r')
        print(f"   {str(val_incr)} File: {str(name[0:80])}", end='\r')
        cursor.execute(f'INSERT INTO {TABLE} (FILE_NAME, FILE_PATH) VALUES ("{name}", "{root}")')
        # Commit each 1000 files
        if (val_incr % 10000 == 0):
            conn.commit()
print(empty_string, end='\r')
print()

# save time in last row of the table
formatted_date = datetime.datetime.now().strftime("%Y_%m%d_%H%M")
cursor.execute(f'INSERT INTO {TABLE} (FILE_NAME, FILE_PATH) VALUES ("END TIME is:", "{formatted_date}")')
conn.commit()

conn.close()

print(formatted_date)






