from pytube import Playlist
import os
import sqlite3
path = os.path.abspath("files/")
os.environ["PATH"] += os.pathsep + path

conn = sqlite3.connect('files/db.sqlite',check_same_thread=False)
cur = conn.cursor()
cur.executescript('''
    CREATE TABLE IF NOT EXISTS "Users" (
	"id" INTEGER,
	"user_name" TEXT,
	"utime_checked"	INTEGER);

    CREATE TABLE IF NOT EXISTS "Playlist" (
    "id" INTEGER,
	"user_id" INTEGER,
    "url" TEXT,
    "status" INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT));

    CREATE TABLE IF NOT EXISTS "Userplaylist" (
	"id" INTEGER,
    "user_id" INTEGER,
	"user_name"	TEXT,
	"utime_checked"	INTEGER),
    PRIMARY KEY("id" AUTOINCREMENT));'''
)


link = Playlist('https://www.youtube.com/playlist?list=PLFaKDBYWwxzTht5OKenNoWWWkMfmAh5NV')
os.chdir('files')
for url in link.video_urls:
    print(url)
    cur.execute('SELECT id FROM Playlist WHERE url = ?',(url,))
    row = cur.fetchone()
    conn.commit()
    if row is None:
        os.system('youtube-dl -x --extract-audio --audio-format mp3 --output %(uploader)s%(title)s.%(ext)s ' + url)
        cur.execute('INSERT INTO Playlist (url, status) VALUES (?, ?)',(url, 0))#update status 1 when it will be deployed
        conn.commit()
    else:
        id = row[0]
        print(url, "is already in the database with id=",id)
