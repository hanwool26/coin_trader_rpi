from src.event import *
from src.coin import *
from src.util import *
import logging
import threading

HOUR = 60 * 60
MONITORING_INTERVAL = 10 # 10 sec

SELL_MARGIN = [1.02, 1.03, 1.04, 1.05] # 2% 3% 4% 6%
TIME_INTERVAL_UNIT = (4 * HOUR) // MONITORING_INTERVAL
MIN_TIME_INTERVAL = (4 * HOUR) // MONITORING_INTERVAL
MAX_TIME_INTERVAL = (48 * HOUR) // MONITORING_INTERVAL


# basis to judge rise or fall tendency
BASIS_JUDGE_TENDENCY = 3

class EventInfinite(Event, threading.Thread):
    def __init__(self, idx, account, socket, report, coin_name, balance, interval):
        threading.Thread.__init__(self)
        self.ev_id = idx
        self.account = account
        self.socket = socket
        # self.ui_control = main_window
        self.report = report
        self.coin_name = coin_name

        self.coin = Coin(self.coin_name)
        self.RATIO_BUY = 1/(PER_BUY*2)

        # Dynamic interval changes
        self.up_down_cnt = 0  # counter to check whether now is bull makret or bear market
        self.check_cur_price = self.check_last_price = 0  # for comparing between prev price and current price during INTERVAL

        self.interval = (interval * HOUR) // MONITORING_INTERVAL
        self.balance = balance
        self.buy_count = 0
        self.avg_price = 0
        self.total_amount = 0

        self.t_condition = threading.Condition()

        self.running = False
        self.threads = [
            threading.Thread(target=self.__trading, daemon=True),
            # threading.Thread(target=self.__show_info, daemon=True),
        ]

        self.sold_flag = False
        self.sold_price = 0
        self.trade_flag = False
        logging.info(f'{coin_name} : 무한 매수 event created!')

    def do_buy(self, price, amount):
        try:
            ret = self.account.buy(self.coin.ticker, price, amount)
            if ret == None:
                return False
            uuid = ret['uuid']

            for sec in range(TIME_OUT+1):
                if self.account.order_status(uuid) == 'done':
                    self.buy_count += 0.5
                    self.total_amount += amount
                    self.avg_price = get_avg_price(self.avg_price, price, self.buy_count)
                    return True
                time.sleep(1)
            self.account.cancel_order(uuid)
            return False
        except Exception as e:
            self.send_log(f"do buy : {ret['error']['message']}")
            self.buy_count += 1
            return False

    def init_trade(self):
        if self.balance <= 0:
            self.send_log('잔고 부족')
            return None
        each_asset = round(self.balance * self.RATIO_BUY, 2)
        self.send_log(f'분할 매수액 : {each_asset}')

        cur_price = self.check_last_price = self.coin.get_current_price()
        self.avg_price = cur_price = get_above_tick_price(cur_price)  # 호가 위 매수
        buying_amount = get_buying_amount(each_asset, cur_price, 1)
        if self.do_buy(cur_price, buying_amount) != True:
            self.close(False)
            return None
        # self.update_progress(PER_BUY, self.buy_count)
        # to do -> asset update
        # self.ui_control.show_asset_info()
        return each_asset

    def order_sell(self):
        # order sell
        # until progess / sell margin
        #        0-25%  /          6%
        #        5-50%  /          4%
        #       50-75%  /          3%
        #      75-100%  /          1%
        if self.buy_count > ((PER_BUY // 4) * 3) :
            selling_price = price_round(self.avg_price * SELL_MARGIN[0]) # sell margin 1%
        elif self.buy_count > ((PER_BUY // 4) * 2) :
            selling_price = price_round(self.avg_price * SELL_MARGIN[1]) # sell margin 3%
        elif self.buy_count > ((PER_BUY // 4) * 1) :
            selling_price = price_round(self.avg_price * SELL_MARGIN[2]) # sell margin 4%
        else:
            selling_price = price_round(self.avg_price * SELL_MARGIN[3]) # sell margin 6%
        ret = self.do_sell(self.coin.ticker, selling_price, self.total_amount)  # 매도
        return ret['uuid']

    def order_buy(self, buying_asset):
        # order buy
        ret = False
        cur_price = self.check_cur_price = self.coin.get_current_price()  # 현재 가격
        above_tick_price = get_above_tick_price(cur_price)  # 현재 가격보다 1호가 위 (바로 매수하기 위해)
        if self.buy_count > PER_BUY // 2:
            BUY_PERCENT = [1, 1]  # AVG_PRICE, AVG_PRICE
        else:
            BUY_PERCENT = [1, 1.04]  # AVG_PRICE, AVG_PRICE * 4%

        for percent in BUY_PERCENT:
            if cur_price <= (self.avg_price * percent):
                buying_amount = get_buying_amount(buying_asset, above_tick_price, 1)
                ret = self.do_buy(above_tick_price, buying_amount)
                self.send_log(f'매수 성공, 진행 : {self.buy_count}' if ret == True else f'매수 실패 : 타임아웃')
            else:
                self.send_log(f'매수 진행 불가 : 현재가 : {cur_price} > 매수 조건가 : {self.avg_price * percent}')

    def __check_sold_status(self, uuid):
        while self.trade_flag :
            if self.account.order_status(uuid) == 'done':
                self.trade_flag = False
                break
            time.sleep(10) # check order_status per 10 seconds

    def get_change_interval(self, prev_price, cur_price, interval):
        new_interval = interval

        if prev_price < cur_price:
            self.up_down_cnt = self.up_down_cnt + 1
        elif prev_price > cur_price:
            self.up_down_cnt = self.up_down_cnt - 1
        
        # continuosly fall price over 3 times, it jugdes to be into bear market
        if self.up_down_cnt == -BASIS_JUDGE_TENDENCY:
            self.up_down_cnt = 0
            if MAX_TIME_INTERVAL > (interval + TIME_INTERVAL_UNIT):
                new_interval = interval + TIME_INTERVAL_UNIT
            else :
                new_interval = MAX_TIME_INTERVAL

        # continuosly rise price over 3 times, it jugdes to be into bear market
        if self.up_down_cnt == BASIS_JUDGE_TENDENCY:
            self.up_down_cnt = 0
            if MIN_TIME_INTERVAL < (interval - TIME_INTERVAL_UNIT):
                new_interval = interval - TIME_INTERVAL_UNIT
            else :
                new_interval = MIN_TIME_INTERVAL

        if new_interval != interval :
            logging.info(f'{self.coin_name} : time interval changed from {(interval * MONITORING_INTERVAL)// HOUR} to {(new_interval * MONITORING_INTERVAL)// HOUR}')
        return new_interval

    def __trading(self):
        buying_asset = self.init_trade()
        if buying_asset == None:
            self.close(False)
            return

        while self.running and self.buy_count < PER_BUY:
            uuid = self.order_sell()
            # trade_interval = self.interval
            sell_status = False
            self.trade_flag = True

            sold_check_th = threading.Thread(target=self.__check_sold_status, daemon=True, args=(uuid, ))
            sold_check_th.start()

            for sec in range(0, self.interval): # wait and check flag during trade_interval
                if self.trade_flag == False:
                    sell_status = True
                    break
                else :
                    time.sleep(MONITORING_INTERVAL)

            self.trade_flag = False # kill the thread
            sold_check_th.join() # wait for complete exit of thread

            if sell_status == True :
                self.send_log('매도 성공')
                # save report in close() with flag True
                self.close(True)
            else:
                self.account.cancel_order(uuid)
                time.sleep(1)
                self.order_buy(buying_asset)
                # change time interval according to rise / fall of price
                self.interval = self.get_change_interval(self.check_last_price, self.check_cur_price, self.interval)
                self.check_last_price = self.check_cur_price

        if self.buy_count >= PER_BUY:
            logging.info(f'{self.coin_name} is going to endless selling')
            uuid = self.do_sell(self.coin.ticker, price_round(self.avg_price), self.total_amount) # 평단 본절
            while True: # 본절가에서 영혼법 지속.
                if self.account.order_status(uuid) == 'done':
                    self.close(True)
                    break
                time.sleep(HOUR)

    def reset_list(self):
        cur_price = self.coin.get_current_price()
        if self.sold_flag:
            cur_price = self.sold_price
        self.update_info(cur_price, self.avg_price, self.total_amount, get_increase_rate(cur_price, self.avg_price),
                         self.buy_count)

    def __show_info(self):
        while self.running:
            cur_price = self.coin.get_current_price()
            self.update_info(cur_price, self.avg_price, self.total_amount, get_increase_rate(cur_price, self.avg_price), self.buy_count)
            time.sleep(0.5)

    def close(self, sold_flag):
        self.send_log('무한 매수 종료')
        self.running = False
        if sold_flag == False:
            self.sold_price = self.avg_price = self.buy_count = self.total_amount = self.up_down_cnt = self.check_cur_price = self.check_last_price = 0
        elif sold_flag == True:
            self.sold_flag = True
            self.sold_price = self.coin.get_current_price()
            self.report.save_report(self.coin_name, self.sold_price, self.avg_price,
                                    self.total_amount, get_increase_rate(self.sold_price, self.avg_price), self.buy_count)
        with self.t_condition:
            self.t_condition.notifyAll()

    def close_thread(self):
        self.close(False)

    def run(self):
        if self.interval == None:
            return
        self.running = True
        self.sold_flag = False
        self.send_log(f'무한 매수 시작 : {self.coin.name}, Interval : {(self.interval * MONITORING_INTERVAL)// HOUR} 시간, 투자금액 : {self.balance} 원')
        for t in self.threads:
            t.start()

        with self.t_condition:
            self.t_condition.wait()

        logging.info('exit main thread of infinite trade')