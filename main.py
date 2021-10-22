import logging

from src.account import *
from src.config import *
from src.manager import *
from src.load_file import *
from main_window import *
import sys
from PyQt5.QtWidgets import *
from src.util import *
import qdarkstyle

# COUPLE_FILE_PATH =

# coin_name, balance, interval, repeat
TEST_JSON = {'coin_name': '리플',
             'balance': 100000,
             'interval': 6,
             'repeat': False}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    config = Config()
    config.load_config()
    access_key, secret_key = config.get_api_key()
    my_account = Account(access_key, secret_key)
    my_account.connect_account()

    # load UI items from file and set the list on listView
    # mywindow.set_table_data(couple_list)

    manager = Manager(my_account)
    manager.do_start(None, 'infinite', TEST_JSON)


