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
    while True:
        comando = input('\n--- DIGITE O CÓDIGO DA AÇÃO QUE DESEJA REALIZAR ---\n|1| ACEITAR\n|2| CANCELAR\n|3| MOSTRAR STATUS\n|4| SAIR\n')  # aqui é o que a gente envia o que o motorista quer pro servidor
        socket.sendall(comando.encode('utf-8')) 
        if comando == '4':
            break


def notifica(socket):
    while True:
        try: 
            corrida = socket.recv(2048)
            if not corrida:
                break
            print(f'\n[NOTIFICAÇÃO RECEBIDA]:\n {corrida.decode('utf-8')}')
        except:
            break



# --------------- Funçaõ Client
def motorista(host = 'localhost', port=8082): 
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    conectar_servidor = (host, port) 
    soquete.connect(conectar_servidor) 


    # Thread 1
    thread1_escuta = threading.Thread(target=notifica, args=(soquete,), daemon=True)
    thread1_escuta.start()


    # Thread 2

    # while True:
    #     comando = input('\n--- MENU ---\n|1| ACEITAR\n|2| CANCELAR\n|3| STATUS\n|4| SAIR\n> ')
    #     soquete.sendall(comando.encode('utf-8'))
        
    #     if comando == '4':
    #         break


    thread2_comando = threading.Thread(target=enviar_comando, args=(soquete,), daemon=True)
    thread2_comando.start()


    soquete.close()
    



# chamando a função motorista
motorista()