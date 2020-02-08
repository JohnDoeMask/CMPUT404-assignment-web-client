#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.split()[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def split_url(self, url):
        # Credit to https://docs.python.org/3/library/urllib.parse.html
        # Parse URL into the following components:
        # scheme, netloc, path, params, query, fragment,
        # username, password, hostname, and port
        parse_results = urllib.parse.urlparse(url)

        # If there is no path in this url,
        # then assign it with "/
        if not parse_results.path:
            path = '/'
        else:
            path = parse_results.path
            query = parse_results.query
            fragment = parse_results.fragment
            if query is not '':
                path += '?' + query
            if fragment is not '':
                path += '#' + fragment

        hostname = parse_results.hostname

        scheme = parse_results.scheme
        if not scheme:
            scheme = "http"
            
        # Credit to https://www.godaddy.com/garage/whats-an-ssl-port-a-technical-guide-for-https/
        if parse_results.port is None:
            # HTTPS connections use TCP port 443. HTTP uses port 80.
            if scheme == "https":
                port = 443
            elif scheme == "http":
                port = 80
        else:
            port = parse_results.port

        return path, hostname, port

    def send_response(self, request, hostname, port):
        # Connect to the url
        self.connect(hostname, port)

        # Send the request
        self.sendall(request)

        # Get all the data
        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)
        print(body)
        return code, body

    def GET(self, url, args=None):
        path, hostname, port = self.split_url(url)

        # Credit to https://www.tutorialspoint.com/http/http_requests.htm
        request = ("GET {0} HTTP/1.1\r\n"
        "Host: {1}\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "\r\n").format(path, hostname)

        code, body = self.send_response(request, hostname, port)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        path, hostname, port = self.split_url(url)

        if args is None:
            args = ""
            headers = "Content-Length: 0\r\n"
        else:
            args = urllib.parse.urlencode(args)
            headers = ("Content-Length: {0}\r\n"
            "Content-Type: application/x-www-form-urlencodeds\r\n").format(str(len(args)))

        # Credit to https://www.tutorialspoint.com/http/http_requests.htm
        request = ("POST {0} HTTP/1.1\r\n"
        "Host: {1}\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "{2}\r\n{3}").format(path, hostname, headers, args)

        code, body = self.send_response(request, hostname, port)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
