import pyupbit
import logging

class Account():
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.upbit = None

    def get_asset(self) -> int:
        asset = self.get_balance() + self.get_locked()
        logging.getLogger('LOG').info(f'asset : {asset} 원')
        return asset

    def get_balance(self) -> int:
        my_info = self.upbit.get_balances()[0]
        balance = (int(my_info['balance'].split('.')[0]))
        logging.getLogger('LOG').info(f"balance : {balance} 원")
        return balance

    def get_locked(self) -> int:
        my_info = self.upbit.get_balances()[0]
        locked = (int(my_info['locked'].split('.')[0]))
        logging.getLogger('LOG').info(f'locked : {locked} 원')
        return locked

    def buy(self, ticker, price, amount):
        if self.get_balance() < 0:
            ret = -1
            raise Exception('no enough blanace')
        else :
            ret = self.upbit.buy_limit_order(ticker, price, amount)
            logging.getLogger('LOG').info(f'success to buy {amount} of {ticker} at {price}')
        return ret

    def sell(self, ticker, price, amount):
        ret = self.upbit.sell_limit_order(ticker, price, amount)
        return ret

    def cancel_order(self, uuid):
        ret = self.upbit.cancel_order(uuid)
        print(ret)
        return ret

    def order_status(self, uuid):
        return self.upbit.get_order(uuid)['state']

    def connect_account(self):
        try:
            self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)
        except Exception as e:
            logging.getLogger('LOG').info(e)

        if self.upbit != None:
            logging.getLogger('LOG').info('Success to access my account')