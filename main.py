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

if __name__ == '__main__':
    app = QApplication(sys.argv)

    files = LoadFile('couple_coin_list.xlsx')
    couple_list = files.get_couple_list()

    mywindow = MainWindow(couple_list)
    mywindow.setWindowTitle('DreamCoin')
    mywindow.set_infinite_table()

    config = Config()
    config.load_config()
    access_key, secret_key = config.get_api_key()
    my_account = Account(access_key, secret_key)
    my_account.connect_account()

    # load UI items from file and set the list on listView
    # mywindow.set_table_data(couple_list)
    mywindow.set_coin_combobox(get_coin_list())
    mywindow.set_interval_combobox()

    manager = Manager(my_account, mywindow, couple_list)
    mywindow.set_manager_handler(manager)

    mywindow.set_asset_rate_combobox()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mywindow.show()
    app.exec_()

