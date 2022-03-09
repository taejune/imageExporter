from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse
import os
import io
import json
import cgi
import regsync

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1_KVOzzVlAl8VQ6y6I4y2NnsokjF-yE51uOXcZPyzDEU/edit#gid=0"
DEFAULT_SHEET_IDX = 0
DEFAULT_COL_NUM = 1
DEFAULT_ROW_NUM = 2
DEFAULT_REGISTRY_URL = "localhost:5000"
DEFAULT_NOTIFY_URL = "http://localhost:3000/run"

class myHandler(BaseHTTPRequestHandler):
  def __get_Parameter(self, key):
    if hasattr(self, "_myHandler__param") == False:
      if "?" in self.path:
        self.__param = dict(urlparse.parse_qsl(self.path.split("?")[1], True))
      else :
        self.__param = {}
    if key in self.__param:
      return self.__param[key]
    return None

  def __set_Header(self, code):
    self.send_response(code)
    self.send_header('Content-type','text/html')
    self.end_headers()

  def __set_Body(self, data):
    self.wfile.write(data.encode())

  def __get_Post_Parameter(self, key):
    if hasattr(self, "_myHandler__post_param") == False:
      data = self.rfile.read(int(self.headers['Content-Length']))
    if data is not None:
      self.__post_param = dict(urlparse.parse_qs(data.decode()))
    else:
      self.__post_param = {}

    if key in self.__post_param:
      return self.__post_param[key][0]
    return None

  def do_POST(self):
    print('{request} from {client}...'.format(request=self.requestline, client=self.client_address))
    ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
    # refuse to receive non-json content
    if ctype != 'application/json':
      self.send_response(400)
      self.end_headers()
      return
    # read the message and convert it into a python dictionary
    length = int(self.headers['Content-Length'])
    message = json.loads(self.rfile.read(length))

    if message.get('sheet') == None:
        message['sheet'] = os.environ['SHEET_URL'] if os.environ.get('SHEET_URL') is not None else DEFAULT_SHEET_URL
    if message.get('idx') == None:
        message['idx'] = os.environ['SHEET_IDX'] if os.environ.get('SHEET_IDX') is not None else DEFAULT_SHEET_IDX
    if message.get('col') == None:
        message['col'] = os.environ['COL_NUM'] if os.environ.get('COL_NUM') is not None else DEFAULT_COL_NUM
    if message.get('row') == None:
        message['row'] = os.environ['ROW_FROM'] if os.environ.get('ROW_FROM') is not None else DEFAULT_ROW_NUM
    if message.get('reg') == None:
        message['reg'] = os.environ['REGISTRY_URL'] if os.environ.get('REGISTRY_URL') is not None else DEFAULT_REGISTRY_URL
    if message.get('docker') == None:
        message['docker'] = os.environ['DOCKER_CRED'] if os.environ.get('DOCKER_CRED') is not None else ''
    if message.get('quay') == None:
        message['quay'] = os.environ['QUAY_CRED'] if os.environ.get('QUAY_CRED') is not None else ''
    if message.get('gcr') == None:
        message['gcr'] = os.environ['GCR_CRED'] if os.environ.get('GCR_CRED') is not None else ''
    if message.get('notify') == None:
        message['notify'] = os.environ['NOTIFY_URL'] if os.environ.get('NOTIFY_URL') is not None else DEFAULT_NOTIFY_URL

    print('Sync {reg} to {reg}'.format(sheet=message['sheet'],  reg=message['reg']))
    res = regsync.run(message['sheet'], int(message['idx']), int(message['col']), int(message['row']),
        message['reg'], message['docker'], message['quay'], message['gcr'], message['notify'])

    print('Uploading {reg}'.format(sheet=message['sheet'],  reg=message['reg']))
    #     response = requests.get(notify_to)
    #     results['uploads'] = { 'status': response.status_code, 'msg': response.text }
    self.__set_Header(200)
    self.wfile.write(bytes(json.dumps(res), 'utf-8'))

  def do_GET(self):
    self.__set_Header(200)

print('Listening on 8080...')
httpd = HTTPServer(('', 8080), myHandler)
httpd.serve_forever()
