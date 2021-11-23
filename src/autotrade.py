import threading

class AutoTrade(threading.Thread):
    def __init__(self, n):
        self.trade_num = n
        self.running_coin = 0
        self.__running = False
        pass

    def close(self):
        self.__running = False

    def start(self):
        self.__running = True
        while self.__running:
            pass








