import socket 
import re
import select
import sys
import multiprocessing

# Variáveis globais
inputs = [sys.stdin]
connections = dict()
HOST = "127.0.0.1"
PORT = 10000
MAX_CLIENTS = 5 

def main():
    sock = start_server()
    clients = []
    while True:
        read, write, execute = select.select(inputs,[],[])
        for process in read:
            if process == sock:
                clisock, addr = accept_connection(sock)
                print(str(addr) + " has connected")
                client = multiprocessing.Process(target=handle_request, args=(clisock,addr))
                client.start()
                clients.append(client)
            elif process == sys.stdin:
                print("Admin command detected")
                command = input()
                if command == "close":
                    for c in clients:
                        c.join()
                    sock.close()
                    sys.exit()

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # usando ipv4 e TCP
    sock.bind((HOST,PORT))
    sock.listen(MAX_CLIENTS)
    sock.setblocking(False)
    inputs.append(sock)
    return sock

def accept_connection(clisock):
    new_sock, addr = clisock.accept()
    connections[new_sock] = addr
    return new_sock, addr

def handle_request(clisock, addr):
    message = clisock.recv(1024)
    if not message:
        print(str(addr) + " closed connection")
        clisock.close()
        return
    else:
        message = str(message, encoding="utf-8")
        message = message.split()
        execute_command(message, clisock)
        
def execute_command(message,sock):
    if message[0] == "read":
        print("read command detected")
        if len(message) == 1:
            sock.send(bytes("[server]: Incorrent command usage", encoding="utf-8"))
        else:
            file_amount = len(message[1:])
            for i in range(1,file_amount + 1):
                result = database_layer(message[i])
                result = processing_layer(result) if result != 0 else "[server] File not found!"
                sock.send(bytes(result,encoding='utf-8'))

    elif message[0] == "echo":
        echo_message = ' '.join(message[1:])
        print(str(connections[sock]) + " " + echo_message)
        sock.send(bytes(echo_message,encoding='utf-8'))

    else:
        sock.send(bytes("[server] Command doesn't exist", encoding="utf-8"))

# Retorna o objeto de arquivo se ele existe, zero se não existe
def database_layer(file_name):
    try:
        file_handler = open(file_name, "r")
        return file_handler

    except Exception:
        return 0

def processing_layer(file_handler):
    words = [] # array que terá todas as palavras do texto
    unique = [{"word":"","count":-1}] # array com palavras únicas. contém objetos com a palavra e a contagem dela
    regex = re.compile('[^a-zA-ZáàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ]') # regex que pega somente letras

    # Adicionando palavras no array de todas as palavras
    for line in file_handler:
        line = line.strip()
        line = regex.sub(' ',line)
        words += line.split()

    # Uso o array de palavras para gerar o de palavras únicas
    for word in words:
        found = False
        for i in range(0,len(unique)):
            if word == unique[i]["word"]:
                unique[i]["count"] += 1
                found = True
                break
        if not found:
            unique.append({"word":word,"count":1})

    # Sorting reverso
    unique = unique[1:] # Botei um item com nada para não pegar erro de index, removo ele aqui
    unique.sort(key=lambda a: a["count"], reverse=True)

    # Gerando a string final com palavra e contagem, separados por tab
    result_string = "[server] Word count for " + file_handler.name + '\n' 
    for item in unique:
        result_string += item["word"] + '\t' + str(item["count"]) + '\n'

    return result_string

main()
