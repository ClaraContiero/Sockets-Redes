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

    # ------ verifica se o servidor respondeu com o limite excedido
    try:
        soquete.settimeout(6) #espera até 06 segundos por uma resposta inicial
        resposta_inicial = soquete.recv(2048) 
        if resposta_inicial:
            mensagem = resposta_inicial.decode('utf-8') #transformar resposta do servidor em txt
            if "LIMITE DE CONEXÕES ATINGIDO" in mensagem:
                print(f'\n{mensagem}')
                soquete.close()
                return
            else:
                print(f"\n[NOTIFICAÇÃO RECEBIDA]:\n {mensagem}")
    except socket.timeout:
        pass
    except (ConnectionAbortedError, ConnectionResetError):
        print(f'\nLIMITE DE CONEXÕES ATINGIDO. TENTE NOVAMENTE MAIS TARDE!!')
        soquete.close()
        return
    
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