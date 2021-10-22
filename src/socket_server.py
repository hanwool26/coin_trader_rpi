import socket
import logging
import threading

class Socket_Server():
    def __init__(self, port):
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None
        self.conn_status = False

        self.threads = [
            threading.Thread(target=self.__send, daemon=True),
            threading.Thread(target=self.__recv, daemon=True),
        ]

    def wait_for_connection(self):
        self.server_sock.bind(('', self.port))
        self.server_sock.listen()
        self.conn, peer = self.server_sock.accept()

        logging.info(f'connection success')
        self.conn_statue = True

        for t in self.threads:
            t.join()






