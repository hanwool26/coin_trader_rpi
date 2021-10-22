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

        self.threads = [
            threading.Thread(target=self.__recv, daemon=False),
        ]
    def setManager(self, manager):
        self.manager = manager

    def send(self, data):
        print('send+')
        if self.conn_status != True:
            logging.info('No connection to client')
        else:
            self.conn.sendall(data.encode())
        pass

    def __recv(self):
        print('recv+')
        while self.conn_status:
            data = self.conn.recv(1024)
            if data != b'':
                parse_data = json.loads(data.decode())
                self.manager.process(parse_data)
        pass

    def close_connection(self):
        print('close connection()')
        self.conn_status = False
        self.conn.close()

    def wait_for_connection(self):
        self.server_sock.listen()
        self.conn, peer = self.server_sock.accept()

        logging.info(f'connection success')
        self.conn_status = True

        for t in self.threads:
            t.start()

        time.sleep(3)
        self.send('good')
        self.close_connection()






