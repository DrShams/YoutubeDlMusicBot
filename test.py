options = {
    'format': 'bestaudio/best',
    'extractaudio' : True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

print(options['postprocessors'][0]['preferredcodec'])
