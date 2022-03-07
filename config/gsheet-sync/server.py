from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse;
import io;
import json
import cgi
import regsync

class myHandler(BaseHTTPRequestHandler):
  def __get_Parameter(self, key):
    if hasattr(self, "_myHandler__param") == False:
      if "?" in self.path:
        self.__param = dict(urlparse.parse_qsl(self.path.split("?")[1], True));
      else :
        self.__param = {};
    if key in self.__param:
      return self.__param[key];
    return None;

  def __set_Header(self, code):
    self.send_response(code);
    self.send_header('Content-type','text/html');
    self.end_headers();

  def __set_Body(self, data):
    self.wfile.write(data.encode());

#   def __get_Post_Parameter(self, key):
#     if hasattr(self, "_myHandler__post_param") == False:
#       data = self.rfile.read(int(self.headers['Content-Length']));
#     if data is not None:
#       self.__post_param = dict(urlparse.parse_qs(data.decode()));
#     else:
#       self.__post_param = {};
#
#     if key in self.__post_param:
#       return self.__post_param[key][0];

    return None;

  def do_POST(self):
    ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
    # refuse to receive non-json content
    if ctype != 'application/json':
      self.send_response(400)
      self.end_headers()
      return

    # read the message and convert it into a python dictionary
    length = int(self.headers['Content-Length'])
    message = json.loads(self.rfile.read(length))
    if message.get('idx') == None:
        message['idx'] = 0
    if message.get('col') == None:
        message['col'] = 1
    if message.get('row') == None:
        message['row'] = 2
    if message.get('reg') == None:
        message['reg'] = 'localhost:5000'
    if message.get('docker') == None:
        message['docker'] = ''
    if message.get('quay') == None:
        message['quay'] = ''
    if message.get('gcr') == None:
        message['gcr'] = ''
    if message.get('output') == None:
        message['output'] = '/tmp'
    if message.get('notify') == None:
        message['notify'] = 'http://localhost:3000'

    body = f"""
Parse google sheet{message['sheet']}(({message['idx']})) in column {message['col']} from {message['row']}
Image sync to {message['reg']} with credential
  docker:{message['docker']}
  quay:{message['quay']}
  gcr:{message['gcr']}
When synced, request to {message['notify']}, then output result to {message['output']}"""
    print(body)

    regsync.run(message['sheet'], int(message['idx']), int(message['col']), int(message['row']), message['reg'], message['docker'], message['quay'], message['gcr'], message['output'], message['notify'])

    # send the message back
    self.__set_Header(200);
    self.__set_Body(body);
#     self.wfile.write(bytes(json.dumps(message)))

  def do_GET(self):
#      sheet = self.__get_Parameter('sheet');
    #     idx = self.__get_Parameter('idx');
    #     if idx == None:
    #         idx = 0
    #
    #     col = self.__get_Parameter('col');
    #     if col == None:
    #         col = 1
    #
    #     row = self.__get_Parameter('row');
    #     if row == None:
    #         row = 2
    #
    #     reg = self.__get_Parameter('reg');
    #     print(reg)
    #     if reg == None:
    #         reg = 'localhost:5000'
    #
    #     docker = self.__get_Parameter('docker');
    #     if docker == None:
    #         docker = ''
    #     quay = self.__get_Parameter('quay');
    #     if quay == None:
    #         quay = ''
    #     gcr = self.__get_Parameter('gcr');
    #     if gcr == None:
    #         gcr = ''
    #
    #     output = self.__get_Parameter('output');
    #     if output == None:
    #         output = '/tmp'
    #
    #     notify = self.__get_Parameter('notify');
    #     print(notify)
    #     if notify == None:
    #         notify = 'http://localhost:3000'
    #     regsync.run(sheet, idx, col, row, reg, docker, quay, gcr, output, notify)
    self.__set_Header(200);
#     self.__set_Body(body);

httpd = HTTPServer(('', 8080), myHandler);
httpd.serve_forever();
