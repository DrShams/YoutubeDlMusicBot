import sqlite3

def makedb():
    """Create Database if not exists"""

    global conn
    global cur

    conn = sqlite3.connect('files/db.sqlite',check_same_thread=False)
    cur = conn.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS "Users" (
        	"id" INTEGER,
        	"user_name" TEXT,
        	"playlist_url"	TEXT);

        CREATE TABLE IF NOT EXISTS "Playlist" (
            "id" INTEGER,
        	"user_id" INTEGER,
            "url" TEXT,
            "status" INTEGER,
        PRIMARY KEY("id" AUTOINCREMENT));
        '''
    )