import youtube_dl

def downloadfile(url):
    """Function download files from Youtube and returns dictionary?"""
    options = {
        'format': 'bestaudio/best',
        'extractaudio' : True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }]
        #'max_filesize': 5000000#telegram will not allow to sent more than 50 megabytes files
    }
    ydl = youtube_dl.YoutubeDL(options)
    result = 'NONE'
    try:
        with ydl:#download
            result = ydl.extract_info(
                url,
                download = True
            )
    except:
        print("[Ошибочка] при скачивании" + url)
    return result