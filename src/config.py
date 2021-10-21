import configparser
import os
from src.util import DATA_PATH

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.secret_key = ""
        self.access_key = ""
        self.CONFIG_PATH = os.path.join(DATA_PATH, '../data/config.ini')


    def load_config(self):
        self.config.read(self.CONFIG_PATH, encoding='utf-8')
        self.access_key = self.config['api_key']['access_key']
        self.secret_key = self.config['api_key']['secret_key']

    def get_api_key(self):
        if len(self.access_key)!=0 and len(self.secret_key)!=0:
            return self.access_key, self.secret_key
