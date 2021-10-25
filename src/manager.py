from src.event_couple import *
from src.event_infinite import *
import logging
from src import log
class Manager:
    def __init__(self, account, socket): # main_window, couple_list):
        self.account = account
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

    def process(self, data):
        # todo
        # -> json format : {command, coin_name, balance, interval, repeat}
        if data['command'] == 'do_start':
            pass
        elif data['command'] == 'do_stop':
            pass
        print(data)
        coin_info = dict()
        selected_id = list()
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
            selected_id = data['selected_id']
            self.do_stop(selected_id, trade)

    def do_start(self, selected_id: list, trade, coin_info :dict):  # trade : method for algorithm ( ex> couple, infinite )
        if trade == 'couple':
            for idx in selected_id:
                self.couple_event[idx].start()
        elif trade == 'infinite':
            # to do -> take variables which is needed to make class from json format.
            self.infinite_event.insert(self.infinite_idx, EventInfinite(self.infinite_idx, self.account, coin_info['coin_name'],
                                                                        coin_info['balance'], coin_info['interval'], coin_info['repeat']))
            self.infinite_event[self.infinite_idx].start()
            self.infinite_idx += 1

    def do_stop(self, selected_id: list, trade):
        if trade == 'couple':
            for idx in selected_id:
                self.couple_event[idx].close_thread()
        elif trade == 'infinite':
            for idx in selected_id:
                self.infinite_event[idx].close_thread()
