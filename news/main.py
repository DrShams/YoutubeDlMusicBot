import os
import configparser
import logging

from rssparser import RSSParser
from vkposter import VKPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Main:
    def __init__(self, config_file='config.conf'):
        #https://www.votpusk.ru/newsrss/cn/newsEG.xml
        self.rss_parser = RSSParser("https://www.votpusk.ru/news.xml")
        self.vk_poster = VKPoster()

        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.access_token = self.config.get('VKSettings', 'access_token')
        self.vk_owner_id = self.config.get('VKSettings', 'vk_owner_id')
        self.vk_version = self.config.get('VKSettings', 'vk_version')

    def run(self):
        self.rss_parser.fetch_rss_content()
        self.rss_parser.parse_rss()

        filename = self.rss_parser.extract_information()

        self.rss_parser.save_to_json()

        vk_from_group = 1
        self.vk_poster.post_to_vk_wall(self.access_token, self.vk_owner_id, vk_from_group, self.vk_version, self.rss_parser.extracted_info, filename)
        os.remove(filename)



if __name__ == "__main__":
    main = Main()
    main.run()
