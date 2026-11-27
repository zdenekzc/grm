
from __future__ import print_function

try :
   from SocketServer import TCPServer
   from SimpleHTTPServer import SimpleHTTPRequestHandler
except :
   from socketserver import TCPServer
   from http.server import SimpleHTTPRequestHandler

import sys, socket, json, urllib.request, optparse

# https://www.jeasyui.com/tutorial/datagrid/datagrid20.php

tree = [
           { "id": 100, "text": "classes",
             "children" : [
                 { "id": 110, "text": "C", "kind": "cls", "children" : [
                       { "id": 111, "text": "x", "type": "int", "kind": "var" },
                       { "id": 112, "text": "y", "type": "int", "kind": "var" },
                    ]
                 },
                 { "id": 120, "text": "D", "kind": "cls", "children" : [
                       { "id": 121, "text": "show", "type": "void", "kind": "func", "children" : [
                             { "id": 121, "text": "txt", "type": "string", "kind": "param", }
                          ]
                       },
                       { "id": 123, "text": "hide", "type": "void", "kind": "func", },
                    ]
                 }
              ]
           },
           { "id": 300, "text":"files",
             "children" : [
                 { "id": 301, "text": "cone.html" },
                 { "id": 302, "text": "cube.html" },
                 { "id": 302, "text": "jgraph-diagram.html" },
                 { "id": 302, "text": "jgraph-layout.html" },
                 { "id": 302, "text": "jgraph-tree.html" },
                 { "id": 302, "text": "webgl.html" },
             ]
           }
       ]

table = {
            "total" : 3,
            "rows" :
            [
                { "name": "block", "type": "rectangle",
                  "x": 97, "y": 27, "width": 200, "height": 160,
                  "pen": "orange", "brush": "yellow", },

                { "name": "left", "type": "ellipse",
                  "x": 40, "y": 40, "width": 40, "height": 40,
                  "pen": "cornflowerblue", "brush": "blue" },

                { "name": "right", "type": "ellipse",
                  "x": 120, "y": 40, "width": 40, "height": 40,
                  "pen": "cornflowerblue", "brush": "blue" },
            ]
        }

properties = [
               { "name": "Name",  "value" : "Abc", "group": "first" },
               { "name": "Value", "value" : 7, "group": "first", "editor":"numberbox"},
               { "name": "Checked", "value" : True, "group": "second" },
             ]


def str_to_bytes (s) :
    if sys.version_info >= (3,) :
       return bytes (s, "ascii")
    else :
       return bytes (s)


class MyHandler (SimpleHTTPRequestHandler):

     def do_GET(self):
         if self.path=="/tree.json":
            self.send_response (200)
            self.send_header ("Content-type", "application/json")
            self.end_headers ()
            self.wfile.write (str_to_bytes(json.dumps(tree)))
            return
         if self.path=="/table.json":
            self.send_response (200)
            self.send_header ("Content-type", "application/json")
            self.end_headers ()
            self.wfile.write (str_to_bytes(json.dumps(table)))
            return
         if self.path=="/properties.json":
            self.send_response (200)
            self.send_header ("Content-type", "application/json")
            self.end_headers ()
            self.wfile.write (str_to_bytes(json.dumps(properties)))
            return
         SimpleHTTPRequestHandler.do_GET (self)

options = optparse.OptionParser ()
options.add_option ("-p", "--port", dest="port", default = 1234, action="store", help="Web server TCP port number")
(opts, args) = options.parse_args ()
port = int (opts.port)

server = TCPServer (("", port), MyHandler)
server.socket.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try :
   print ("serving at port", port)
   server.serve_forever ()
except KeyboardInterrupt :
   print ("Control C received, shutting down the web server")
finally :
   server.socket.close ()

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all

