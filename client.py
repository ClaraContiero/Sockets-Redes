# --------------- PROJETO: Desenvolvimento de um sistema de chat multiusuário com notificação de status

# socket()
# .bind()
# .listen()
# .accept() 
# .connect()
# .connect_ex()
# .send()
# .recv()
# .close() -> podemos fechar a aplicação aqui


# --------------- Imports

import socket
import numpy as np
import socket


# --------------- Funções Principais

def motorista(host = 'localhost', port=8082): 
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    conectar_servidor = (host, port) 

    print("Conectando ao endereço %s na porta %s" % conectar_servidor) 
    soquete.connect(conectar_servidor) 

    # acho que aqui é o que a gente envia o que o motorista quer pro servidor
    
    message = input('\nDIGITE AQUI O QUE DESEJA FAZER:\n')
    print("Enviando... %s" % message) 

    soquete.sendall(message.encode('utf-8')) 

    # aqui estamos tentando garantir que os dados cheguem completos ao outro lado
    amount_received = 0 
    amount_expected = len(message) 

    while amount_received < amount_expected: 
        data = soquete.recv(1024) 
        amount_received += len(data) 
        print ("Recebido do Servidor: %s" % data)  

    # e aqui é o comando que encerra o programa
    soquete.close()




motorista()