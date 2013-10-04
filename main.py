
import socket
import time

LOGIN = 'neo-210@yandex.ru'
PASSW = 'b65bc519105b'
HOST_SERVER_ID = 6

HOST = 'node%(id)s.net2ftp.ru' % { 'id' : HOST_SERVER_ID }
PORT = 21

BUFF_SIZE = 1024

def recv_timeout(s,timeout=2):
    s.setblocking(0)
    total_data=[];data='';begin=time.time()
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        try:
            data=s.recv(BUFF_SIZE)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.05)
        except:
            pass
    return ''.join(total_data)

def request(s, message):
    request = message + '\r\n'
    print request
    s.send(request)
    
    response = recv_timeout(s)
    print response
    return response

def open_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def open_child_socket(s):
    response = request(s, "PASV")

    iptext = response.split(' ')[4].replace('(', '').replace(')','').split(',')
    host = '%(1)s.%(2)s.%(3)s.%(4)s' % { '1' : iptext[0], '2' : iptext[1], '3' : iptext[2], '4' : iptext[3] }
    port = int(iptext[4]) * 256 + int(iptext[5])

    return open_socket(host, port)

def ls(s):
    file_socket = open_child_socket(s)

    request(s, "LIST")

    print recv_timeout(file_socket)

    file_socket.close()

def login(s, user, passw):
    request(s, 'USER ' + user)
    request(s, 'PASS ' + passw)

def logout(s):
    request(s, 'QUIT')
    s.close()

def cd(s, path):
    request(s, 'CWD ' + path)

def pwd(s):
    request(s, 'PWD')

def upload(s, filename):
    pass

def download(s, filename):
    pass

###########################
# commands to implement ###
###########################
# command  | params
#--------------------------
# login    | loging, passw
# logout   |
# cd       | direcotry
# ls       |
# upload   | filename
# download | filename
############################

#############################
# to do list
#############################
# - response code validation
# - file up/down-loading
# - threading
#############################

if __name__ == '__main__':
    client_socket = open_socket(HOST, PORT)

    print recv_timeout(client_socket)
    
    login(client_socket, LOGIN, PASSW)
    pwd(client_socket)
    ls(client_socket)
    cd(client_socket, './asd')
    logout(client_socket)
