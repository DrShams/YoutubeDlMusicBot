import os
import configparser

from rssparser import RSSParser
from vkposter import VKPoster


class Main:
    def __init__(self, config_file='config.conf'):
        self.rss_parser = RSSParser("https://www.votpusk.ru/newsrss/cn/newsEG.xml")#https://www.votpusk.ru/news.xml - ALL
        self.vk_poster = VKPoster()

        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.access_token = self.config.get('VKSettings', 'access_token')
        self.vk_owner_id = self.config.get('VKSettings', 'vk_owner_id')
        self.vk_version = self.config.get('VKSettings', 'vk_version')


    def run(self):
        # Fetch and parse the RSS feed
        self.rss_parser.fetch_rss_content()
        self.rss_parser.parse_rss()

        # Extract information from the latest news item
        filename = self.rss_parser.extract_information()

        # Save the extracted information to a JSON file
        self.rss_parser.save_to_json()

        # VK API credentials
        #access_token="vk1.a.iz-qPCHE3i5yCps4oXNmmllM0cL8VVkAtgRiD1LgtcyLtMjoQgdAy-EHgrnyxwur0BNwfAMGTWAsUMUsdGKTyB7cBX30fEpQmwXXvdion31JnOG8AQTqinFVhzFc8H8T0XqOEOMYJJwyP66YFxqmBkxj9YzqZfTZ3lM5FoogtjpBlhzLarM8WA0348A6ynPfAtllPFZxN0-4l-6gRsYSvg"
        #vk_owner_id = -50679937
        vk_from_group = 1
        #vk_version = "5.133"

        # Post the extracted information to VK wall
        self.vk_poster.post_to_vk_wall(self.access_token, self.vk_owner_id, vk_from_group, self.vk_version, self.rss_parser.extracted_info, filename)
        os.remove(filename)


if __name__ == "__main__":
    main = Main()
    main.run()
