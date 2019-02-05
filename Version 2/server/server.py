import socket
import os
import sys
import msvcrt
from tinydb import TinyDB, Query
from datetime import datetime as dt
import time
import select
import threading

# basic parameters
usersdb = TinyDB('users.json',default_table="users")
ip     = socket.gethostbyname(socket.gethostname())
address   = 20000
bufferSize  = 65000
blocking_mode = False # This flag is to block the server while recieve a file from the client
file_to_upload = None # file object to be opened when uploading from the client.
active_clients = dict()
threads = dict()

def create_socket(timeout_period = 10, ip=ip, port= address):
    # Create a datagram socket
    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Bind to address and ip
    soc.bind((ip, port))
    #set time out on the socket
    soc.settimeout(timeout_period)
    # Declare success and some notes
    print("UDP server up and listening")
    print("press \'esc\' to terminate the server.")
    print("Note that The server might take some time 'up to 10 sec' to terminate after hitting esc")
    return soc

def send_to_client(soc, client_address, msg):
    soc.sendto(str.encode(msg), client_address)


def create_new_user(msg, soc, client_address, users):
    username = str(msg.split("|")[1])
    password = str(msg.split("|")[2])
    if len(usersdb.search(users.name==username))==0:
        usersdb.insert({'name':username, 'password':password, 'creation time':str(dt.now()), 'login log':[], 'download log':[], 'upload log':[]})
        send_to_client(soc, client_address, '1')
    else:
        send_to_client(soc, client_address, '0')


def login_user(msg, soc, client_address, users):
    global active_clients
    username = str(msg.split("|")[1])
    password = str(msg.split("|")[2])
    query = usersdb.search(users.name==username) 
    if len(query) == 0:
        send_to_client(soc, client_address, '-1')
    else:
        if query[0]['password'] == password:
            usersdb.update({"login log":query[0]["login log"]+[str(dt.now())]}, users.name==username)
            send_to_client(soc, client_address, '1')
            active_clients[client_address]=username
        else:
            send_to_client(soc, client_address, '0')


def download_file(msg, client_address, users, soc):
    filename = str(msg.split("|")[1])
    username = active_clients[client_address]
    query = usersdb.search(users.name==username) 
    if filename in os.listdir("files"):
        send_to_client(soc, client_address, "1")
        f = open(os.path.join("files",filename), "rb")
        data = f.read(bufferSize)
        while data:
            soc.sendto(data, client_address)
            data = f.read(bufferSize)
            time.sleep(0.1) # to not overwhelm the reviever
        # Update download log
        usersdb.update({"download log":query[0]["download log"]+[str(dt.now())]}, users.name==username)

def edit_account(msg, users, soc, client_address):
    new_username = str(msg.split("|")[1])
    new_password = str(msg.split("|")[2])
    if len(usersdb.search(users.name==new_username))>0:
        send_to_client(soc, client_address, "0")
    else:
        usersdb.update({'name':new_username, 'password':new_password}, users.name == active_clients[client_address])
        active_clients[client_address] = new_username
        send_to_client(soc, client_address, '1')

def file_search(msg, soc, client_address):
    filename = str(msg.split("|")[1])
    if filename in os.listdir('files'):
        send_to_client(soc, client_address, '1')
    else:
        send_to_client(soc, client_address, '0')
    return 

def retrieve_stats(msg, users, client_address, soc):
    options = int(str(msg.split("|")[1]))
    current_user = usersdb.search(users.name==active_clients[client_address])[0]
    if int(options) == 0:
        logs = list()
        logs.append(current_user['creation time'])
        logs.append(current_user['login log'])
        logs.append(current_user['download log'])
        logs.append(current_user['upload log'])
        send_to_client(soc, client_address, str(logs))
    elif int(options) == 1:
        send_to_client(soc, client_address, str(current_user['creation time']))
    elif int(options) == 2:
        send_to_client(soc, client_address, str(current_user['login log']))
    elif int(options) == 3:
        send_to_client(soc, client_address, str(current_user['download log']))
    elif int(options) == 4:
        send_to_client(soc, client_address, str(current_user['upload log']))

def logout_user(client_address, soc):
    try:
        del active_clients[client_address]
        send_to_client(soc, client_address, '1')
    except KeyError as k:
        print(k)
        print("A cleint asks for logout. He might be registered before the server reboot. No operation will be tuckled.")
        send_to_client(soc, client_address, '0')

def get_file_from_client(file_to_upload, data, client_address):
    global blocking_mode
    file_to_upload.write(data[0])
    users = Query()
    query = usersdb.search(users.name==active_clients[client_address]) 
    usersdb.update({"upload log":query[0]["upload log"]+[str(dt.now())]}, users.name==active_clients[client_address])
    file_to_upload.close()
    blocking_mode = False
    print("file revieved from "+ str(data[1]))
    return

def process_upload_file_parameters(msg, soc, client_address):
    global blocking_mode
    global file_to_upload
    if not blocking_mode:
        filename = str(msg.split("|")[1])
        if filename in os.listdir('files'):
            send_to_client(soc, client_address, "0")
        else:
            send_to_client(soc, client_address, "1")
            file_to_upload = open(os.path.join('files',filename), 'wb')
            blocking_mode = True
    return

def process_message(data, soc, client_address):
    # some parameter
    global blocking_mode
    global file_to_upload
    if blocking_mode == False:
        msg = (data[0]).decode('utf-8')
        flag = int(msg.split("|")[0])
        users = Query()

        if flag == 0:
            # create new  user
           create_new_user(msg, soc, client_address, users)
                                
        elif flag == 1:
            # login user
            login_user(msg, soc, client_address, users)
            
        elif flag == 2:
            # list files in the system
            send_to_client(soc, client_address, str(os.listdir("files")))

        elif flag == 3:
            # download a file to the client
            download_file(msg, client_address, users, soc)                

        elif flag == 4:
            # upload a file from the client, initial logic
            process_upload_file_parameters(msg, soc, client_address)

        elif flag == 5:
            # doing file search
            return file_search(msg, soc, client_address) 

        elif flag == 6:
            # edit account
            edit_account(msg, users, soc, client_address)
            
        elif flag == 7:
            # retireve stats to the client
            retrieve_stats(msg, users, client_address, soc)
        elif flag == 8:
            # logout
            logout_user(client_address, soc)
        else:
            send_to_client(soc, client_address, '-1')
    else:
        # get file from the client
        return get_file_from_client(file_to_upload, data, client_address)



# Listen for connections
def listen_for_connections(soc):
    # Listen for incoming datagrams if the server mode is not blocking
    client_address = None
    while True:
        try:
            msg = soc.recvfrom(bufferSize)
            print(str(msg[1])+" sends a message.")
            # print(str(msg[0]))   # debug
            client_address = msg[1]
            threading.Thread(target=process_message, args=(msg, soc,client_address), name=str(client_address)).start()
            
        except socket.timeout:
            print("No message during the past 10 seconds. There is(are) "+str(len(active_clients))+" active client(s).")
        # exit on esc press
        if msvcrt.kbhit():
            if ord(msvcrt.getch()) == 27: # exit button
                if len(active_clients) == 0:
                    break
                else:
                    print("there are some connections to come clients.")
                    print("The server cannot terminate until all connections are closed.")

# Main Function
try:
    soc = create_socket(10)
    listen_for_connections(soc)
except KeyboardInterrupt:
    print("Forced to terminate. The program will shutdown eventhough there is some active connections with some clients.")
    sys.exit()
