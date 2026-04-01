import cgi
import json
import logging
import os
import urllib.parse
import uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from io import BytesIO

from PIL import Image

HOST = '0.0.0.0'
PORT = 8000

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

logger = logging.getLogger('image_server')
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(
        os.path.join(LOGS_DIR, 'app.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_content_type(path):
    if path.endswith('.css'):
        return 'text/css'
    elif path.endswith('.js'):
        return 'application/javascript'
    elif path.endswith('.png'):
        return 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        return 'image/jpeg'
    elif path.endswith('.gif'):
        return 'image/gif'
    return 'application/octet-stream'


class ImageServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0]

        if path == '/' or path == '':
            self.serve_file('index.html', 'text/html; charset=utf-8')

        elif path == '/upload':
            self.serve_file('form/upload.html', 'text/html; charset=utf-8')

        elif path == '/images':
            self.serve_file('form/images.html', 'text/html; charset=utf-8')

        elif path == '/api/images':
            self.handle_list_images()

        elif path.startswith('/image-uploader/'):
            relative_path = path.lstrip('/')
            file_path = os.path.join(STATIC_DIR, relative_path)
            content_type = get_content_type(path)
            self.serve_absolute_file(file_path, content_type)

        elif path.startswith('/images/'):
            filename = os.path.basename(path)
            file_path = os.path.join(IMAGES_DIR, filename)
            content_type = get_content_type(path)
            self.serve_absolute_file(file_path, content_type)

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        path = self.path.split('?')[0]

        if path == '/upload':
            self.handle_upload()
        else:
            self.send_error(404, "Not Found")

    def do_DELETE(self):
        path = self.path

        if path.startswith('/delete'):
            query = urllib.parse.urlparse(path).query
            params = urllib.parse.parse_qs(query)

            filename = params.get('name', [None])[0]

            if not filename:
                self.send_json(400, {"success": False, "error": "No filename"})
                return

            file_path = os.path.join(IMAGES_DIR, filename)

            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f'Видалено: {filename}')
                self.send_json(200, {"success": True})
            else:
                self.send_json(404, {"success": False, "error": "File not found"})
        else:
            self.send_json(404, {"success": False, "error": "Not found"})

    def handle_upload(self):
        content_type = self.headers.get('Content-Type', '')

        if 'multipart/form-data' not in content_type:
            self.send_json(400, {
                'success': False,
                'error': 'Content-Type must be multipart/form-data'
            })
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > MAX_FILE_SIZE:
            self.send_json(400, {
                'success': False,
                'error': 'File is too large. Maximum size is 5 MB'
            })
            return

        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],
                }
            )

            if 'file' not in form:
                self.send_json(400, {
                    'success': False,
                    'error': 'File field is missing'
                })
                return

            file_item = form['file']

            if not file_item.filename:
                self.send_json(400, {
                    'success': False,
                    'error': 'No file selected'
                })
                return

            original_filename = os.path.basename(file_item.filename)
            _, ext = os.path.splitext(original_filename)
            ext = ext.lower()

            if ext not in ALLOWED_EXTENSIONS:
                logger.info(f'Помилка: непідтримуваний формат файлу ({original_filename})')
                self.send_json(400, {
                    'success': False,
                    'error': 'Unsupported file format'
                })
                return

            file_data = file_item.file.read()

            if len(file_data) > MAX_FILE_SIZE:
                self.send_json(400, {
                    'success': False,
                    'error': 'File is too large. Maximum size is 5 MB'
                })
                return

            try:
                Image.open(BytesIO(file_data)).verify()
            except Exception:
                self.send_json(400, {
                    'success': False,
                    'error': 'Invalid image file'
                })
                return

            unique_filename = f'{uuid.uuid4().hex}{ext}'
            save_path = os.path.join(IMAGES_DIR, unique_filename)

            with open(save_path, 'wb') as f:
                f.write(file_data)

            logger.info(f'Успіх: зображення {original_filename} завантажено.')

            self.send_json(200, {
                'success': True,
                'filename': unique_filename,
                'url': f'/images/{unique_filename}'
            })

        except Exception as e:
            logger.info(f'Помилка завантаження: {str(e)}')
            self.send_json(500, {
                'success': False,
                'error': 'Internal server error'
            })

    def handle_list_images(self):
        files = []

        for filename in os.listdir(IMAGES_DIR):
            file_path = os.path.join(IMAGES_DIR, filename)

            if os.path.isfile(file_path):
                files.append({
                    'filename': filename,
                    'url': f'/images/{filename}'
                })

        self.send_json(200, files)

    def serve_file(self, relative_path, content_type):
        file_path = os.path.join(STATIC_DIR, relative_path)
        self.serve_absolute_file(file_path, content_type)

    def serve_absolute_file(self, file_path, content_type):
        if not os.path.exists(file_path):
            self.send_error(404, "File not found")
            return

        with open(file_path, 'rb') as f:
            content = f.read()

        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, status_code, data):
        response = json.dumps(data).encode('utf-8')

        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


def main():
    server = ThreadingHTTPServer((HOST, PORT), ImageServerHandler)
    print(f"🚀 Server started at http://localhost:{PORT}")
    logger.info(f'Сервер запущено на {HOST}:{PORT}')
    server.serve_forever()


if __name__ == "__main__":
    main()