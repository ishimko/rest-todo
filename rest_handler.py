import http_handler
from http import HTTPStatus
import json

from logger import log


class RESTHandler(http_handler.HTTPRequestHandler):
    tasks = [
        {
            'id': 1,
            'title': 'Do course work',
            'description': 'oops',
            'done': False
        },
        {
            'id': 2,
            'title': 'Do OOP',
            'description': 'Lab 4, 5',
            'done': False
        }

    ]

    def do_GET(self):
        segments = self.path.split('/')
        method = segments[1]
        if method == 'todo':
            if len(segments) == 3:
                try:
                    task_id = int(segments[2])
                except ValueError:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self.get_task(task_id)
            else:
                self.get_all_tasks()
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def _send_json(self, object):
        self.send_response(HTTPStatus.OK, json.dumps(object, indent=True))

    def get_all_tasks(self):
        log('sending all tasks')
        self._send_json(self.tasks)

    def do_POST(self):
        post_data = self.rfile.read(self.headers['Content-Length'])
        self.send_response(HTTPStatus.OK, post_data)

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
            if isinstance(content, str):
                content = content.encode('UTF-8', 'replace')
            self.wfile.write(content)

    def get_task(self, task_id):
        task = [x for x in self.tasks if x['id'] == task_id]

        if not task:
            self.send_error(HTTPStatus.NOT_FOUND)
            log('task {} not found'.format(task_id))
        else:
            log('sending task {}'.format(task_id))
            self._send_json(task[0])
