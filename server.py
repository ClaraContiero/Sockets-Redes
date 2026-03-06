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


# --------------- Variáveis Globais

valor_total = 0
status = True # se True, motorista está disponível, se False, não está
sair = False


# --------------- Funções Principais

def gerar_corrida():
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
  while True:
    time.sleep(5)
    client.sendall(gerar_corrida().encode('utf-8'))


def servidor(host='localhost', port=8082): # operação local, porta TCP/UDP (local host indica basicamente o IP da nossa máquina)

  global status
  global sair
  
  data_payload =  2048 # quantidade máxima de dados que pode ser recebida de uma vez

  soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # com o soquete criado, estamos definindo que iremos usar IPv4 e que o protocolo de transporte será o TCP (queremos que os dados cheguem inteiros)


  conectar_servidor = (host, port) # é o que vai associar o nosso soquete criado com o endereço IP e a porta que estamos utilizando

  print('Inicializando servidor -> %s port %s' %conectar_servidor)
  soquete.bind(conectar_servidor)

  soquete.listen(5) # aqui podemos colocar um parâmetro que indica quantas conexões pendentes serão permitidas antes de recusar novas conexões


  print('Esperando o motorista...')
  
  motorista, endereco = soquete.accept()

  # Thread 2

  thread2_evento = threading.Thread(
    target=gerar_evento, 
    args=(motorista,) # parâmetro da função gerar evento
)
  
  thread2_evento.start()

  # Thread 1
  resposta = motorista.recv(data_payload) # aqui é onde ele recebe a mensagem do client (se vai aceitar, cancelar, sair ou mostrar status)
  resposta_decode = resposta.decode('utf-8').strip()

  if resposta_decode == ('1'): 
    status = False # então o status muda pra ocupado
    motorista.sendall("CORRIDA ACEITA".encode('utf-8'))

  elif resposta_decode == ('2'): 
    status = True # status muda pra disponível
    motorista.sendall("CORRIDA CANCELADA".encode('utf-8'))

  elif resposta_decode == ('3'):
    motorista.sendall(mostrar_status(status).encode('utf-8'))

  elif resposta_decode == ('4'):
    sair = True
    print('Saindo da aplicação...')
    motorista.sendall('Saindo da Aplicação...'.encode('utf-8'))
    motorista.close()



servidor() # chamando a função servidor
