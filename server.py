# --------------- PROJETO: Desenvolvimento de um sistema de chat multiusuário com notificação de status

# socket()
# .bind()
# .listen()
# .accept()
# .connect()
# .connect_ex()
# .send()
# .recv()
# .close()


# --------------- Imports

import socket
import numpy as np
import threading
import time


# --------------- Variáveis Globais - vão ser alteradas ao longo do programa

valor_total = 0
status = True # se True, motorista está disponível, se False, não está
sair = False


# --------------- Funções Principais

def gerar_corrida():
  global valor_total
  dist_inicial = np.random.randint(1, 20)
  dist_total = np.random.randint(1, 100)
  global valor_total
  valor_total = (dist_total * 2.50) * 0.25
  notif = f"\n--- OLÁ, MOTORISTA! ---\nDistância para o Início da Corrida: {dist_inicial} Km\nDistância da Corrida: {dist_total} Km\nValor a Ser Recebido: {round(valor_total,2)} reais\n"
  return notif

def mostrar_status(status):
  if status == True:
    return 'Status: Disponível'
  else:
    return 'Status: Ocupado'
  
def gerar_evento(client):
  global status
  while True:
    time.sleep(3)
    if status == 'True':
      client.sendall(gerar_corrida().encode('utf-8'))


def recebe_comando(client, data):
  global status
  while True:
    resposta = client.recv(data) # aqui é onde ele recebe a mensagem do client (se vai aceitar, cancelar, sair ou mostrar status)
    resposta_decode = resposta.decode('utf-8').strip()

    if resposta_decode == ('1'): 
      status = False # então o status muda pra ocupado
      client.sendall("CORRIDA ACEITA".encode('utf-8'))

    elif resposta_decode == ('2'): 
      status = True # status muda pra disponível
      client.sendall("CORRIDA CANCELADA".encode('utf-8'))

    elif resposta_decode == ('3'):
      client.sendall(mostrar_status(status).encode('utf-8'))

    elif resposta_decode == ('4'):
      sair = True
      print('Saindo da aplicação...')
      client.sendall('Saindo da Aplicação...'.encode('utf-8'))
      break

    client.close()
    sair = True

# --------------- Função Servidor

def servidor(host='localhost', port=8082): # operação local (na minha máquina), porta TCP/UDP (local host indica basicamente o IP da nossa máquina)
  global status
  global sair
  
  carga_dados =  2048 # quantidade máxima de dados que pode ser recebida de uma vez

  soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # com o soquete criado, estamos definindo que iremos usar IPv4 e que o protocolo de transporte será o TCP (queremos que os dados cheguem inteiros)

  conectar_servidor = (host, port) # é o que vai associar o nosso soquete criado com o endereço IP e a porta que estamos utilizando

  print('Inicializando servidor -> %s port %s' %conectar_servidor)
  soquete.bind(conectar_servidor)

  soquete.listen(5) # aqui podemos colocar um parâmetro que indica quantas conexões pendentes serão permitidas antes de recusar novas conexões

  print('Esperando o motorista...')
  
  motorista, endereco = soquete.accept() # ele cria o socket que conversa com o client

  # Thread 2 - gera os eventos
  thread2_evento = threading.Thread(
    target=gerar_evento, 
    args=(motorista,) # parâmetro da função gerar evento
)
  

  # Thread 1 - recebe os comandos e altera os status
#   thread1_recebeComma = threading.Thread(
#     target=recebe_comando, 
#     args=(motorista, carga_dados) # parâmetro da função gerar evento
# )
  
  # rodando as threads
  thread2_evento.start()
  # thread1_recebeComma.start()
  



servidor() # chamando a função servidor
