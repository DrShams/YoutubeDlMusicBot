from pytube import Playlist
import os
import sqlite3
import youtube_dl
import re


STATUS_CODE_JUST_DOWNLOADED = 0
path = os.path.abspath("files/")
os.environ["PATH"] += os.pathsep + path
conn = sqlite3.connect('files/db.sqlite',check_same_thread=False)
cur = conn.cursor()

def makedb():
    """Create Database if not exists"""

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

def download():
    """Download all files in mp3 format from youtube by defined link"""

    link = Playlist('https://www.youtube.com/playlist?list=PLFaKDBYWwxzTht5OKenNoWWWkMfmAh5NV')
    os.chdir('files')

    options = {
        'format': 'bestaudio/best',
        'extractaudio' : True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    }

    ydl = youtube_dl.YoutubeDL(options)
    for url in link.video_urls:
        print(url)

        cur.execute('SELECT id FROM Playlist WHERE url = ?',(url,))
        row = cur.fetchone()
        conn.commit()
        if row is None:
            with ydl:#GOOGLE
                result = ydl.extract_info(
                    url,
                    download = True
                )
            if 'entries' in result:
                # Can be a playlist or a list of videos
                video = result['entries'][0]
            else:
                # Just a video
                video = result
            video_title = video['title']

            pattern = '=([\w]*)'
            m = re.search(pattern,url)

            filename = video_title + '-' + m.group(1)
            print(filename)

            cur.execute('INSERT INTO Playlist (url, status) VALUES (?, ?)',(url, STATUS_CODE_JUST_DOWNLOADED))#update status 1 when it will be deployed
            conn.commit()
        else:
            id = row[0]
            #print(url, "is already in the database with id=",id)

if __name__ == "__main__":
    makedb()
    download()
