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

    APP_NAME = 'todo'

    def _send_json(self, json_object, code=HTTPStatus.OK):
        self.send_response(code, json.dumps(json_object, indent=True))

    def _request_to_json(self):
        if self._read_request_data():
            try:
                request_json = json.loads(self.request_data)
            except ValueError:
                return False
            self.request_data = request_json
        return True

    def _read_request_data(self):
        if 'Content-Length' in self.headers:
            self.request_data = str(self.rfile.read(self.headers['Content-Length']), 'utf-8')
            return True
        else:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return False

    def get_all_tasks(self):
        log('get_all_tasks: sending all tasks')
        self._send_json(self.tasks)

    def do_GET(self):
        if len(self.segments) < 1:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        app = self.segments[0]
        if app == self.APP_NAME:
            if len(self.segments) == 2:
                try:
                    task_id = int(self.segments[1])
                except ValueError:
                    self.send_error(HTTPStatus.NOT_FOUND)
                    return
                self.get_task(task_id)
            elif len(self.segments) == 1:
                self.get_all_tasks()
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if len(self.segments) < 1:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        app = self.segments[0]
        if app == self.APP_NAME:
            if len(self.segments) == 1 and self._request_to_json() and 'title' in self.request_data:
                self.add_task(self.request_data)
            else:
                self.send_error(HTTPStatus.BAD_REQUEST)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_PUT(self):
        if len(self.segments) < 1:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        app = self.segments[0]
        if app == self.APP_NAME and len(self.segments) == 2:
            try:
                task_id = int(self.segments[1])
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST)
                return

            if self._request_to_json():
                self.update_task(task_id, self.request_data)
            else:
                self.send_error(HTTPStatus.BAD_REQUEST)
        else:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_DELETE(self):
        if len(self.segments) < 1:
            self.send_error(HTTPStatus.FORBIDDEN)
            return

        app = self.segments[0]
        if app == self.APP_NAME and len(self.segments) == 2:
            try:
                task_id = int(self.segments[1])
            except ValueError:
                self.send_error(HTTPStatus.BAD_REQUEST)
                return

            self.delete_task(task_id)

    def add_task(self, task):
        new_task = {
            'id': self.tasks[-1]['id'] + 1,
            'title': task['title'],
            'description': task['description'] if 'description' in task else '',
            'done': False
        }
        self.tasks.append(new_task)

        log('new task added')

        self._send_json(new_task, code=HTTPStatus.CREATED)

    def update_task(self, task_id, new_task):
        task = [x for x in self.tasks if x['id'] == task_id]

        if not task:
            log('update_task: task {} not found'.format(task_id))
            self.send_error(HTTPStatus.NOT_FOUND)
        else:
            log('update_task: task {} updated'.format(task_id))

            task = task[0]
            task['title'] = new_task.get('title', task['title'])
            task['description'] = new_task.get('description', task['description'])
            task['done'] = new_task.get('done', task['done'])

            self._send_json(task)

    def send_response(self, code, content=None):
        super(RESTHandler, self).send_response(code)
        self.send_header('Content-Type', 'application/json')
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
            log('get_task: task {} not found'.format(task_id))
        else:
            log('get_task: task {} sent'.format(task_id))
            self._send_json(task[0])

    def delete_task(self, task_id):
        task = [x for x in self.tasks if x['id'] == task_id]

        if not task:
            log('delete_task: task {} not found'.format(task_id))
            self.send_error(HTTPStatus.NOT_FOUND)
        else:
            log('delete_task: task {} deleted'.format(task_id))
            self.tasks.remove(task[0])
            self._send_json({'result': True})
