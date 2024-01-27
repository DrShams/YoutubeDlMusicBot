import requests
import json
import configparser

class VKPoster:
    def __init__(self, config_file='config.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Accessing values from the configuration file
        self.tokenForPhotos = self.config.get('VKSettings', 'tokenForPhotos')
        self.version = self.config.get('VKSettings', 'version')
        self.user_albumid = self.config.get('VKSettings', 'user_albumid')

        
    def post_to_vk_wall(self, token, owner_id, from_group, version_vk, extracted_info, filename):
        """Этот метод постит запись непосредственно в группу в вк"""
        url = "https://api.vk.com/method/wall.post"

        # Extract title and description from extracted_info
        title = extracted_info.get('Title', '')
        description = extracted_info.get('Description', '')

        # Combine title and description with a newline
        message = f"{title}\n\n{description}"
        
        #tokenForPhotos = 'vk1.a.Tf9QOGbAMwb5yRzD2FJG0ohC4ZybRogBsAu4ZZTpYxfid8Q7QVy5PcVzqHFJ322MnbGpLvZNlJNC3xOEPSCh8mUv4eF_JHvLAml6z6ZCN7l3r1oNBab_hWjfablr2ZLO7iZa2aNDKPR5G9K1B45Uvmdj4VAn3RAkcrRNGViNfvmfDIpzhxpe0UDrTg8HdYBoEZExndMac_D82bqLS7PA2w'
        #version = '5.199'
        #user_albumid = '299629472'

        photo_id = self.upload_photo_to_vk(self.tokenForPhotos, self.user_albumid, filename, self.version)
        photo = "photo151028064_" + str(photo_id)

        response = requests.post(
            url=url,
            params={
                'access_token': token,
                'from_group': from_group,
                'owner_id': owner_id,
                'attachments': photo,
                'v': version_vk
            },
            data={
                'message': message
            }
        )

        # Print the response content for debugging
        print("Response Content:", response.content)

        # Try to print response.json() if the content is valid JSON
        try:
            print(response.json())
            print(f"[log]Content successfully posted to vk wall with title {title}")
        except Exception as e:
            print("Error parsing JSON:", e)

    def upload_photo_to_vk(self, token, alb, adres, version):
        """Этот метод возвращает ид фото после заливки на сервер"""
        upload_url = self.get_upload_url(token, alb, version)
        #print("upload_url " + upload_url)
        photo_data = {'file1': open(adres, 'rb')}

        upload_response = requests.post(upload_url, files=photo_data).json()
        #print("upload_response " + str(upload_response))

        save_url = 'https://api.vk.com/method/photos.save'
        save_params = {
            'access_token': token,
            'album_id': upload_response['aid'],
            'server': upload_response['server'],
            'photos_list': upload_response['photos_list'],
            'hash': upload_response['hash'],
            'v': version,
        }

        save_response = requests.post(save_url, params=save_params).json()
        #print("save_response " + str(save_response))

        # Extract and return the 'id' from the response
        photo_id = save_response['response'][0]['id']
        print(f"[log]Photo was uploaded to the vk server's host and has an id {photo_id}")
        return photo_id

    def get_upload_url(self, token, alb, version):
        """Этот метод получает урл куда можно заливать фотографию"""
        url = 'https://api.vk.com/method/photos.getUploadServer'
        params = {
            'access_token': token,
            'album_id': alb,
            'v': version
        }

        response = requests.get(url, params=params).json()
        urlServer = response['response']['upload_url']
        print(f"[log]Url for uploading photos was recieved {urlServer}")
        return urlServer