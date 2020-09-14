import socket 
import sys

HOST = "127.0.0.1"
PORT = 10000 

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST,PORT))
    while True:
        command = input()
        handleCommand(sock, command)

def handleCommand(sock, command):
    command = command.split()

    if command[0] == "close":
        sock.close()
        sys.exit()

    elif command[0] == "read":
        sock.send(bytes(' '.join(command),encoding='utf-8'))
        number_of_responses = len(command[1:])
        print(number_of_responses)

        if (number_of_responses <= 1):
            message = sock.recv(1024)
            message = str(message, encoding='utf-8')
            print(message)

        else:
            for i in range(0,number_of_responses):
                message = sock.recv(1024)
                message = str(message, encoding='utf-8')
                print(message)
    else:
        sock.send(bytes(' '.join(command),encoding='utf-8'))
        message = sock.recv(1024)
        message = str(message, encoding='utf-8')
        print(message)

main()
