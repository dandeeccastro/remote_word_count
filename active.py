import socket 

if __name__ == "__main__":

    # Iniciando conexão no lado passivo
    sock = socket.socket()
    sock.connect(("localhost",4500))

    while True:
        # Envio o comando
        command = input()
        sock.send(bytes(command,encoding='utf-8'))

        command = command.split()
        # Fecho caso seja o comando de encerramento
        if command[0] == "close":
            break

        # Checando o número de arquivos enviados
        elif command[0] == "read":
            number_of_responses = len(command[1:])
            if number_of_responses == 0:
                message = sock.recv(1024)
                message = str(message, encoding='utf-8')
                print(message)
            else:
                for i in range(0,number_of_responses):
                    message = sock.recv(1024)
                    message = str(message, encoding='utf-8')
                    print(message)

        
        else:
            message = sock.recv(1024)
            message = str(message, encoding='utf-8')
            print(message)
