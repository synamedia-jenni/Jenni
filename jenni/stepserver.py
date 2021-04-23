import json
import logging
import os
from time import sleep
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

http_server = None
request_event = threading.Event()
response_event = threading.Event()
response_result = None
response_status = "initial"
request_num = 0
request_filename = None


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # logging.debug("http POST request received")
        global response_result
        global response_status
        content_length = int(self.headers["Content-Length"])
        try:
            data = json.loads(self.rfile.read(content_length).decode())
            response_status = data["status"]
            response_result = data["result"]
        except Exception as ex:
            logging.error(f"ERROR: Response failure: {ex}")
            response_status = "error"
        if response_status != "initial":
            response_event.set()
        # logging.debug('waiting for request_event')
        request_event.wait()
        # logging.debug('got request_event')
        request_event.clear()
        self.send_response(200)
        self.send_header("Content-Length", str(len(request_filename.encode())))
        self.end_headers()
        self.wfile.write(request_filename.encode())

    def log_request(self, code="-", size="-"):
        pass


def get_free_port() -> int:
    # Taken from https://stackoverflow.com/questions/2838244/get-open-tcp-port-in-python/2838309#2838309
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def start_server():
    global http_server
    if http_server is not None:
        logging.warning("http_server already created")
        return
    # port = 1234
    # find free port:
    port = get_free_port()
    url = f"http://localhost:{port}"
    logging.debug(f"Listening on {url}")
    with open("_url.txt", "w") as fp:
        fp.write(url)
    httpd = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
    http_server = threading.Thread(name="http_server", target=httpd.serve_forever)
    http_server.setDaemon(True)
    http_server.start()


def execute_groovy(s, exit_status=None):
    global request_filename
    global request_num
    request_num += 1
    request_filename = f"request-{request_num}.groovy"
    with open(request_filename, "w") as fp:
        fp.write("{ it-> ")
        fp.write(s)
        fp.write("}")
    logging.debug(f"Sending request for {s}")
    request_event.set()
    if exit_status is not None:
        sleep(1)
        return
    response_event.wait()
    response_event.clear()
    logging.debug(f"Got response {response_result}")
    os.unlink(request_filename)
    if response_status == "ok":
        return response_result
    raise Exception(f"Groovy response failure: {response_result}")
