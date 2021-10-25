import socket
import json
import time
import logging
import threading

class Socket_Server():
    def __init__(self, manager, port):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.conn_status = False
        self.server_sock.bind(('', port))
        self.manager = manager
        self.cond = threading.Condition()

        self.threads = [
            threading.Thread(target=self.__recv, daemon=True, args=(self.conn, )),
        ]

    def __send(self, data):
        print('send+')
        if self.conn_status != False:
            logging.info('No connection to client')
        else:
            self.conn.sendall(data.encode())
        pass

    def __recv(self, conn):
        print('recv+')
        while self.conn_status:
            data = self.conn.recv(1024)
            if data.decode() == 'disconnect':
                self.close_connection()
                break
            if data != b'':
                self.manager.process(json.loads(data).decode('UTF-8'))

    def close_connection(self):
        logging.info('close connection()')
        self.conn_status = False
        self.conn.close()

    def start_thread(self):
        threads = [
            threading.Thread(target=self.__recv, daemon=True),
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
        time.sleep(1)
        self.start_thread()







