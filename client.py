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
import threading


# --------------- Funções Principais
def enviar_comando(socket):
    comando = input('\n--- DIGITE O CÓDIGO DA AÇÃO QUE DESEJA REALIZAR ---\n|1| ACEITAR\n|2| CANCELAR\n|3| MOSTRAR STATUS\n|4| SAIR\n')  # aqui é o que a gente envia o que o motorista quer pro servidor
    socket.sendall(comando.encode('utf-8')) 



def motorista(host = 'localhost', port=8082): 
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    conectar_servidor = (host, port) 

    print("Conectando ao endereço %s na porta %s" % conectar_servidor) 
    soquete.connect(conectar_servidor) 


    # Thread 1
    recebe_evento = soquete.recv(2048)
    print(f"{recebe_evento.decode('utf-8')}")


    # Thread 2
    
    thread1_comandos = threading.Thread(
        target=enviar_comando, 
        args=(soquete,) # parâmetro da função gerar evento
    )
    
    thread1_comandos.start()

    # aqui estamos tentando garantir que os dados cheguem completos ao outro lado
    # amount_received = 0 
    # amount_expected = len(comando) 

    # while amount_received < amount_expected: 
    data = soquete.recv(1024) 
    # amount_received += len(data) 
    print (f"Recebido do Servidor: {data.decode('utf-8')}" )  

    # e aqui é o comando que encerra o programa
    soquete.close()




# chamando a função motorista
motorista()