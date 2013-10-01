
import socket

LOGIN = 'neo-210@yandex.ru'
PASSW = 'b65bc519105b'
HOST_SERVER_ID = 5

HOST = 'node%(id)s.net2ftp.ru' % { 'id' : HOST_SERVER_ID }
PORT = 21

BUFF_SIZE = 1024

if __name__ == '__main__':
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    
    data = client_socket.recv(BUFF_SIZE)
    print data
    
    request = 'USER ' + LOGIN
    print request
    client_socket.send(request)

    #data = client_socket.recv(BUFF_SIZE)
    #print data
    
    request = 'PASS ' + PASSW
    print request
    client_socket.send(request)
    
    #data = client_socket.recv(BUFF_SIZE)
    #print data
    
    client_socket.close()
    