import pyupbit
import logging
from src.util import market_info, KRW

class Coin:
    def __init__(self, name):
        self.name = name
        self.ticker = self.from_name_to_ticker(name)

        logging.getLogger('LOG').info(f'init coin : {name}({self.ticker})')

    def from_name_to_ticker(self, name) -> str:
        ticker = None
        for attr in market_info:
            if name == attr['korean_name']:
                if KRW in attr['market']:
                    ticker = attr['market']
                    break

        if ticker == None:
            logging.getLogger('LOG').warn(f'no found {name} in market list')

        return ticker

    def get_current_price(self):
        return pyupbit.get_current_price(self.ticker)
