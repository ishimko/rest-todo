import socketserver
from logger import log
from http import HTTPStatus
from datetime import datetime


class HTTPRequestHandler(socketserver.StreamRequestHandler):
    HTTP_VERSION = "HTTP/1.1"
    ERROR_MESSAGE_TEMPLATE = """\
    <!DOCTYPE html>
    <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>{code} {title}</title>
        </head>
        <body>
            <h1>{title}</h1>
            <p>{message}</p>
        </body>
    </html>
    """

    ERROR_CONTENT_TYPE = "text/html;charset=utf-8"

    SERVER_INFO = 'python'

    HTTP_RESPONSES = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
                                               'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),
        428: ('Precondition Required',
              'The origin server requires the request to be conditional.'),
        429: ('Too Many Requests', 'The user has sent too many requests '
                                   'in a given amount of time ("rate limiting").'),
        431: ('Request Header Fields Too Large', 'The server is unwilling to '
                                                 'process the request because its header fields are too large.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
        511: ('Network Authentication Required',
              'The client needs to authenticate to gain network access.'),
    }

    def handle(self):
        self.request = str(self.rfile.readline().strip(), 'iso-8859-1')

        if not self.request:
            return

        self.log_request()

        if not self.parse_request():
            return

        method_name = 'do_' + self.command
        if not hasattr(self, method_name):
            self.send_error(HTTPStatus.NOT_IMPLEMENTED, 'Unsupported method {}'.format(self.command))

        method = getattr(self, method_name)
        method()

    def parse_request(self):
        self.command = None
        self.path = None

        words = self.request.split()
        if len(words) == 3:
            self.command, self.path, version = words

            if version[:len('HTTP/')] != 'HTTP/':
                self.send_error(HTTPStatus.BAD_REQUEST, 'Bad request version {}'.format(version))
                return False
        elif not words:
            return False
        else:
            self.send_error(HTTPStatus.BAD_REQUEST, 'Bad request syntax {}'.format(self.request))
            return False

        return self._parse_headers()

    def _parse_headers(self):
        self.headers = {}
        while True:
            line = str(self.rfile.readline().strip(), 'iso-8859-1')
            if line in ('\r\n', '\n', ''):
                break
            semicolon_pos = line.find(':')
            if semicolon_pos == -1:
                return False

            header_name = line[:semicolon_pos].strip()
            header_value = line[semicolon_pos + 1:].strip()
            if header_value.isnumeric():
                header_value = int(header_value)
            self.headers[header_name] = header_value
        return True

    def send_error(self, code, custom_message=None):
        if code in self.HTTP_RESPONSES:

            title, message = self.HTTP_RESPONSES[code]
            if custom_message is None:
                custom_message = message
            content = self.ERROR_MESSAGE_TEMPLATE.format(code=code, title=title, message=custom_message)
            content = content.encode('UTF-8', 'replace')

            self.log_error(code, custom_message)

            self.send_status(code, custom_message)
            self.send_header('Content-Type', self.ERROR_CONTENT_TYPE)
            self.send_header('Connection', 'close')
            self.send_header('Content-Length', len(content))
            self.end_headers()

            if self.command != 'HEAD':
                self.wfile.write(content)

    def log_request(self):
        log('\n\t{}'.format(self.request))

    def log_error(self, code, message):
        log("\n\tERROR\n\t{} {}".format(code, message))

    def send_response(self, code, message=''):
        self.send_status(code, message)
        self.send_header('Server', self.SERVER_INFO)
        self.send_header('Date', self.date_time_string())

    @staticmethod
    def date_time_string():
        return datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

    def send_status(self, code, message):
        if not message:
            message = self.HTTP_RESPONSES[code][0]

        self._add_header("{} {} {}".format(self.HTTP_VERSION, code, message))

    def send_header(self, key, value):
        self._add_header("{}: {}".format(key, value))

    def _add_header(self, header):
        if not hasattr(self, '_headers_buffer'):
            self._headers_buffer = []
        self._headers_buffer.append(header)

    def end_headers(self):
        self._headers_buffer.append('\r\n')
        self.wfile.write(b'\r\n'.join([x.encode('latin-1') for x in self._headers_buffer]))
        self._headers_buffer = []
