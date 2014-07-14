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
		self.file_read_chunk_size = 2**30

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

	def serve_whole_file(self, file_path):
		self.handler.send_response(200)
		content_type = mimetypes.guess_type(file_path)[0]
		if content_type:
			self.handler.send_header('Content-Type', content_type)
		self.handler.send_header('Content-Length', os.path.getsize(file_path))
		self.handler.send_header('Date', self.handler.get_current_timestamp())
		self.handler.end_headers()
		f = open(file_path, "rb")
		while True:
			data = f.read(self.file_read_chunk_size)
			if not data:
				break
			self.handler.wfile.write(data)
		f.close()
		self.handler.wfile.close()
		return True

	def serve_part_of_file(self, file_path, start, stop):
		file_size = os.path.getsize(file_path)
		response_size = stop - start + 1
		self.handler.send_response(206) #Partial content
		content_type = mimetypes.guess_type(file_path)[0]
		if content_type:
			self.handler.send_header('Content-Type', content_type)
		self.handler.send_header('Content-Length', response_size)
		self.handler.send_header('Date', self.handler.get_current_timestamp())
		self.handler.send_header('Content-Range', "bytes %d-%d/%d" % (start, stop, file_size) )
		self.handler.end_headers()
		f = open(file_path, "rb")
		f.seek(start)
		n_chunks = response_size / self.file_read_chunk_size
		for _ in xrange(n_chunks):
			data = f.read(self.file_read_chunk_size)
			if not data:
				f.close()
				self.handler.wfile.close()
				return True
			else:
				self.handler.wfile.write(data)
		remaining = response_size % self.file_read_chunk_size
		data = f.read(remaining)
		if data:
			self.handler.wfile.write(data)
		f.close()
		self.handler.wfile.close()
		return True


	def serve_file(self, filename):
		file_range = self.handler.headers.getheader("Range") 
		file_path = os.path.join(self.share_path, filename)
		if not (os.path.exists(file_path) and os.path.isfile(file_path) and not os.path.islink(file_path)):
			return False
		if not filename:
			return False
		if filename[0] == ".":
			return False

		if not file_range:
			return self.serve_whole_file(file_path)
		else: #range: bytes=22164992- <type 'str'>
			#Content-Range = "Content-Range" ":" content-range-spec

			#content-range-spec      = byte-content-range-spec
			#byte-content-range-spec = bytes-unit SP
				#byte-range-resp-spec "/"
				#( instance-length | "*" )

				#byte-range-resp-spec = (first-byte-pos "-" last-byte-pos)
					#| "*"
				#instance-length           = 1*DIGIT

			split_by_bytes = file_range.split("bytes=")
			if len(split_by_bytes) != 2:
				return self.serve_whole_file(file_path)
			range_part = split_by_bytes[1]
			start_stop = range_part.split("-")
			if not start_stop[0]:
				start = 0
			else:
				start = int(start_stop[0])
			if not start_stop[1].split('/')[0]:
				stop = os.path.getsize(file_path) - 1
			else:
				stop = int(start_stop[1].split('/')[0])
			if start < 0:
				self.handler.send_response(416) # Requested Range Not Satisfiable
				self.handler.wfile.close()
				return True
			if stop > os.path.getsize(file_path) - 1:
				self.handler.send_response(416) # Requested Range Not Satisfiable
				self.handler.wfile.close()
				return True
			return self.serve_part_of_file(file_path, start, stop)


	def serve(self):
		if None != re.search("hosting-cocosting/?$", self.handler.path):	
			page = self.create_file_list_page()
			self.handler.send_response(200)
			self.handler.send_header('Content-Type', "text/html")
			self.handler.send_header('Date', self.handler.get_current_timestamp())
			self.handler.send_header('Content-Length', len(page))
			self.handler.end_headers()
			self.handler.wfile.write(page)
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
