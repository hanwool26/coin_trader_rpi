from src.event_couple import *
from src.event_infinite import *
from src.account import *
import logging
from src import log

class Manager:
    def __init__(self, socket): # main_window, couple_list):
        self.account = None
        self.socket = socket
        # self.main_window = main_window
        self.couple_event = list()
        self.infinite_event = list()
        self.infinite_idx = 0
        self.socket = socket

        # if couple_list is not None:
        #    self.init_eventcouple(couple_list)
    '''
    def init_eventcouple(self, couple_list):
        for idx, couple_coin in enumerate(couple_list):
            primary, chain, cohesion = couple_coin[0], couple_coin[1], couple_coin[2]
            self.couple_event.insert(idx, EventCouple(idx, self.account, self.main_window, primary, chain, cohesion))
    '''
    def get_account(self, access_key, secret_key):
        if self.account == None:
            self.account = Account(access_key, secret_key)
            self.account.connect_account()
        else:
            logging.info("Already got account instance")

    def update_asset(self):
        asset = self.account.get_asset()
        signal = {'command': 'asset_update', 'asset': asset}
        signal = json.dumps(signal)
        self.socket.send(signal)

    def process(self, data):
        coin_info = dict()
        command = data['command']
        if command == 'do_start':
            selected_id = None  # for only coupling trade
            trade = data['trade']
            coin_info['coin_name'] = data['coin_name']
            coin_info['balance'] = data['balance']
            coin_info['interval'] = data['interval']
            coin_info['repeat'] = data['repeat']
            self.do_start(selected_id, trade, coin_info)
        elif command == 'do_stop':
            trade = data['trade']
            selected_id = data['sel_id']
            self.do_stop(selected_id, trade)
        elif command == 'account':
            access_key = data['access_key']
            secret_key = data['secret_key']
            self.get_account(access_key, secret_key)
            self.init_update()
            self.update_asset()
        elif command == 'request_asset':
            self.update_asset()

    def do_start(self, selected_id: list, trade, coin_info :dict):  # trade : method for algorithm ( ex> couple, infinite )
        if trade == 'couple':
            for idx in selected_id:
                self.couple_event[idx].start()
        elif trade == 'infinite':
            # to do -> take variables which is needed to make class from json format.
            if coin_info['interval'] != 0:
                self.infinite_event.insert(self.infinite_idx, EventInfinite(self.infinite_idx, self.account, self.socket, coin_info['coin_name'],
                                                                        coin_info['balance'], coin_info['interval'], coin_info['repeat']))
                self.infinite_event[self.infinite_idx].start()
                self.infinite_idx += 1
            else:
                logging.info(f'이벤트 생성 실패 : Input the valid Interval')

    def do_stop(self, selected_id: list, trade):
        if trade == 'couple':
            for idx in selected_id:
                self.couple_event[idx].close_thread()
        elif trade == 'infinite':
            for idx in selected_id:
                if idx < self.infinite_idx:
                    self.infinite_event[idx].close(False)
                    self.sort_event(idx)

    def set_max_row(self):
        signal = {'command':'set_max_row', 'row':self.infinite_idx}
        signal = json.dumps(signal)
        self.socket.send(signal)

    def init_update(self):
        self.set_max_row()
        for event in self.infinite_event:
            event.reset_list()

    def sort_event(self, id):
        size = len(self.infinite_event)
        for idx in range(id, size+1):
            if idx+1 < self.infinite_idx:
                self.infinite_event[idx] = self.infinite_event[idx+1]
                self.infinite_event[idx].ev_id = idx
        del self.infinite_event[size-1]
        self.infinite_idx -=1
        self.init_update()


