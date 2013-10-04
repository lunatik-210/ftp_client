
import socket
import time

LOGIN = 'neo-210@yandex.ru'
PASSW = 'b65bc519105b'
HOST_SERVER_ID = 6

HOST = 'node%(id)s.net2ftp.ru' % { 'id' : HOST_SERVER_ID }
PORT = 21

BUFF_SIZE = 2048

def recv_timeout(s,timeout=1):
    s.setblocking(0)
    total_data=[];data='';begin=time.time()
    while True:
        if total_data and time.time()-begin>timeout:
            break
        elif time.time()-begin>timeout*2:
            break
        try:
            data=s.recv(BUFF_SIZE)
            if data:
                total_data.append(data)
                begin=time.time()
            else:
                time.sleep(0.1)
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
    
def mkd(s, dir):
    request(s, 'MKD ' + dir)
    
def rmd(s, dir):
    request(s, 'RMD ' + dir)
    
def upload(s, filename):
    file_stream = open_child_socket(s)
    request(s, 'STOR ' + filename)
    buffer = "hello"
    f = open(filename, 'rb')
    while True:
        buffer = f.read(BUFF_SIZE)
        if buffer == "":
            break
        file_stream.send(buffer)
    f.close()
    file_stream.close()
    print recv_timeout(s)

def download(s, filename):
    file_stream = open_child_socket(s)
    request(s, 'RETR ' + filename)
    data = recv_timeout(file_stream)
    file_stream.close()
    print recv_timeout(s)
    return data
    
def rm(s, filename):
    request(s, 'DELE ' + filename)

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
    upload(client_socket, "test.obj")
    print download(client_socket, "testfile2.txt")
    ls(client_socket)
    rm(client_socket, "test.obj")
    ls(client_socket)
    mkd(client_socket, "test")
    ls(client_socket)
    rmd(client_socket, "test")
    ls(client_socket)
    logout(client_socket)
