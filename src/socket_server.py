import socket
import json
import time
import logging
import threading

class Socket_Server():
    def __init__(self, port):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.conn_status = False
        self.server_sock.bind(('', port))
        self.manager = None

    def setManager(self, manager):
        self.manager = manager

    def send(self, data):
        if self.conn_status != True:
            logging.info('No connection to client')
        else:
            try:
                self.conn.sendall(data.encode())
            except Exception as e:
                logging.error(f'send() : {e}')
        pass

    def __recv(self):
        while self.conn_status:
            try:
                data = self.conn.recv(1024)
                if data.decode() == 'disconnect':
                    self.close_connection()
                    break
                if data != b'':
                    parse_data = json.loads(data.decode())
                    self.manager.process(parse_data)
            except Exception as e:
                logging.error(f'recv() : {e}')

    def close_connection(self):
        print('close connection()')
        self.conn_status = False
        self.conn.close()

    def connection_thread(self):
        threads = [
            threading.Thread(target=self.__recv, daemon=False),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def wait_for_connection(self):
        logging.info('wait for connection')
        self.server_sock.listen()
        self.conn, peer = self.server_sock.accept()

        logging.info(f'connection success')
        self.conn_status = True
        self.send('connect')

        self.connection_thread()






