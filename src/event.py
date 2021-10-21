import threading
import pyupbit
from src.util import *
from src.event_couple import *

STATUS_HEADER = 5 # columm number
TIME_OUT = 60
PER_BUY = 40 # divided by 40

class Event():
    def __init__(self):
        self.trade_lock = None
        self.account = None
        self.ui_control = None
        self.status = 'Ready' # 'Ready' , 'Monitoring', 'Bought', 'ready to sell', 'sold'
        self.ev_id = -1
        self.coin_name = ''

    def do_buy(self, ticker, amount):
        current_price = pyupbit.get_current_price(ticker)
        ret = self.account.buy(ticker, current_price, amount) # 현재가 윗호가 매수
        return ret

    def do_sell(self, ticker, price, amount):
        try:
            ret = self.account.sell(ticker, price, amount)
            print(f'do sell : {ticker}, {price}, {amount}')
        except Exception as e:
            print(e)
        return ret

    def get_status(self):
        return self.status

    def update_info(self, price, avg_price, amount, profit_rate, count):
        invest_asset = round(avg_price * amount, 2)
        info = [f'{self.coin_name}', f'{price}원', f'{avg_price}원', f'{invest_asset}원', f'{round((invest_asset * profit_rate)/100, 2)}원',
               f'{profit_rate} %', f'{count}/{PER_BUY}']
        self.ui_control.infinite_item_update(self.ev_id, info)
            # self.ui_control.update_info(info)

    def update_status(self, status):
        self.status = status
        if self.ui_control == None:
            print('ui control is none')
        else:
            self.ui_control.couple_item_update(self.ev_id, STATUS_HEADER, status)

    def update_progress(self, max, count):
        if self.ui_control == None:
            print('ui control is none')
        else:
            self.ui_control.update_progress(max, count)


