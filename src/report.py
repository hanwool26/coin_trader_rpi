import os
import datetime
from src.event import PER_BUY
Today = datetime.date.today()
Now = datetime.datetime.now()

OUTPUT_DIR = '/usr/share/coin_trade/output/'

class Report():
    def __init__(self):
        print('Init Report()')
        file_url = OUTPUT_DIR

    def make_file_path(self) -> str:
        y_m_str = 'report_%s-%s.txt' % (Today.year, Today.month)
        file_path = os.path.join(OUTPUT_DIR, y_m_str)
        return file_path

    def make_report_str(self, name, sold_price, avg_price, amount, invest_rate, buy_count):
        profit = (sold_price - avg_price) * amount
        progress = (buy_count / PER_BUY) * 100
        report_str = '%s / %s / 평단가 : %s원 / 매도가 : %s원 / 이익율 : %s%% / 손익 : %s원  / 진행률 : %s%%\n' % (
            Now, name, avg_price, sold_price, invest_rate, profit, progress)
        return report_str

    def save_report(self, name, sold_price, avg_price, amount, invest_rate, buy_count):
        file_path = self.make_file_path()
        report_str = self.make_report_str(name,sold_price,avg_price,amount,invest_rate,buy_count)
        with open(file_path, "a") as f:
            f.write(report_str)
