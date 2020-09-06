import socket 
import re

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
    result_string = file_handler.name + '\n' 
    for item in unique:
        result_string += item["word"] + '\t' + str(item["count"]) + '\n'

    return result_string

# Retorna o objeto de arquivo se ele existe, zero se não existe
def database_layer(file_name):
    try:
        file_handler = open(file_name, "r")
        return file_handler

    except Exception:
        return 0

if __name__ == "__main__":

    # Passos iniciais de conexão do lado passivo
    sock = socket.socket()
    sock.bind(('',4500))
    sock.listen(1)
    new_sock, address = sock.accept()

    while True:
        # Recebo o comando e divido ele
        message = new_sock.recv(1024)   
        message = str(message,encoding="utf-8")
        message = message.split()

        if message[0] == "close":
            break

        elif message[0] == "read":
            # Comando é read <nome do arquivo>, se o nome do arquivo não vem, informamos o usuário
            if len(message) == 1:
                new_sock.send(bytes("Incorrect command usage",encoding='utf-8'))

            else:
                file_amount = len(message[1:])
                print("Number of files to be checked: " + str(file_amount))
                for i in range (1,file_amount + 1):
                    result = database_layer(message[i])
                    result = processing_layer(result) if result != 0 else "File not found!"
                    new_sock.send(bytes(result,encoding='utf-8'))

        # Comando não reconhecido, avisamos o usuário
        else:
            new_sock.send(bytes("Unknown command, use read or close",encoding='utf-8'))

