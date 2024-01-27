import requests
import json
import configparser
import logging

class VKPoster:
    def __init__(self, config_file='config.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Accessing values from the configuration file
        self.tokenForPhotos = self.config.get('VKSettings', 'tokenForPhotos')
        self.version = self.config.get('VKSettings', 'version')
        self.user_albumid = self.config.get('VKSettings', 'user_albumid')

        
    def post_to_vk_wall(self, token, owner_id, from_group, version_vk, extracted_info, filename):
        url = "https://api.vk.com/method/wall.post"

        # Extract title and description from extracted_info
        title = extracted_info.get('Title', '')
        description = extracted_info.get('Description', '')

        # Combine title and description with a newline
        message = f"{title}\n\n{description}"

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
        logging.debug("Response Content:", response.content)

        # Try to print response.json() if the content is valid JSON
        try:
            logging.debug(response.json())
            logging.info(f"Content successfully posted to vk wall with title {title}")
        except Exception as e:
            logging.error("Error parsing JSON:", e)

    def upload_photo_to_vk(self, token, album_id, photo_path, version):
        """Returns id photo after uploading image to the server"""
        upload_url = self.get_upload_url(token, album_id, version)
        photo_data = {'file1': open(photo_path, 'rb')}

        upload_response = requests.post(upload_url, files=photo_data).json()
        #logging.info("upload_response " + str(upload_response))

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
        #logging.info("save_response " + str(save_response))

        photo_id = save_response['response'][0]['id']
        logging.info(f"Photo was uploaded to the vk server's host and has an id {photo_id}")
        return photo_id

    def get_upload_url(self, token, album_id, version):
        """Returns URL where we can upload images"""
        url = 'https://api.vk.com/method/photos.getUploadServer'
        params = {
            'access_token': token,
            'album_id': album_id,
            'v': version
        }

        response = requests.get(url, params=params).json()
        urlServer = response['response']['upload_url']
        logging.info(f"Url for uploading photos was recieved {urlServer}")
        return urlServer