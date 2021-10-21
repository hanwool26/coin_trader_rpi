from openpyxl import load_workbook
import os
import logging
from src.util import DATA_PATH

class LoadFile:
    def __init__(self, file):
        try:
            self.load_wb = load_workbook(os.path.join(DATA_PATH, file), data_only=True)
            logging.getLogger('LOG').info(f'loading {file}')
        except Exception as e:
            logging.getLogger('LOG').error(f'failed to load {file} : {e}')

    def get_couple_list(self):
        couple_list = list()
        if self.load_wb != None:
            ws = self.load_wb.active
            for row in ws.values:
                couple_list.append(row)

            # del couple_list[0] # delete header in couple_list
            #for attr in couple_list:
            #    print(attr)
        del couple_list[0] # delete HEADER

        return couple_list

