import os
import logging
import pyupbit
import numpy as np
import pandas as pd
import time
import requests
from ast import literal_eval
from pyupbit.request_api import _call_public_api

KRW = 'KRW'
BTC = 'BTC'

def fetch_market():
    url = "https://api.upbit.com/v1/market/all"
    market, req_limit_info = _call_public_api(url, isDetails=False)
    return market

market_info = fetch_market()

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
        logging.getLogger('LOG').error(f'no found {name} in market list')
    else:
        return pyupbit.get_current_price(ticker)

def from_name_to_ticker(name) -> str:
    ticker = None
    for attr in market_info:
        if name == attr['korean_name']:
            if KRW in attr['market']:
                ticker = attr['market']
                break

    if ticker == None:
        logging.error(f'no found {name} in market list')
    return ticker

# RSI계산 함수
def rsi_calculate(l, n, sample_number):  # l = price_list, n = rsi_number

    diff = []
    au = []
    ad = []

    if len(l) != sample_number:  # url call error
        return -1
    for i in range(len(l) - 1):
        diff.append(l[i + 1] - l[i])  # price difference

    au = pd.Series(diff)  # list to series
    ad = pd.Series(diff)

    au[au < 0] = 0  # remove ad
    ad[ad > 0] = 0  # remove au

    _gain = au.ewm(com=n, min_periods=sample_number - 1).mean()  # Exponentially weighted average
    _loss = ad.abs().ewm(com=n, min_periods=sample_number - 1).mean()
    RS = _gain / _loss
    try:
        rsi = 100 - (100 / (1 + RS.iloc[-1]))
    except Exception as e:
        print(e)
        return 0

    return rsi


def get_RSI(coin, time_unit='weeks', unit=None):  # 1분 RSI 분석
    if time_unit == 'minutes':
        url = "https://api.upbit.com/v1/candles/" + time_unit + "/" + str(unit)  # 1, 3, 5, 10, 15, 30, 60, 240
    else:
        url = "https://api.upbit.com/v1/candles/" + time_unit # days, weeks, months

    ticker = from_name_to_ticker(coin)
    coin_to_price = {}
    rsi_number = 14
    sample = 200
    request_limit_per_second = -10
    request_count = 0
    request_time_list = np.array([])

    # 코인별 시간별 가격
    querystring = {"market": ticker, "count": str(sample)}  # 캔들 갯수
    if (request_count < request_limit_per_second):  # max api 요청수, 분당 600, 초당 10회
        request_count += 1  # 요청수 1회 증가
    else:
        request_time_sum = np.sum(request_time_list[request_limit_per_second:])
        if (request_time_sum >= 1):
            pass
        else:
            time.sleep(1 - request_time_sum)

    response = requests.request("GET", url, params=querystring)
    r_str = response.text
    r_str = r_str.lstrip('[')  # 첫 문자 제거
    r_str = r_str.rstrip(']')  # 마지막 문 제거
    r_list = r_str.split("}")  # str를 }기준으로 쪼개어 리스트로 변환

    date_to_price = {}
    price_list = []

    for j in range(len(r_list) - 1):
        r_list[j] += "}"
        if j != 0:
            r_list[j] = r_list[j].lstrip(',')
        r_dict = literal_eval(r_list[j])  # stinrg to dict
        temp_dict = {r_dict["candle_date_time_kst"]: r_dict["trade_price"]}
        date_to_price.update(temp_dict)  # 시간-가격 매핑
        price_list.append(r_dict["trade_price"])  # 가격 리스트
    price_list.reverse()  # order : past -> now
    temp_dict = {ticker: date_to_price}
    coin_to_price.update(temp_dict)  # 코인-시간-가격 매핑
    return round(rsi_calculate(price_list, rsi_number, len(price_list)),2)  # RSI 계산

def get_sort_rsi():
    coin_rsi = dict()
    print('rsi calculating...')
    for coin in get_coin_list():
        rsi = get_RSI(coin)
        if rsi < 20: # excluding abnormal rsi value of coin.
            continue
        coin_rsi.update({coin: rsi})
    res = sorted(coin_rsi.items(), key=(lambda x:x[1]), reverse=False)

    print('finish')
    return res

print(get_sort_rsi())



