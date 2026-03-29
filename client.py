# --------------- Imports
import socket
import numpy as np
import threading


# --------------- Parte 1: Notificar Corridas
def notifica(socket):
    while True:
        try: 
            corrida = socket.recv(2048)
            if not corrida:
                break
            print(f'\n[NOTIFICAÇÃO RECEBIDA]:\n {corrida.decode('utf-8')}')
        except:
            break


# --------------- Parte 2: Enviar Comandos
def enviar_comando(socket):
    while True:
        comando = input()  # aqui é o que a gente envia o que o motorista quer pro servidor
        socket.sendall(comando.encode('utf-8')) 
        


# --------------- Cliente Completo
def motorista(host = 'localhost', port=8082): 

    # ------ conexão com o socket e servidor
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    conectar_servidor = (host, port) 
    soquete.connect(conectar_servidor) # fazendo a ponte com o server

    # ------ entrando com o nome de usuário e enviando para o server
    nome =  input('Entre com o seu nome de usuário:\n')
    soquete.sendall(nome.encode('utf-8'))

    
    # ------ thread 1 - notificar eventos de corrida
    thread1_escuta = threading.Thread(target=notifica, args=(soquete,))
    thread1_escuta.start()
  
    # ------ thread 2 - enviar comandos para o server
    thread2_envia = threading.Thread(target=enviar_comando, args=(soquete,))
    thread2_envia.start()
    thread2_envia.join()


    soquete.close()


# --------------- Execução do Programa
motorista() 