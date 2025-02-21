# %%
import os
import logging
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from logging.handlers import TimedRotatingFileHandler
import controller as controller
from config import server_port, log_path, font_path
from urllib.parse import urlparse
import socket

# %%
class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, message, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-Length', len(message))
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))

    def do_GET(self):
        parse_result = urlparse(self.path)
        if parse_result.path == '/':
            controller.hello(self)
        else:
            file_path = parse_result.path.lstrip('/')  # remove the leading '/'
            try:
                if file_path == 'show':
                    controller.show(self)
                elif file_path == 'bytes':
                    controller.bytes(self)
                else:
                    self.send_error(404)
            except Exception as e:
                logging.error(e)
                self.send_error(500)

# %%
def run_server(server_class=ThreadingHTTPServer, handler_class=RequestHandler):
    server_address = ('0.0.0.0', server_port)
    httpd = server_class(server_address, handler_class)
    logging.info(f'Server started on port {server_port}')
    httpd.serve_forever()

if __name__ == '__main__':
    # create dirs
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] => %(message)s",
        handlers=[
            TimedRotatingFileHandler(log_path, 'D', 14, 0),
            logging.StreamHandler()
        ],
    )

    logging.info('Starting server...')
    run_server()

    # Print server IP address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    logging.info(f'Server IP address: {ip_address}')