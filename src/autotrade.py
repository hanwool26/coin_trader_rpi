import threading
from src.manager import *

class AutoTrade(threading.Thread):
    def __init__(self, manager, trade_num):
        self.trade_num = trade_num
        self.running_coin = 0
        self.__running = False
        self.manager = manager
        pass

    def check_running(self):
        closing = 0
        if self.infinite_event == None:
            return closing

        for idx in range(self.trade_num):
            if self.manager.infinite_event[idx].__running == False:
                self.manager.do_stop(idx, 'infinite')
                closing += 1

        return self.trade_num - closing

    def close(self):
        self.__running = False

    def start(self):
        self.__running = True
        while self.__running:
            running_num = self.check_running()
            if running_num < self.trade_num:

            pass








