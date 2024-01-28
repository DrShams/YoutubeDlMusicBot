import os
import configparser
import logging
import random

from rssparser import RSSParser
from vkposter import VKPoster

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a file handler and set the logging level
file_handler = logging.FileHandler('server.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Create a formatter for the file handler
file_formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_formatter)

# Get the root logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)

class Main:
    def __init__(self, config_file='config.conf'):
        """Read Config File"""
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        #Read Random News
        random_travel_link = self.get_random_link("TravelLinks", self.config)
        logging.info("Random Travel Link:" + str(random_travel_link))

        self.rss_parser = RSSParser(random_travel_link)
        self.vk_poster = VKPoster()

        self.access_token = self.config.get('VKSettings', 'access_token')
        self.vk_owner_id = self.config.get('VKSettings', 'vk_owner_id')
        self.vk_version = self.config.get('VKSettings', 'vk_version')

    def run(self):
        self.rss_parser.fetch_rss_content()
        self.rss_parser.parse_rss()

        data = self.rss_parser.extract_information()
        self.rss_parser.save_to_json()

        self.vk_poster.post_to_vk_wall(self.access_token, self.vk_owner_id, self.vk_version, self.rss_parser.extracted_info)

        filename = data['ImageFileName']
        os.remove(filename)

    def get_random_link(self, section_name, config):
        links = dict(config.items(section_name))
        return random.choice(list(links.values()))    



if __name__ == "__main__":
    main = Main()
    main.run()
