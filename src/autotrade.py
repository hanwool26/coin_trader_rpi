import threading
import logging
import time
from src.manager import *
from src.util import *

HOUR = 60*60
RSI_STD = 60 # RSI Standard
TRADE_INTERVAL = 24

class AutoTrade(threading.Thread):
    def __init__(self, manager, trade_num):
        threading.Thread.__init__(self)
        self.trade_num = trade_num
        self.running_coin = 0
        self.__running = False
        self.manager = manager
        self.trade = 'infinite'
        self.threads = [
            threading.Thread(target=self.__auto_trading, daemon=True),
        ]

    def check_running(self):
        delete_idx = list()

        for idx in range(self.manager.infinite_idx):
            if self.manager.infinite_event[idx].running == False:
                delete_idx.append(idx)

        if delete_idx != None:
            delete_idx.reverse()
            self.manager.do_stop(delete_idx, self.trade)

        return self.manager.infinite_idx

    def buy_coin(self, buying_coin_num):
        invest_asset = self.manager.account.get_balance() * 0.98 # reason that multiply 0.95 is to make enough space of investing asset.
        each_asset = round( (invest_asset / buying_coin_num), 2)
        logging.info(f'buy coin - total asset : {invest_asset}, each_asset : {each_asset}, coin_number : {buying_coin_num}')
        coin_list = get_sort_rsi_by_vol()
        idx = 0
        coin_info = {
            'balance': each_asset,
            'interval': TRADE_INTERVAL,
            'repeat': False,
        }

        while True:
            flag = True
            coin_name = coin_list[idx][0]
            coin_RSI = coin_list[idx][1]
            if coin_RSI > RSI_STD:
                logging.info(f'RSI is over the RSI Standard({RSI_STD})')
                break
            for event in self.manager.infinite_event:
                if coin_name == event.coin_name:
                    flag = False
                    break
            if flag == True:
                logging.info(f'buy coin : {coin_name}, RSI : {coin_RSI}')
                coin_info.update({'coin_name': coin_name})
                self.manager.do_start(None, self.trade, coin_info)
                time.sleep(1)

            idx += 1
            if self.trade_num == self.manager.infinite_idx:
                break

    def close(self):
        self.__running = False
        idx_list = [idx for idx in range(self.manager.infinite_idx - 1, -1, -1)]
        self.manager.do_stop(idx_list, self.trade)

    def __auto_trading(self):
        while self.__running:
            self.running_coin = self.check_running()
            need_coin = self.trade_num - self.running_coin
            logging.info(f'?????? ????????? ?????? ??? : {need_coin}')

            if need_coin > 0:
                self.buy_coin(need_coin)
            time.sleep(HOUR)

        if self.check_running() == 0:
            logging.info(f'auto trading exit')

    def run(self) -> None:
        self.__running = True
        for t in self.threads:
            t.start()
