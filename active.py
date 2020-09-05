import socket 

if __name__ == "__main__":

    # Iniciando conexão no lado passivo
    sock = socket.socket()
    sock.connect(("localhost",4500))

    while True:
        # Envio o comando
        command = input()
        sock.send(bytes(command,encoding='utf-8'))

        # Fecho caso seja o comando de encerramento
        if command == "close":
            break

        # Recebo a mensagem caso o comando seja válido
        message = sock.recv(1024)
        message = str(message,encoding="utf-8")
        print(message)
