#!/usr/bin/env python
#-*- coding:utf8 -*-

import os
import os.path
import re
import mimetypes
import urllib

class HostingCocosting(object):
	def __init__(self, http_request_handler):
		self.handler = http_request_handler
		self.share_path = "/mnt/data/Public"

	def get_files_list(self):
		return [ f for f in os.listdir(self.share_path) if os.path.isfile(os.path.join(self.share_path,f)) and not os.path.islink(os.path.join(self.share_path,f)) and f[0] != "."]

	def get_requested_file_name(self):
		name = self.handler.path
		name = urllib.unquote(name)		
		name = name.split('/')[-1]
		name = name.split('\\')[-1] #In case you're a pervert running this thing on Windows
		return name

	def create_file_list_page(self): #Yes, yes! Judge me for this! Judge me harder!
		page = "<html>\n"
		page += "\t<head>\n"
		page += "\t\t<title>Hosting Cocosting</title>\n"
		page += "\t\t<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n"
		page += "\t</head>\n"
		page += "\t<body>\n"
		
		files_list = self.get_files_list()
		if not files_list:
			page += "\t\t<p>Move along, nothing to see here!</p>\n"
		else:
			page += "\t\t<ul>\n"
			files_list.sort()
			for filename in files_list:
				filename = filename.decode("utf-8")
				page += (u"\t\t\t<li><a href=\"hosting-cocosting/%s\">%s</a></li>\n" % (filename, filename)).encode("utf-8")
			page += "\t\t</ul>\n"

		page += "\t</body>\n"
		page += "</html>"
		return page


	def serve_file(self, filename):
		file_path = os.path.join(self.share_path, filename)
		if not (os.path.exists(file_path) and os.path.isfile(file_path) and not os.path.islink(file_path)):
			return False
		if not filename:
			return False
		if filename[0] == ".":
			return False
		self.handler.send_response(200)
		content_type = mimetypes.guess_type(filename)[0]
		if content_type:
			self.handler.send_header('Content-Type', content_type)
		self.handler.end_headers()
		f = open(file_path, "rb")
		content = "".join(f.readlines())
		f.close()
		self.handler.wfile.write(content)
		self.handler.wfile.close()
		return True

	def serve(self):
		if None != re.search("hosting-cocosting/?$", self.handler.path):
			self.handler.send_response(200)
			self.handler.send_header('Content-Type', "text/html")
			self.handler.end_headers()
			self.handler.wfile.write(self.create_file_list_page())
			self.handler.wfile.close()
			return True
		elif None != re.search("hosting-cocosting/[^/]*$", self.handler.path):
			requested_file = self.get_requested_file_name()
			available_files = self.get_files_list()
			if requested_file not in available_files:
				return False
			else:
				return self.serve_file(requested_file)
		else:
			return False
