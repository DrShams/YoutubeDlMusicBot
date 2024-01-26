import requests
import json

token = 'vk1.a.wAdIGz8-l4N_TIuMcY5f-kYcpO6hHksPzIg8TcXsCiEjnbhgQLvm_R1DWiw9XZro9IwTr5kX1sAinNtL2yxc2_THMTZqmIVDMrldmGAF6qFDbHtLMPp6xbNvYqoMq0PpBw8_FXGU-F4Vrio8n6pNElMR0dhxRaX8jAP40MMGtVMMhFg31nYm1HYWiQksnq0Y'
version = '5.199'
alb = '299629472'
adres = 'abc.jpg'


def get_url():
    r = requests.get('https://api.vk.com/method/photos.getUploadServer',
        params={
            'access_token': token,
            'album_id': alb,
            'v': version
        }).json()
    return r['response']['upload_url']


url = get_url()

file = {'file1': open(adres, 'rb')}
ur = requests.post(url, files=file).json()
result = requests.get('https://api.vk.com/method/photos.save',
                        params={
                            'access_token': token,
                            'album_id': ur['aid'],
                            'server': ur['server'],
                            'photos_list': ur['photos_list'],
                            'hash': ur['hash'],
                            'v': version,
                        }).json()


