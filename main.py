import logging

from src.account import *
from src.config import *
from src.manager import *
import sys
from src.util import *
from src.socket_server import *

# COUPLE_FILE_PATH =

# coin_name, balance, interval, repeat
TEST_JSON = {'coin_name': '리플',
             'balance': 220000,
             'interval': 1,
             'repeat': False}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='[%(asctime)s] %(message)s')
    # load UI items from file and set the list on listView
    # mywindow.set_table_data(couple_list)

    socket = Socket_Server(9999)
    manager = Manager(socket)
    socket.setManager(manager)
    while True:
        socket.wait_for_connection()
    # manager.do_start(None, 'infinite', TEST_JSON)


