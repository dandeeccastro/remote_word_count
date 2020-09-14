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

    # Inicializar server e array de clientes (processos)
    sock = start_server()
    clients = []

    while True:
        read, write, execute = select.select(inputs,[],[]) # usando select para pegar os tipos de inputs diferentes
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

# Configurações iniciais do servidor, setando sock como não bloqueante para deixar isso com o select
# e adicionando esse sock como uma fonte de input
def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # usando ipv4 e TCP
    sock.bind((HOST,PORT))
    sock.listen(MAX_CLIENTS)
    sock.setblocking(False)
    inputs.append(sock)
    return sock

# Aceito a conexão e adiciono ela no dicionário de histórico de conexões
def accept_connection(clisock):
    new_sock, addr = clisock.accept()
    connections[new_sock] = addr
    return new_sock, addr

# Função que é rodada em cada processo. Chama execute_command quando existe comando
# e desconecta quando não existe nenhum. Prints a partir daqui não aparecem no terminal
# porque o processo que roda essa função não é o que tá associado ao stdout do terminal
def handle_request(clisock, addr):
    message = clisock.recv(1024)
    if not message:
        print(str(addr) + " closed connection")
        clisock.close()
    else:
        message = str(message, encoding="utf-8")
        message = message.split() # para poder pegar os argumentos do comando em questão
        execute_command(message, clisock)
        
# Aqui é onde eu lido com comandos de leitura e fechamento de conexão. Essa função pode ser
# expandida para ter outros comandos (como eu fiz aqui com o comando de echo)
def execute_command(message,sock):
    if message[0] == "read":
        print("read command detected")
        if len(message) == 1:
            sock.send(bytes("[server]: Incorrent command usage", encoding="utf-8")) # Enviou o read sem dizer qual arquivo ler
        else:
            file_amount = len(message[1:]) # Se o read foi usado de forma correta, cada item é um arquivo diferente
            for i in range(1,file_amount + 1):
                result = database_layer(message[i])
                result = processing_layer(result) if result != 0 else "[server] File not found!"
                sock.send(bytes(result,encoding='utf-8'))

    elif message[0] == "echo":
        echo_message = ' '.join(message[1:]) # Junto a mensagem de novo
        print(str(connections[sock]) + " " + echo_message
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

# Conta as palavras e gera a string final do resultado
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
