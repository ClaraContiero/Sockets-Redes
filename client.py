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
import time


# --------------- Funções Principais

def enviar_comando(socket):
    while True:
        comando = input('Sua Escolha: ')  # aqui é o que a gente envia o que o motorista quer pro servidor
        socket.sendall(comando.encode('utf-8')) 
        if comando == '4':
            print("\nSaindo da Aplicação...")
            break

def print_evento(socket):
    while True:
        recebe_evento = socket.recv(2048)
        print(f"\n[NOTIFICAÇÃO]\n{recebe_evento.decode('utf-8')}")
        print(f"\nEscolha uma opção abaixo:\n|1| ACEITAR\n|2| CANCELAR\n|3| MOSTRAR STATUS\n|4| SAIR\n")


# --------------- Função Cliente

def motorista(host = 'localhost', port=8082): 
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    conectar_servidor = (host, port) 

    print("Conectando ao endereço %s na porta %s" % conectar_servidor) 
    soquete.connect(conectar_servidor) 


    # Thread 2 - imprime notificação na tela
    thread2_printEvento = threading.Thread(
    target=print_evento, 
    args=(soquete,) # parâmetro da função gerar evento
    )

    # # Thread 1 - envia comando
    # thread1_comandos = threading.Thread(
    #     target=enviar_comando, 
    #     args=(soquete,) # parâmetro da função gerar evento
    # )

    # rodando as threads
    thread2_printEvento.start()
    # thread1_comandos.start()

        
    print('\nCliente conectado a')

    while True:
        time.sleep(1)


    # e aqui é o comando que encerra o programa
    # thread1_comandos.join()
    soquete.close()




# chamando a função motorista
motorista()