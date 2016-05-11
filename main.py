#!/usr/bin/python3

from logger import log
from rest_handler import RESTHandler
from socketserver import TCPServer

if __name__ == '__main__':
    server_address = ('', 8000)
    server = TCPServer(server_address, RESTHandler)

    log('Server started')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        log('Server stopped')

