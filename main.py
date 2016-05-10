from http_handler import HTTPRequestHandler
from socketserver import TCPServer

if __name__ == '__main__':
    server_address = ('', 8000)
    server = TCPServer(server_address, HTTPRequestHandler)
    server.serve_forever()
