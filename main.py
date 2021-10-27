import logging
from src.manager import *
import sys
from src.socket_server import *

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='[%(asctime)s] %(message)s')
    # load UI items from file and set the list on listView
    # mywindow.set_table_data(couple_list)

    socket = Socket_Server(9999)
    manager = Manager(socket)
    socket.setManager(manager)
    while True:
        socket.wait_for_connection()


