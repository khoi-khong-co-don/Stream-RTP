import socket

from ServerWorker import ServerWorker
import multiprocessing


class Server:

	def main(self):
		# try:
		# 	SERVER_PORT = 2024
		# except:
		# 	print ("[Usage: Server.py Server_port]\n")
		# rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# rtspSocket.bind(('', SERVER_PORT))
		# print ("RTSP Listing incoming request...")
		# rtspSocket.listen(5)

		# # Receive client info (address,port) through RTSP/TCP session
		# while True:
		# 	clientInfo = {}
		# 	clientInfo['rtspSocket'] = rtspSocket.accept()   # this accept {SockID,tuple object},tuple object = {clinet_addr,intNum}!!!
		# 	print(clientInfo['rtspSocket'])
		# 	print(clientInfo['rtspSocket'][0])
		# 	ServerWorker(clientInfo).run()

		
		print ("RTSP Listing incoming request...")

		# Receive client info (address,port) through RTSP/TCP session
			# clientInfo['rtspSocket'] = rtspSocket.accept()   # this accept {SockID,tuple object},tuple object = {clinet_addr,intNum}!!!
		for i in range(4):

			clientInfo= {}
			clientInfo['portRTP'] = 12345 + i
			device = ServerWorker(clientInfo)
			process_live = multiprocessing.Process(target=device.run)
			process_live.start()

# Program Start Point
if __name__ == "__main__":
	(Server()).main()