import http_handler
from http import HTTPStatus
from logger import log


class RESTHandler(http_handler.HTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(HTTPStatus.OK)

    def do_GET(self):
        self.send_response(HTTPStatus.OK, 'GET')

    def do_POST(self):
        self.send_response(HTTPStatus.OK, 'POST')

    def do_DELETE(self):
        self.send_response(HTTPStatus.OK, 'DELETE')

    def do_PUT(self):
        self.send_response(HTTPStatus.OK, 'PUT')

    def send_response(self, code, content=None):
        super(RESTHandler, self).send_response(code)
        self.send_header('Content-Type', 'text/html;charset=utf-8')
        if content is not None:
            self.send_header('Content-Length', len(content))
        self.end_headers()

        if content is not None:
            content = content.encode('UTF-8', 'replace')
            self.wfile.write(content)
