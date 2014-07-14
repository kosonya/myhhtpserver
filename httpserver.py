#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import re
import os
import threading
import hostingcocosting

class HTTPRequestHandler(BaseHTTPRequestHandler):

	def address_string(self): #Fix for the slow response
		#host, _ = self.client_address[:2]
		return "maxikov.com"

	def return_file(self, file_name, content_type):
		filespath = os.path.dirname(os.path.realpath(__file__))
		filename = os.path.join(filespath, file_name)
		f = open(filename, "r")
		content = "".join(f.readlines())
		f.close()
		self.send_response(200)
		self.send_header('Content-Type', content_type)
		self.end_headers()
		self.wfile.write(content)
		self.wfile.close()

	def do_GET(self):
		if None != re.search("hosting-cocosting", self.path):
			hosting_cocosting = hostingcocosting.HostingCocosting(self)
			if not hosting_cocosting.serve():
				if None != re.search("hosting-cocosting/my.css", self.path):
					self.return_file("my.css", "text/css")
				elif None != re.search("hosting-cocosting/z0r-de_22.swf", self.path):
					self.return_file("z0r-de_22.swf", "application/x-shockwave-flash")
				else:
					self.return_file("index.html", "text/html")
		elif None != re.search("my.css", self.path):
			self.return_file("my.css", "text/css")
		elif None != re.search("z0r-de_22.swf", self.path):
			self.return_file("z0r-de_22.swf", "application/x-shockwave-flash")
		else:
			self.return_file("index.html", "text/html")


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	allow_reuse_address = True
 
	def shutdown(self):
		self.socket.close()
		HTTPServer.shutdown(self)


class SimpleHttpServer():
	def __init__(self, ip, port):
		self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
 
	def start(self):
		self.server_thread = threading.Thread(target=self.server.serve_forever)
		self.server_thread.daemon = False
		self.server_thread.start()
 
	def waitForThread(self):
		self.server_thread.join()
 
	def stop(self):
		self.server.shutdown()
		self.waitForThread()

def main():
	http_server = SimpleHttpServer('', 8080)
	http_server.start()
	http_server.waitForThread()

if __name__ == "__main__":
	main()
