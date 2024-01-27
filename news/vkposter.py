import configparser
import logging

import requests



class VKPoster:
    """ Class for posting data to the wall VK social media -> REST"""

    def __init__(self, config_file='config.conf'):
        """Initializes a VKPoster object. :param config_file: The path to the configuration file. """
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Accessing values from the configuration file
        self.token_for_photos = self.config.get('VKSettings', 'token_for_photos')
        self.version = self.config.get('VKSettings', 'version')
        self.user_albumid = self.config.get('VKSettings', 'user_albumid')
        self.myuser_id = self.config.get('VKSettings', 'myuser_id')

    def post_to_vk_wall(self, token, owner_id, version_vk, extracted_info):
        """
        Posts content to VK wall.

        :param token: Access token for VK.
        :param owner_id: Owner ID of the VK wall.
        :param version_vk: VK API version.
        :param extracted_info: Extracted information to be posted.
        """
        url = "https://api.vk.com/method/wall.post"

        # Extract title and description from extracted_info
        title = extracted_info.get('Title', '')
        description = extracted_info.get('Description', '')
        filename = extracted_info.get('ImageFileName', '')
        #:param from_group: Specifies whether the post should be from a group.
        from_group = 1

        # Combine title and description with a newline
        message = f"{title}\n\n{description}"

        photo_id = self.upload_photo_to_vk(self.token_for_photos, self.user_albumid, filename, self.version)
        photo = "photo" + self.myuser_id + "_" + str(photo_id)

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
            },
            timeout=60
        )

        logging.debug("Response Content: " + str(response.content))

        # Try to print response.json() if the content is valid JSON
        try:
            logging.debug(response.json())
            logging.info(f"Content successfully posted to vk wall with title {title}")
        except Exception as err:
            logging.error("Error parsing JSON:", err)

    def upload_photo_to_vk(self, token, album_id, photo_path, version):
        """Returns id photo after uploading image to the server"""
        upload_url = self.get_upload_url(token, album_id, version)

        with open(photo_path, 'rb') as file:
            photo_data = {'file1': file}

            upload_response = requests.post(upload_url, files=photo_data, timeout=60).json()
            logging.debug("upload_response " + str(upload_response))

        save_url = 'https://api.vk.com/method/photos.save'
        save_params = {
            'access_token': token,
            'album_id': upload_response['aid'],
            'server': upload_response['server'],
            'photos_list': upload_response['photos_list'],
            'hash': upload_response['hash'],
            'v': version,
        }

        save_response = requests.post(save_url, params=save_params, timeout=60).json()
        logging.debug("Save_response " + str(save_response))

        photo_id = save_response['response'][0]['id']
        logging.info(f"Photo was uploaded to the vk server's host and has an id {photo_id}")
        return photo_id

    def get_upload_url(self, token, album_id, version):
        """
        Retrieves the URL for uploading images.

        :param token: Access token for VK.
        :param album_id: ID of the VK album.
        :param version: VK API version.
        :return: URL for uploading photos.
        """
        url = 'https://api.vk.com/method/photos.getUploadServer'
        params = {
            'access_token': token,
            'album_id': album_id,
            'v': version
        }

        response = requests.get(url, params=params, timeout=60).json()
        url_server = response['response']['upload_url']
        logging.info(f"Url for uploading photos was recieved {url_server}")
        return url_server
