import os
import logging
import pyupbit

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data')
UI_PATH = os.path.join(os.path.dirname(__file__), '../ui')
market_info = pyupbit.fetch_market()

KRW = 'KRW'
BTC = 'BTC'

def get_increase_rate(current_price, base_price):
    if base_price == 0 or base_price == None or current_price == None:
        return 0
    increase_rate = round(((current_price - base_price)/base_price)*100, 2)
    return increase_rate

def get_buying_amount(balance, price, coherence):
    if price == 0:
        return 0
    amount = (balance / price) * coherence
    return round(amount,2)

def get_tick_unit(price):
    if price < 10:
        return 0.01
    elif price < 100:
        return 0.1
    elif price < 1000:
        return 1
    elif price < 10000:
        return 5
    elif price < 100000:
        return 10
    elif price < 500000:
        return 50
    elif price < 1000000:
        return 100
    elif price < 2000000:
        return 500
    else:
        return 1000

def get_above_tick_price(price):
    return price + get_tick_unit(price)

def get_below_tick_price(price):
    return price - get_tick_unit(price)

def get_avg_price(avg_price, price, count):
    avg_price = ((avg_price * (count-1) + price)) / count
    return round(avg_price, 2)

def get_coin_list():
    coin_list = list()
    market_info = pyupbit.fetch_market()
    for attr in market_info:
        if 'KRW' in attr['market']:
            coin_list.append(attr['korean_name'])
    coin_list.sort()

    return coin_list

def price_round(price):
    tick = get_tick_unit(price)
    price = (price // tick) * tick
    return price

def util_strip(string):
    string = string.split()
    return int(string[0])

def get_price_by_name(name):
    ticker = None
    for attr in market_info:
        if name == attr['korean_name']:
            if KRW in attr['market']:
                ticker = attr['market']
                break

    if ticker == None:
        logging.getLogger('LOG').warn(f'no found {name} in market list')
    else:
        return pyupbit.get_current_price(ticker)





