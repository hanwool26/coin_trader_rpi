import threading
import time
import src.util as util
import pyupbit
import logging
from src.event import *
from src.coin import *

INTERVAL = 5 * TIME_OUT # per minutes

class EventCouple(Event):
    BUYING_AMOUNT = { # show chain cohesion
        'welldone' : 1,
        'medium': 0.5,
        'rare': 0.2,
    }
    TARGET_PROFIT = {
        'welldone': 10,
        'medium' : 5,
        'rare' : 1,
    }
    def __init__(self, idx, account, main_window, primary_c_name, chain_c_name, cohesion):
        # super
        self.ev_id = idx
        self.account = account
        self.trade_lock = threading.Condition()
        self.ui_control = main_window

        # mine
        self.primary_coin = Coin(primary_c_name)
        self.chain_coin = Coin(chain_c_name)
        self.cohesion = self.BUYING_AMOUNT[cohesion]
        self.target_per = self.TARGET_PROFIT[cohesion]
        # self.wait_time = 5 # secs

        self.__running = False
        self.update_status('ready')

    def do_trade(self, ticker, buying_price, target):

        my_balance = self.account.get_balance()
        amount = util.get_buying_amount(my_balance, buying_price, self.cohesion)
        # -> Exception happens when price of chain is bigger than balance.
        if my_balance <= 0:
            logging.getLogger('LOG').info(f'not enough balance')
            return -1
        logging.getLogger('LOG').info(f'ready to buy')

        ret = self.account.buy(ticker, buying_price, amount)
        uuid = ret['uuid']

        for sec in range(1, TIME_OUT+1):
            if sec == TIME_OUT:
                logging.getLogger('LOG').info(f'cancel order to buy {ticker}')
                self.account.cancel_order(uuid)
                return -1
            if self.account.order_status(uuid) == 'done':
                break
            time.sleep(1)

        self.update_status('bought')
        logging.getLogger('LOG').info(f'bought (coin : {ticker}, price : {buying_price}, amount : {amount}')
        ret = self.selling_target(ticker, buying_price, amount, target)
        return ret

    def selling_target(self, ticker, buying_price, amount, target):
        logging.getLogger('LOG').info(f'ready to sell {ticker} for {target}%')
        self.update_status('ready to sell')
        sell_flag = False
        while sell_flag != True and self.__running:
            current_price = self.chain_coin.get_current_price()
            increase_rate =  util.get_increase_rate(current_price, buying_price)
            if increase_rate > target or increase_rate < -target:
                ret = self.account.sell(ticker, current_price, amount)
                uuid = ret['uuid']
                for sec in range(1, TIME_OUT+1):
                    if sec == TIME_OUT:
                        self.account.cancel_order(uuid)

                    if self.account.order_status(uuid) == 'done':
                        logging.getLogger('LOG').info(f'selling {ticker} with {increase_rate}%')
                        self.update_status('complete to sold')
                        sell_flag = True
                        break
                    time.sleep(1)

        return 0 if increase_rate > 0 else -1 # selling for plus return 0, selling for minus return -1

    def __monitoring(self):
        logging.getLogger('LOG').info(f'모니터링 시작 : {self.primary_coin.name} - {self.chain_coin.name}')
        primary_base_price = self.primary_coin.get_current_price()
        chain_base_price = self.chain_coin.get_current_price()

        while self.__running:
            try:
                primary_current_price = self.primary_coin.get_current_price()
                chain_current_price = self.chain_coin.get_current_price()
                if (util.get_increase_rate(primary_current_price, primary_base_price)) >= self.target_per:
                    logging.getLogger('LOG').info('Primary coin begins to pump up with 1%')
                    if util.get_increase_rate(chain_current_price, chain_base_price) < self.target_per:
                        logging.getLogger('LOG').info('ready to buy chain coin')
                        self.do_trade(self.chain_coin.ticker, self.chain_coin.get_current_price(), self.target_per)
                    else:
                        logging.getLogger('LOG').info('chain coin already has pumped up')
                # wait interval
                int_val = 0
                while int_val < INTERVAL and self.__running:
                    int_val +=1
                    time.sleep(1)

                primary_base_price = self.primary_coin.get_current_price()
                chain_base_price = self.chain_coin.get_current_price()
            except Exception as e:
                logging.getLogger('LOG').error(e)

        logging.getLogger('LOG').info(f'모니터링 종료 : {self.primary_coin.name} - {self.chain_coin.name}')

    def close_thread(self):
        self.update_status('ready')
        self.__running = False

    def start(self) -> None:
        self.update_status('monitoring')
        self.__running = True
        t = threading.Thread(target=self.__monitoring, args=())
        t.start()




