import socket
import os
import struct
import subprocess
import argparse
import time
from threading import Thread
BUFFER_SIZE = 65


class VideoThread(Thread):
	def __init__(self, sc, sock_name):
		self.sc = sc
		self.sock_name = sock_name
		Thread.__init__(self)
	
	def run(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		videos_dir = os.path.join(dir_path, 'videos')
		files = [f for f in os.listdir(videos_dir)]
		no_files = len(files)
		self.sc.send(str(no_files).encode('ascii'))
		self.sc.recv(BUFFER_SIZE)
		for file in files:
			self.sc.send(file.encode('ascii'))
			self.sc.recv(BUFFER_SIZE)
		file_name = self.sc.recv(BUFFER_SIZE).decode('ascii')
		video_path = os.path.join(videos_dir, file_name)
		time.sleep(3)
		subprocess.call(['ffmpeg', '-i', video_path, '-f', 'rtsp', '-rtsp_transport', 'tcp',
						 'rtsp://' + self.sock_name[0] + ':6633/live.sdp'])


def recv_all(sock, length):
	data = b''
	while len(data) < length:
		more = sock.recv(length - len(data))
		if not more:
			raise EOFError('was expecting %d bytes but only received %d bytes before the socket closed' % (length, len(data)))
		data += more
	return data


def server(interface, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind((interface, port))
	sock.listen(5)
	print("Server is listening at ", sock.getsockname())
	while True:
		sc, sock_name = sock.accept()
		print('We have accepted a connection from', sock_name)
		VideoThread(sc, sock_name).run()
		
		
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Send and receive over TCP')
	parser.add_argument('host', help='interface the server listens at host the client sends to')
	parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')
	args = parser.parse_args()
	server(args.host, args.p)
