import sqlite3

def select():

    conn = sqlite3.connect('../data/golden-eye.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM xrates")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    conn.close()

if __name__ == '__main__':
    select()