import socket
import pathlib
import select
import time
import os
import sys
import ntpath
import ast
import subprocess as sp
import ipaddress
import getpass
import traceback

# Connection parameters
server_address   = (socket.gethostbyname(socket.gethostname()), 20000)
bufferSize          = 65000

# user credintals
user_credintals = None

def create_socket(timeout_period = 10):
    # Create a UDP socket at client side
    soc = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    soc.settimeout(timeout_period)
    return soc

def send_to_server(msg, socket, server_address):
    socket.sendto(str.encode(msg), server_address)
    server_response = socket.recvfrom(bufferSize)
    return server_response[0].decode('utf-8')

def close_socket(socket):
    socket.close()

def list_files(soc):
    res = send_to_server("2", soc, server_address)
    if res != None:
        filenames =  [str(filename) for filename in res[1:-1].split(', ')]
        print("Current file(s) in the system:")
        for i in range(len(filenames)):
            print(str(i+1)+". "+filenames[i])
    elif res == '10':
        print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
    else:
        print("Problem with the server. Please try again later.")


def download_file(soc, filename):
    print("Please note that the file will be downloaded to the same directory where this program is located.")
    while True:
        res = send_to_server("3|"+filename, soc, server_address)
        if int(res) == 1:
            f = open(filename, 'wb')
            while True:
                ready = select.select([soc], [], [], 0.1) # the last argument is the timeout
                if ready[0]:
                    data = soc.recvfrom(bufferSize)
                    f.write(data[0])
                else:
                    print("Finish downloading the file.")
                    f.close()
                    return
        elif res == '10':
            print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
        else:
            print("The file is not in the server. Please try again. Enter \'|\' to go to the previous list.")
            filename = str(input())
            if filename == "|":
                return
                

def get_file_name(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def upload_file(soc, filepath):
    if not os.path.isfile(filepath):
        print("This is not a valid file name and path. Please try again.")
        return
    filename = get_file_name(filepath)
    res = send_to_server("4|"+filename, soc, server_address)
    if int(res) == 0:
        print("A file with the same name already exist on the server. Please change the name of your file and try again.")
    elif res == '10':
        print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
    elif int(res) == -1:
        print("A problem with the server occured. Please try later.")
    else:
        f = open(filepath,"rb")
        data = f.read(bufferSize)
        res = None
        while data:
            res = soc.sendto(data, server_address)
            data = f.read(bufferSize)
            time.sleep(0.1) # not to overwhelm the server
        print("The file is uploaded successfully")
    return

def file_search(soc, filename):
    res = send_to_server("5|"+filename, soc, server_address)
    if int(res) == 1:
        print("The file "+filename+" is in the server database.")
    elif int(res) == 0:
        print("The file "+filename+" is NOT in the server database.")
    elif res == '10':
        print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
    else:
        print("Error with the server. Please try again later.")


def validate_username():
    username = ""
    print("Please enter your user name refering to the following criteras:")
    while True:
        print("The user name shall be 2 chars at least.")
        print("The user name shall not contain the character \'|\' or space character")
        username = str(input("Please enter your user name:"))
        if len(username)>2 and '|' not in username and ' ' not in username:
            break
        else:    
            print("Not an appropriate user name. Please try again. Please note the following:")
    return username

def validate_password():
    password = ""
    print("Please enter your password refering to the following criteras:")
    while True:
        print("The password shall be 3 chars at least.")
        print("The user name shall not contain the character \'|\' or space character")
        password = str(getpass.getpass("Please choose your password (chars will not appear):"))
        if len(password)>=3 and '|' not in password and ' ' not in password:
            break
        else:    
            print("Not an appropriate password. Please try again. Please note the following:")
    return password


def administrate_account(soc, options, info):
    global user_credintals
    if options == 1:
        # update username and password
        print("Update command will update your username and passowrd. This is an administrative operation. Please provide your credintlats:")
        name = input("Enter your username:")
        while name != user_credintals[0]:
            name = input("Wrong username. Please try again:")
        pwrd = getpass.getpass("Enter your passowrd (chars will not appear):")
        while pwrd != user_credintals[1]:
            pwrd = input("Wrong password. Please try again:")
        while True:
            print("Please enter your new username and password:")
            new_name = validate_username()
            new_pwrd = validate_password()
            res = send_to_server("6|"+new_name+"|"+new_pwrd, soc, server_address)
            if int(res) == 1:
                print("Information is updated successfully.")
                user_credintals = (new_name, new_pwrd)
                break
            elif int(res) == 0:
                print("A user with the same name already exist. Please chose another name and try again.")
            elif res == '10':
                print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
            else:
                print("Problem with the server. Please try again")
                break

    elif options == 2:
        # retrive stats from the server
        if info == None:
            # retrive all logs
            res = send_to_server("7|0",soc, server_address)
            if res == '10':
                    print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
            else:
                res = ast.literal_eval(res)
                print("creation time:")
                print(res[0])
                print("login log:")
                for i in range(len(res[1])):
                    print(str(i+1)+". "+res[1][i])
                print("download log:")
                for i in range(len(res[2])):
                    print(str(i+1)+". "+res[2][i])
                print("upload log:")
                for i in range(len(res[3])):
                    print(str(i+1)+". "+res[3][i])
        else:
            if info == 'ctime':
                res = send_to_server("7|1",soc, server_address)
                if res == '10':
                    print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
                else:
                    print("creation time:")
                    print(res)
            elif info == 'llog':
                res = send_to_server("7|2",soc, server_address)
                if res == '10':
                    print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
                else:
                    print("login log:")
                    llog = ast.literal_eval(res)
                    for i in range(len(llog)):
                        print(str(i+1)+". "+llog[i])
            elif info == 'dlog':
                res = send_to_server("7|3",soc, server_address)
                if res == '10':
                    print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
                else:
                    print("download log:")
                    dlog = ast.literal_eval(res)
                    for i in range(len(dlog)):
                        print(str(i+1)+". "+dlog[i])
            elif info == 'ulog':
                res = send_to_server("7|4",soc, server_address)
                if res == '10':
                    print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
                else:
                    print("upload log:")
                    ulog = ast.literal_eval(res)
                    for i in range(len(ulog)):
                        print(str(i+1)+". "+ulog[i])
                


def login_user(soc):
    global user_credintals
    global server_address
    global bufferSize
    print("Client program for file sharing application. Enter \'help\' for more information.")
    print("Please login with your credintals.")
    while True:
        name = str(input("Please enter your user name:"))
        password = str(getpass.getpass("Please enter your password (chars will not appear):"))
        res = send_to_server("1|"+name+"|"+password, soc, server_address)
        if int(res) == 1:
            user_credintals = name,password
            while True:
                user_input = str(input(">"))
                choice = user_input.split(" ")[0]
                if choice == "ls":
                    list_files(soc)
                elif choice == "download":
                    download_file(soc, user_input.split(" ")[1])
                elif choice == "upload":
                    upload_file(soc, " ".join(user_input.split(" ")[1:]))
                elif choice == "search":
                    file_search(soc, user_input.split(" ")[1])
                elif choice == "update":
                    administrate_account(soc, 1, None)
                elif choice == "stats":
                    if len(user_input.split(" ")) == 1:
                        administrate_account(soc, 2, None)
                    else:
                        administrate_account(soc, 2, user_input.split(" ")[1])
                elif choice == "help":
                    print("Welcome to this command line client file sharing program. You can read the readme.RM file for more information on the structure of the program. Operations this program can support are:")
                    print("1. <ls> this command will list all files in the server repository.")
                    print("2. <download filename> this command will download the file from the server to the client. Please do not forget the extension of the file in the \"filename\".")
                    print("3. <upload filepath> this command will upload a file given its full directory and extension.")
                    print("4. <search filename> this command will search the server files repository for the given file name.")
                    print("5. <update> this command allows the user to update his account username and passowrd. Note that this is an administritive operation. Meaning that the user need to enter his credintials in order to update to the new ones.")
                    print("6. <stats [ctime, llog,dlog,ulog]> this command will show stats about the user activities on the server. Note that [ctime, llog, dlog, ulog] are optional. \'ctime\' shows the creation time. \'llog\' shows the login log. \'dlog\' shows the download log. \'ulog\' shows the upload log. If no optional paramter entered, the command will show all the logs.")
                    print("7. <help> To show this window again :)")
                    print("8. <cls> To to clear the window.")
                    print("9. <exit> To logout and terminate.")
                    # print("10. <serveraddress ip port buffersize> To change the default parameters of the server address. Note that this operation is VERY CRITICAL.")
                elif choice =='cls':
                    # to clear the screen
                    sp.call("cls",shell=True)
                elif choice == "exit":
                    res = send_to_server("8|",soc, server_address)
                    if int(res) == 1:
                        print("The program will logout. Thansk for using our service.")
                    elif int(res) == 0:
                        print("The server reboots while this client program was running. This will not defect any information you have put. The program will terminate safely.")
                    else:
                        print("There is a problem currently in the server.The program will terminate anyway.")
                    soc.close()
                    exit()
                else:
                    print("Unkown command. Enter \'help\' to get more information.")
            break
        elif int(res) == 0:
            print("Correct username but wrong password. Please try again. If you forgot your password, please enter")
        elif res == '10':
            print("The server is busy currently serving other clients in some critical opearions. Please try again.")
        elif int(res) == -1:
            print("This user name is not in the database. Please try again.")
        else:
            print("Unknown error with the server. Please try again.")


def create_user(soc):
    user_name = validate_username()
    passowrd = validate_password()
    server_response = send_to_server("0|"+user_name+"|"+passowrd, soc, server_address)
    if int(server_response) == 1:
        print("Your user account has been created successfully.")
        login_user(soc)
    elif int(server_response) == 0:
        print("Username already exist. Please login instead.")
        login_user(soc)
    elif server_response == '10':
        print("The server is busy currently serving other clients in some critical opearions. Please try after sometime. Thanks for your patience.")
    else:
        print("Error with the server. Please try again later. Client program will terminate")


# Main Function:
while True:    
    try:
        while 1:
            print("Server IP address:"+server_address[0])
            print("Server port number:"+str(server_address[1]))
            print("buffer size:"+str(bufferSize))
            choice = input("Are these information correct?(y/n)")
            if choice =='n':
                try:
                    user_address = input("Please enter the server IP address:")
                    ipaddress.ip_address(user_address)
                    user_port = int(input("Please enter the server port number:"))
                    if user_port < 1024:
                        print("Not a valid port number.")
                    else:
                        server_address = (user_address,user_port)
                        print("Server address is updated successfully.")
                    user_buffer_size = int(input("Please enter the buffer size:"))
                    if user_buffer_size < 64 or user_buffer_size > 65000:
                        print("Not a valid buffer size.")
                    else:
                        bufferSize = user_buffer_size
                    print("A socket will be created based on the given information.")
                    break 
                except ValueError:
                    print("Not a valid IP address.")
            elif choice =='y':
                print("New server information has been accepted. A socket will be created based on this information.")
                break
            else:
                print("Did not understand your choice. Please try again.")
        # create socket:
        soc = create_socket(10)
        while True:
            user_type = input("are you new user? (y/n)")
            if user_type == 'n':
                login_user(soc)
                break
            elif user_type == 'y':
                create_user(soc)
                break
            else:
                print("Did not understand your choice. Please try again.")
    except socket.timeout:
        print("server takes too mucth time to responce. The connection will be closed. You will also be logged out and terminate.")
        if user_credintals is not None:
            send_to_server("8|", soc, server_address)
        sys.exit()
    except KeyboardInterrupt:
        print("Force logout and termination. The program will logout and terminate.")
        if user_credintals is not None:
            send_to_server("8|", soc, server_address)
        sys.exit()
    except ConnectionResetError as c:
        print(">..........")
        print("Connection with the server is lost. Please make sure the server is alive.")
        sys.exit()
    except Exception as e:
        print(traceback.format_exc())
        if user_credintals is not None:
            send_to_server("8|", soc, server_address)
        sys.exit()