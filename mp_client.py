import socket
from progmp import ProgMP
import subprocess
import argparse

BUFFER_SIZE = 4000


def recv_all(sock, length):
	data = b''
	while len(data) < length:
		more = sock.recv(length - len(data))
		if not more:
			raise EOFError(
				'was expecting %d bytes but only received %d bytes before the socket closed' % (length, len(data)))
		data += more
	return data


def recv_until(sock, length, char_sequence):
	data = ''
	flag = False
	for suff in char_sequence:
		if data.endswith(suff):
			flag = True
	while not flag:
		data += sock.recv(4)
	return data


def client(interface, port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((interface, port))
	scheduler_name = "illustratingMinRTT"
	with open("illustratingMinRtt.progmp", "r") as src:
		sched_prog_str = src.read()
	try:
		ProgMP.loadScheduler(sched_prog_str)
	except:
		print("Scheduler loading error.")
	
	try:
		ProgMP.setScheduler(sock, scheduler_name)
	except:
		print("Scheduler not found, maybe no MPTCP ?")
	
	ProgMP.setUser(sock, 2)
	ProgMP.setRegister(sock, ProgMP.R1(), 5)
	print('Connected to video server please wait 3 seconds after selecting file to play video :), Enjoy!!')
	no_of_files = int(sock.recv(12).decode('ascii'))
	file_names = []
	sock.send('No of files received'.encode('ascii'))
	for i in range(no_of_files):
		# name = recv_all(sock, BUFFER_SIZE).decode('ascii')
		name = sock.recv(BUFFER_SIZE).decode('ascii')
		# name = sock.recv_until(sock, BUFFER_SIZE, ['.avi', '.mkv', '.mp4']).decode('ascii')
		sock.send('acknowledge'.encode('ascii'))
		file_names.append(name)
		print("{}: {}".format(i + 1, name))
	index = int(input('Enter the selected index to choose the file: '))
	sock.send(file_names[index - 1].encode('ascii'))
	subprocess.call(['ffplay', '-rtsp_flags', 'listen', 'rtsp://0.0.0.0:6633/live.sdp?tcp'])
	ProgMP.removeScheduler(scheduler_name)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Send and receive over TCP')
	parser.add_argument('host', help='interface the server listens at host the client sends to')
	parser.add_argument('-p', metavar='PORT', type=int, default=1060, help='TCP port (default 1060)')
	args = parser.parse_args()
	client(args.host, args.p)
