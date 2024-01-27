import os
import configparser


class Main:
    def __init__(self, config_file='config.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.access_token = self.config.get('VKSettings', 'access_token')
        self.vk_owner_id = self.config.get('VKSettings', 'vk_owner_id')
        self.vk_version = self.config.get('VKSettings', 'vk_version')


    def run(self):
        # Fetch and parse the RSS feed
        print("access_token " + self.access_token)
        print("vk_owner_id " + self.vk_owner_id)
        print("vk_version " + self.vk_version)


if __name__ == "__main__":
    main = Main()
    main.run()
