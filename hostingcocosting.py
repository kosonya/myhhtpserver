#!/usr/bin/env python
#-*- coding:utf8 -*-

import os
import os.path
import re

class HostingCocosting(object):
	def __init__(self, http_request_handler):
		self.handler = http_request_handler
		self.share_path = "/mnt/data/Public"

	def get_files_list(self):
		return [ f for f in os.listdir(self.share_path) if os.path.isfile(os.path.join(self.share_path,f)) and not os.path.islink(os.path.join(self.share_path,f))]

	def get_requested_file_name(self):
		name = self.handler.path.split('/')[-1]
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
			for filename in files_list:
				page += "\t\t\t<li><a href=\"%s\">%s</a></li>\n" % (filename, filename)
			page += "\t\t</ul>\n"

		page += "\t</body>\n"
		page += "</html>"
		return page

	def serve(self):
		if None != re.search("hosting-cocosting/?$", self.handler.path):
			self.handler.send_response(200)
			self.handler.send_header('Content-Type', "text/html")
			self.handler.end_headers()
			self.handler.wfile.write(self.create_file_list_page())
			self.handler.wfile.close()
			return True
		else:
			return False
