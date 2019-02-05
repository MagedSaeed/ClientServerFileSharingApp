Introduction
==========

This is a _readme_ file for **file sharing client server application**. The propose of this application is to share files through sockets using *UDP* protocol. The program is written in python.

Usage
=====

After downloading program files:
- Run server.py on one machine.
- Get the IP address and port number of this machine on the network. The default value of the port number is 20000. The default value for the buffer size is 65000.
- Run the client.py on a machine. Either the same machine of the server or any other machine on the network.
- When client.py starts. It will show the default values for the server address and port numbers. Modify them as needed and start using the application.

Dependencies
===========
Please make sure that the following libraries are available. Use the well-known python package manager *pip* to download:

- For the client application:
	- socket
	- pathlib
	- select
	- ast
	- subprocess
	- ipaddress
	- getpass

- For the server application:
	- socket
	- msvcrt
	- tinydb


Impelentation Details
====================

## Concurrency

The program tries to achieve concurrnecy using threads. However, this is packed with a limitation in hand. The biggest file size can be uploaded to the server is the largest size a UDP packet can handle which is 65000 byte.

## Control Flow design:

When start implementing the application, two ideas came up in mind:
1. Either to show all the functionalities as a list and the user chose one of these functionalities. 
2. Or let the user type the command name and parameters just like FTP application.

The First choice is appealing. The application will be clear and smooth enought such that writing a user manual is unnecessary. However, it is not the most user friendly choice.
The second choice is more elegant. No more words on the screen. The user can type in 'help' to get familiar with the application commands.

## Flow of the program:

### Server application:
When running *server.py*, a general instructions will be shown. Then, the server will be alive waiting for client connections. It will show notifications every 10 seconds about the number of connected clients. When a client sends a message, the server reports this on the screen.

### Client application:

When the *client.py* runs, it will ask the user to assure server information. If these information are not correct, the program will ask the user to update them . The program will, then, ask the user if he is a new user or not. If he is a new, then he will create a new profile after collected the needed information from the user then ask him to log in. After logging in, the program will ask the user to input his commands with the appropriate parameters if there is any.



Connection Protocol
==================

This section will show the commands used by the client application and the protocol used to communicate with the server.  The client application uses flags to indicate the required command. The server application will receive this flag and respond accordingly. The list of commands are as follows:

- ls
  This command is used to list all files in the server repository. The user needs to type *ls*. The client application will send a flag value of 2 to the server in order to receive the list of file names.

- download filename 
  This command is used to download files from the server. The user shall provide the file name as a parameter to this command. The client application will send a flag value of 3 to the server in order to download the file of interest. 

- upload filepath
  This command is used to upload a file to the server. The user shall provide the complete file path as a parameter to this command. The client application will send a flag value of 4 to the server in order to upload the file of interest. 

- search filename
  This command is used to search files in the server. The user shall provide the file name as a parameter to this command. The client application will send a flag value of 5 to the server in order to search the file of interest.

- stats [options]
  This command is used to retrieve usage information from the server. These information are the logs of download, login, upload and the account creation time. Values of these parameters are [dlog, llog, ulog, ctime] respectively. If no option is specified, the server will return all these logs. The flag value sent by the client application in order to perform this operation is 7. flags for options are 1,23,4 for creation time, login log, download log and upload log.

- update
  This command is used to update user name and password of the user account. Once used, the client application will ask for the account credentials. If provided correctly, the client application will send a flag value of 6 along with the new name and password. The server will make sure the user name is not used informing the client application if so. Otherwise, the update operation will be succeed.

- help
  This command is used to give an overview of the previous commands and how it works. There is no need to contact the server in order to do so.

- cls
  This command is used to clear the screen. It is usually needed when the command line interface becomes so crowded with the many information shown.

- exit
  This command is used to logout from both the client and server applications. The flag sent by the client to communicate this information to the server is 8.

- Other connections and useful notes
  - When the user first uses the client application, the application asks him to sign up. It sends this information with flag 0. If the user is already a registered user, the client application will send his information with the flag value of 1.
  - When the client application shutdowns for any reason, a logout signal is sent to the server. The flag is the same.
  - When the server is getting a file from a client, it is not accepting any other client connections. It sends a flag value of  10 to notify the client app that he is busy currently.
  - The server may return flags of 1, 0 or -1. 1 indicates a successful operation. 0 indicates a successful connection but wrong parameter. -1 indicates that an unknown error occurred.

Database
=======

In order to achieve the above operation, a sort of database structure shall be maintained. However, building a huge database infrastructure such as SQLServer or Oracle database server will overcome the simplicity and elegancy of this application. The goal, though, is to come up with an in-between solution. Suggestions are to use *json* or *xml* as they are simple and sufficient enough. A nice python library performing this job is, fortunately, available. It is called *tinydb* and linked here: https://pypi.org/project/tinydb/. It maintains a *json* structure simplifying database operations and queries.

Contact
======
This application is done as an assignment to a client-server progarmming graduate course. However, it turns out that it worths publishing. Please report any issues or inqueries you have either by opening an issue here in this repository or e-mail me on mageedsaeed1@gmail.com. Thanks in advance.