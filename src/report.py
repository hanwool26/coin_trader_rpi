import os
import datetime
import logging
from src.event import PER_BUY

OUTPUT_DIR = '/usr/share/coin_trade/output/'

class Report():
    def __init__(self):
        file_url = OUTPUT_DIR
        Today = None
        Now = None

    def make_file_path(self) -> str:
        y_m_str = 'report_%s-%s.txt' % (self.Today.year, self.Today.month)
        file_path = os.path.join(OUTPUT_DIR, y_m_str)
        return file_path

    def make_report_str(self, name, sold_price, avg_price, amount, invest_rate, buy_count):
        profit = (sold_price - avg_price) * amount
        progress = (buy_count / PER_BUY) * 100
        report_str = '%s / %s / 평단가 : %s원 / 매도가 : %s원 / 이익율 : %s%% / 손익 : %s원  / 진행률 : %s%%\n' % (
            self.Now, name, avg_price, sold_price, invest_rate, round(profit, 2), progress)
        return report_str

    def save_report(self, name, sold_price, avg_price, amount, invest_rate, buy_count):
        self.Today = datetime.date.today()
        self.Now = datetime.datetime.now()
        file_path = self.make_file_path()
        report_str = self.make_report_str(name,sold_price,avg_price,amount,invest_rate,buy_count)
        logging.info(report_str)
        with open(file_path, "a") as f:
            f.write(report_str)
