import configparser

class Configurator:
    def __init__(self, config_file='config.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get_logging_level(self):
        return self.config.get('Logging', 'level', fallback='DEBUG')

    def get_file_path(self):
        return self.config.get('Logging', 'file_path', fallback='console.log')

    def get_date_format(self):
        return self.config.get('Logging', 'date_format')

    def get_news_age_limit_days(self):
        return int(self.config.get('NewsSettings', 'news_age_limit_days'))

    def get_vk_settings(self):
        return {
            'access_token': self.config.get('VKSettings', 'access_token'),
            'vk_owner_id': self.config.get('VKSettings', 'vk_owner_id'),
            'vk_version': self.config.get('VKSettings', 'vk_version'),
            'user_albumid': self.config.get('VKSettings', 'user_albumid'),
            'myuser_id': self.config.get('VKSettings', 'myuser_id'),
        }

    def get_section_links(self, section_name):
        section = self.config[section_name]
        return dict(section)