import threading
import logging
import time
from src.manager import *
from src.util import *

HOUR = 60*60

class AutoTrade(threading.Thread):
    def __init__(self, manager, trade_num):
        self.trade_num = trade_num
        self.running_coin = 0
        self.__running = False
        self.manager = manager
        self.trade = 'infinite'
        pass

    def check_running(self):
        closing = 0
        delete_idx = list()
        if self.infinite_event == None:
            return closing

        for idx in range(self.manager.infinite_idx):
            if self.manager.infinite_event[idx].__running == False:
                delete_idx.append(idx)
                closing += 1

        for idx in reversed(delete_idx):
            self.manager.do_stop(idx, self.trade)
            time.sleep(3)

        return self.trade_num - closing

    def buy_coin(self, buying_coin_num):
        invest_asset = self.manager.account.get_balance() * 0.95 # reason that multiply 0.95 is to make enough space of investing asset.
        each_asset = round( (invest_asset / buying_coin_num), 2)
        logging.info(f'buy coin - total asset : {invest_asset}, each_asset : {each_asset}, coin_number : {buying_coin_num}')
        coin_list = get_sort_rsi_by_vol()
        idx = 0
        coin_info = {
            'balance': each_asset,
            'interval': 12,
            'repeat': False,
        }

        while True:
            flag = True
            coin_name = coin_list[idx][0]
            for event in self.manager.infinite_event:
                if coin_name == event.coin_name:
                    flag = False
                    break
            if flag == True:
                logging.info(f'buy coin : {coin_name}')
                coin_info.update({'coin_name': coin_name})
                self.manager.do_start(None, self.trade, coin_info)

            idx += 1
            if self.trade_num == self.manager.infinite_idx:
                break

    def close(self):
        self.__running = False
        for idx in range(self.manager.infinite_idx, 0, -1):
            self.manager.do_stop(idx, self.trade)

    def start(self):
        self.__running = True
        while self.__running:
            self.running_coin = self.check_running()
            need_coin = self.trade_num - self.running_coin
            logging.info(f'매수 필요한 코인 수 : {need_coin}')
            if need_coin == 0: # init
                continue
            elif need_coin > 0:
                self.buy_coin(need_coin)

            time.sleep(HOUR)
