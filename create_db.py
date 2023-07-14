from sqlite3 import connect

with connect('database.db') as connection:
        cur = connection.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS "game" (
        "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
        "A1" NULL,
        "A2" NULL,
        "A3" NULL,
        "B1" NULL,
        "B2" NULL,
        "B3" NULL,
        "C1" NULL,
        "C2" NULL,
        "C3" NULL
        );''')
        connection.commit()
