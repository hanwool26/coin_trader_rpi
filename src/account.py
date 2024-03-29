import pyupbit
import logging

class Account():
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.upbit = None

    def get_asset(self) -> int:
        try:
            asset = self.get_balance() + self.get_locked()
            logging.info(f'asset : {asset} 원')
        except Exception as e:
            logging.info('account.get_asset()')
            logging.error(e)
        return asset

    def get_balance(self) -> int:
        try:
            my_info = self.upbit.get_balances()[0]
            balance = (int(my_info['balance'].split('.')[0]))
            logging.info(f"balance : {balance} 원")
        except Exception as e:
            logging.error(e)
        return balance

    def get_locked(self) -> int:
        try:
            my_info = self.upbit.get_balances()[0]
            locked = (int(my_info['locked'].split('.')[0]))
            logging.info(f'locked : {locked} 원')
        except Exception as e:
            logging.error(e)
        return locked

    def buy(self, ticker, price, amount):
        if self.get_balance() < 0:
            ret = -1
            raise Exception('no enough blanace')
        else :
            ret = self.upbit.buy_limit_order(ticker, price, amount)
            if ret != None:
                logging.info(f'success to buy {ticker}, price : {price}, amount : {amount}')
            else:
                logging .info(f'failed to buy {ticker}, price : {price}, amount : {amount}')
        return ret

    def sell(self, ticker, price, amount):
        ret = self.upbit.sell_limit_order(ticker, price, amount)
        return ret

    def cancel_order(self, uuid):
        ret = self.upbit.cancel_order(uuid)
        return ret

    def order_status(self, uuid) -> str:
        try:
            ret = self.upbit.get_order(uuid)['state']
            return ret
        except Exception as e:
            logging.error(e)
            return None

    def connect_account(self):
        try:
            self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)
        except Exception as e:
            logging.log.error(e)

        if self.upbit != None:
            logging.info('Success to access my account')
