
import socket
import time
import getpass

LOGIN = 'neo-210@yandex.ru'
PASSW = 'b65bc519105b'
HOST_SERVER_ID = 6

HOST = 'node%(id)s.net2ftp.ru' % { 'id' : HOST_SERVER_ID }
PORT = 21

BUFF_SIZE = 2048

responsehash = { 'USER' : [331],
                 'PASS' : [230],
                 'CONN' : [220],
                 'PWD'  : [257],
                 'CWD'  : [250],
                 'RMD'  : [250],
                 'MKD'  : [257],
                 'LIST' : [150,226],
                 'RETR' : [150,226],
                 'STOR' : [150,226],
                 'PASV' : [227],
                 'QUIT' : [221],
                 'DELE' : [250]
               }

help = '''
###########################
# command  | params
#--------------------------
# login    | loging, passw
# logout   |
# cd       | direcotry
# ls       |
# upload   | filename
# download | filename
# mkdir    | directory
# pwd      | 
# rmd      | directory
# rm       | filename
# connect  | host, port
############################
'''
               
def recv_timeout(s,timeout=2):
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

def recv_file(s,filename,timeout=1):
    s.setblocking(0)
    somedatarecved=False;data='';begin=time.time()
    f = open(filename, 'wb')
    while True:
        if somedatarecved and time.time()-begin>timeout:
            break
        elif time.time()-begin>timeout*2:
            break
        try:
            data=s.recv(BUFF_SIZE)
            if data:
                somedatarecved = True
                f.write(data)
                f.flush()
                begin=time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    f.close()

def request(s, message):
    request = message + '\r\n'
    #print request
    s.send(request)
    
    response = recv_timeout(s)
    #print response
    return response

def open_socket(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def open_child_socket(s):
    response = request(s, 'PASV')
    if not process_response(response, 'PASV'):
        return None
    
    iptext = response.split(' ')[4].replace('(', '').replace(')','').split(',')
    host = '%(1)s.%(2)s.%(3)s.%(4)s' % { '1' : iptext[0], '2' : iptext[1], '3' : iptext[2], '4' : iptext[3] }
    port = int(iptext[4]) * 256 + int(iptext[5])

    return open_socket(host, port)

def process_response(response, command):
    if response == '':
        return False
    isValid = True
    for a in response.splitlines():
        if int(response[0:3]) not in responsehash[command]:
            isValid = False
            break
    return isValid
    
def ls(s):
    file_socket = open_child_socket(s)
    if file_socket == None:
        print 'Operation failed'
        return False

    if not process_response(request(s, 'LIST'), 'LIST'):
        print 'Operation failed'
        return False
    
    print recv_timeout(file_socket)

    file_socket.close()

def login(s, user, passw):
    if not process_response(request(s, 'USER ' + user), 'USER'):
        print 'Invalid user'
        return False
    if not process_response(request(s, 'PASS ' + passw), 'PASS'):
        print 'Invalid password'
        return False
    print 'Successfully logged in'
    return True

def logout(s):
    ret = True
    if not process_response(request(s, 'QUIT'), 'QUIT'):
        print 'Quit operation falied'
        ret = False
    s.close()
    print 'Successfully logged out'
    return ret

def cd(s, path):
    if not process_response(request(s, 'CWD ' + path), 'CWD'):
        print "Can't change directory to " + path
        return False
    print 'Ok'
    return True
        
def pwd(s):
    response = request(s, 'PWD')
    if not process_response(response, 'PWD'):
        print 'Operation failed'
        return False
    print response[4:]
    return True
    
def mkd(s, dir):
    if not process_response(request(s, 'MKD ' + dir), 'MKD'):
        print "Can't create a directory with such a name"
        return False
    print 'Ok'
    return True
    
def rmd(s, dir):
    if not process_response(request(s, 'RMD ' + dir), 'RMD'):
        print "Can't remove a directory with such a name"
        return False
    print 'Ok'
    return True        
    
def upload(s, filename):
    file_stream = open_child_socket(s)
    if file_stream == None:
        print 'Operation failed'
        return False
    
    if not process_response(request(s, 'STOR ' + filename), 'STOR'):
        print "Can't upload file to ftp"
        return False
    
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
    print 'Ok'
    return True

def download(s, filename):
    file_stream = open_child_socket(s)
    if file_stream == None:
        print 'Operation failed'
        return False
        
    if not process_response(request(s, 'RETR ' + filename), 'RETR'):
        print "Can't download file from ftp"
        return False
    
    recv_file(file_stream, filename+"_")
    file_stream.close()
    print recv_timeout(s)
    print 'Ok'
    return True
    
def rm(s, filename):
    if not process_response(request(s, 'DELE ' + filename), 'DELE'):
        print "Can't remove a file with such a name"
        return False
    print 'Ok'
    return True
    
def connect(host, port):
    client_socket = open_socket(HOST, PORT)
    
    if not process_response(recv_timeout(client_socket), 'CONN'):
        print "Can't connect to the server " + HOST + ':' + str(PORT)
        client_socket = None
    else:
        print 'Succesefully connected to the server ' + HOST + ':' + str(PORT)
        print 'Login is required'

    return client_socket

if __name__ == '__main__':

    client_socket = None
   
    while True:
        args = str(raw_input()).split(' ')
        command = args[0]
        
        if command == 'connect':
            if args == 3:
                host = args[1]
                port = int(args[2])
                client_socket = connect(host, port)
            else:
                client_socket = connect(HOST, PORT)
            continue
                
        if client_socket == None:
            print 'First connect to the server'
            continue
        
        if command == 'login':
            user = str(raw_input('User: '))
            passw = getpass.getpass()
            if user == '':
                login(client_socket, LOGIN, PASSW)
            else:
                login(client_socket, user, passw)
        elif command == 'pwd':
            pwd(client_socket)
        elif command == 'cd':
            cd(client_socket, args[1])
        elif command == 'ls':
            ls(client_socket)
        elif command == 'mkdir':
            mkd(client_socket, args[1])
        elif command == 'rm':
            rm(client_socket, args[1])
        elif command == 'rmd':
            rmd(client_socket, args[1])
        elif command == 'upload':
            upload(client_socket, args[1])
        elif command == 'download':
            download(client_socket, args[1])
        elif command == 'logout':
            logout(client_socket)
            exit()
        elif command == 'help':
            print help
        else:
            print 'Invalid operation, see help'
