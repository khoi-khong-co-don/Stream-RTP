
import random, math
import time
from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket


class ServerWorker:
	SETUP = 'SETUP'
	PLAY = 'PLAY'
	PAUSE = 'PAUSE'
	TEARDOWN = 'TEARDOWN'

	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT

	OK_200 = 0
	FILE_NOT_FOUND_404 = 1
	CON_ERR_500 = 2

	clientInfo = {}

	IPP2P = ""
	PORTP2P = 0

	HOST = '192.168.111.93'
	# HOST = '192.168.43.25'

	PORT = 12345

	
	def __init__(self, clientInfo):
		self.clientInfo = clientInfo	


	def run(self):
		threading.Thread(target=self.recvRtspRequest).start()

	def recvRtspRequest(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.HOST, self.PORT))
		self.sock.sendto(b'lo', ('103.151.241.66',55555))
		print("Day la Client A")
		data, addr = self.sock.recvfrom(1024)
		print(data, addr)
		data_str = data.decode('utf-8')
		data_list = eval(data_str)
		self.IPP2P, self.PORTP2P = data_list[0], data_list[1]
		print("Dia chi cua Client B la: ", self.IPP2P, self.PORTP2P)
		while True:
			self.sock.sendto(b'connect', (self.IPP2P, self.PORTP2P))
			data1, addr1 = self.sock.recvfrom(1024)
			data1 = data1.decode('utf-8')
			if data1.find('turn')>=0:
				break
			if data1.find('ok')>=0:
				print("Do break")
				break
			self.sock.sendto(b'connect', (self.IPP2P, self.PORTP2P))
		print("Da Break")
		
		########## TIEN HANH DUNG TURN ####################

		data_turn, addr_turn = self.sock.recvfrom(1024)
		print(data_turn, addr_turn)
		data_turn_str = data_turn.decode('utf-8')

		data_list_turn = eval(data_turn_str)

		ip_turn, port_turn = data_list_turn[0], data_list_turn[1]
		self.sock.sendto(b'server connect turn', (ip_turn, port_turn))
		############################################################
		data_turn_recv, addr_turn_recv = self.sock.recvfrom(1024)
		print(data_turn_recv, addr_turn_recv)
		data_turn_recv_str = data_turn_recv.decode('utf-8')

		data_list_recv_turn = eval(data_turn_recv_str)

		ip_turn_recv, port_turn_recv = data_list_recv_turn[0], data_list_recv_turn[1]
		self.sock.sendto(b'server connect to recv', (ip_turn_recv, port_turn_recv))
		temp = 0
		while True:
			data_turn_recv, addr_turn_recv = self.sock.recvfrom(1024)
			data_turn_recv_str = data_turn_recv.decode('utf-8')
			if data_turn_recv_str.find('connected') >= 0:
				temp = temp + 1
				if temp == 2:
					while True:
						self.sock.sendto(b't la server', (ip_turn, port_turn))
						data, addr = self.sock.recvfrom(1024)
						print(data, addr)
						print("turn server")
						data_str = data.decode('utf-8')
						if data_str == 'close':
							break

	def processRtspRequest(self, data):
		"""Process RTSP request sent from the client."""
		# Get the request type
		data_str = data.decode('utf-8')
		request = data_str.split('\n')
		
		line1 = request[0].split(' ')
		requestType = line1[0]
		# Get the media file name
		filename = line1[1]
		# Get the RTSP sequence number
		seq = request[1].split(' ')

		# Process SETUP request
		if requestType == self.SETUP:
			if self.state == self.INIT:
				# Update state
				print ("SETUP Request received\n")

				try:

					self.clientInfo['videoStream'] = VideoStream(filename)
					self.state = self.READY

				except IOError:
					self.replyRtsp(self.FILE_NOT_FOUND_404, seq[1])

				# Generate a randomized RTSP session ID
				self.clientInfo['session'] = randint(100000, 999999)

				# Send RTSP reply
				self.replyRtsp(self.OK_200, seq[0])  #seq[0] the sequenceNum received from Client.py
				print ("sequenceNum is " + seq[0])
				# Get the RTP/UDP port from the last line
				self.clientInfo['rtpPort'] = request[2].split(' ')[3]
				print ('-'*60 + "\nrtpPort is :" + self.clientInfo['rtpPort'] + "\n" + '-'*60)
				print ("filename is " + filename)

		# Process PLAY request
		elif requestType == self.PLAY:
			if self.state == self.READY:
				print ('-'*60 + "\nPLAY Request Received\n" + '-'*60)
				self.state = self.PLAYING

				# Create a new socket for RTP/UDP

				self.replyRtsp(self.OK_200, seq[0])
				print ('-'*60 + "\nSequence Number ("+ seq[0] + ")\nReplied to client\n" + '-'*60)

				# Create a new thread and start sending RTP packets
				self.clientInfo['event'] = threading.Event()
				self.clientInfo['worker']= threading.Thread(target=self.sendRtp)
				self.clientInfo['worker'].start()
                
		# Process RESUME request
			elif self.state == self.PAUSE:
				print ('-'*60 + "\nRESUME Request Received\n" + '-'*60)
				self.state = self.PLAYING

		# Process PAUSE request
		elif requestType == self.PAUSE:
			if self.state == self.PLAYING:
				print ('-'*60 + "\nPAUSE Request Received\n" + '-'*60)
				self.state = self.READY

				self.clientInfo['event'].set()

				self.replyRtsp(self.OK_200, seq[0])

		# Process TEARDOWN request
		elif requestType == self.TEARDOWN:
			print ('-'*60 + "\nTEARDOWN Request Received\n" + '-'*60)

			self.clientInfo['event'].set()

			self.replyRtsp(self.OK_200, seq[0])

			# Close the RTP socket
			# comment tam
			# self.clientInfo['rtpSocket'].close()

	def sendRtp(self):
		"""Send RTP packets over UDP."""
		counter = 0
		threshold = 10
		while True:
			# jit = math.floor(random.uniform(-13,5.99))
			# jit = jit / 1000
			#
			# self.clientInfo['event'].wait(0.05 + jit)
			# jit = jit + 0.020

			# Stop sending if request is PAUSE or TEARDOWN
			if self.clientInfo['event'].isSet():
				break

			data = self.clientInfo['videoStream'].nextFrame()
			#print '-'*60 + "\ndata from nextFrame():\n" + data + "\n"
			if data:
				frameNumber = self.clientInfo['videoStream'].frameNbr()
				try:

					port = int(self.clientInfo['rtpPort'])
					prb = math.floor(random.uniform(1,100))
					if prb > 5.0:
						#self.clientInfo['rtspSocket'][1][0]
						send_large_data_via_udp(self.makeRtp(data, frameNumber), self.sock, (self.IPP2P, self.PORTP2P))
						# self.clientInfo['rtpSocket'].sendto(self.makeRtp(data, frameNumber),("192.168.111.65",port))
						counter += 1
						# time.sleep(jit)
				except:
					print ("Connection Error")
					print ('-'*60)
					traceback.print_exc(file=sys.stdout)
					print ('-'*60)

	def makeRtp(self, payload, frameNbr):
		"""RTP-packetize the video data."""
		version = 2
		padding = 0
		extension = 0
		cc = 0
		marker = 0
		pt = 26 # MJPEG type
		seqnum = frameNbr
		ssrc = 0

		rtpPacket = RtpPacket()

		rtpPacket.encode(version, padding, extension, cc, seqnum, marker, pt, ssrc, payload)

		return rtpPacket.getPacket()

	def replyRtsp(self, code, seq):
		"""Send RTSP reply to the client."""
		if code == self.OK_200:
			#print "200 OK"
			reply = "RTSP/1.0 200 OK\nCSeq: " + seq + "\nSession: " + str(self.clientInfo["session"])
			# connSocket = self.clientInfo["rtspSocket"][0]
			# reply_bytes = reply.encode('utf-8')
			# connSocket.send(reply_bytes)

		# Error messages
		elif code == self.FILE_NOT_FOUND_404:
			print ("404 NOT FOUND")
		elif code == self.CON_ERR_500:
			print ("500 CONNECTION ERROR")


def send_large_data_via_udp(data, udp_socket, remote_address, max_packet_size=60000):
    data_length = len(data)
    print("data_length: " + str(data_length))
    for i in range(0, data_length, max_packet_size):
        chunk = data[i:i + max_packet_size]
        udp_socket.sendto(chunk, remote_address)
        data3, addr3 = udp_socket.sendto(chunk, remote_address)