# import random
# import numpy as np
# import pandas as pd

# nome = 'maria'

# valor_total = 0


# # cria o arquivo
# try:
#   with open("saldos.json", "r") as arquivo:
#       base_dados = json.load(arquivo)
# except:
#   dicio_base = {}

# if nome in dicio_base:
#   print(f'SALDO ATUAL: {dicio_base[nome]}')
# else:
#   dicio_base[nome] = 0

# with open("saldos.json", "w") as arquivo:
#     json.dump(dicio_base, arquivo, indent=4) ---> salvar  o arquivo





# --------------- Imports
import socket
import numpy as np
import threading
import time
import random
import json


# --------------- Variáveis Globais
valor_total = 0
status = True # True - Disponível
sair = False
saldo_total = 0


# --------------- Parte 1: Gerar Eventos de Corrida
def gerar_corrida():
  dist_inicial = np.random.randint(1, 20)
  dist_total = np.random.randint(1, 100)
  global valor_total
  valor_total = (dist_total * 2.50) * 0.25
  notif = f"\n--- OLÁ, MOTORISTA! ---\nDistância para o Início da Corrida: {dist_inicial} Km\nDistância da Corrida: {dist_total} Km\nValor a Ser Recebido: {round(valor_total,2)} reais\n"
  return notif


def gerar_evento(client):
    global sair
    primeira_corrida = True # isso é pra que o programa execute rápido só na primeira rodada

    while not sair: # enquanto sair for True
        try:
            espera = 0 if primeira_corrida else 10
            time.sleep(espera)
            if sair:
                break

            corrida_atual = gerar_corrida()
            client.sendall(corrida_atual.encode('utf-8'))

            time.sleep(6)

            if status == True:    
                cancelar = 'CORRIDA CANCELADA'.encode('utf-8')
                aumentar = f'NOVO PREÇO: {(round(valor_total + (valor_total * 0.35),2))} reais'.encode('utf-8')
                lista = [cancelar, aumentar]
                sorteio = random.choice(lista)
                client.sendall(sorteio)

            primeira_corrida = False
        except (OSError, ConnectionResetError):
            break

# --------------- Parte 2: Receber Comandos

def mostrar_status(status):
  if status == True:
    return 'Status: DISPONÍVEL'
  else:
    return 'Status: OCUPADO'

def recebe_comando(client, data):
  global sair 
  global status
  global resposta
  global saldo_total

  while True:
    try:
      resposta = client.recv(data) # aqui é onde ele recebe a mensagem do client (se vai aceitar, cancelar, sair ou mostrar status)
      
      resposta_decode = resposta.decode('utf-8').strip()

      if resposta_decode == (':aceitar'): 
        status = False # então o status muda pra ocupado
        saldo_total = saldo_total + valor_total
        client.sendall('CORRIDA ACEITA!'.encode('utf-8'))

      elif resposta_decode == (':cancelar'): 
        status = True # status muda pra disponível
        client.sendall('CORRIDA CANCELADA!'.encode('utf-8'))

      elif resposta_decode == (':status'):
        client.sendall(mostrar_status(status).encode('utf-8'))

      elif resposta_decode == (':carteira'):
         client.sendall(f'SALDO TOTAL: R${round(saldo_total, 2)}'.encode('utf-8'))

      elif resposta_decode == (':sair'):
        sair = True
        try:
            client.sendall('Saindo da Aplicação...'.encode('utf-8'))
            # aqui vai ser salvo no txt
        except:
          pass
        break
    except:
      break
  client.close()

      
# --------------- Servidor Completo
def servidor(host='localhost', port=8082): # operação local, porta TCP/UDP (local host indica basicamente o IP da nossa máquina)
    global status
    global sair
   

    # ------ conexão com o socket
    carga_dados =  2048 # quantidade máxima de dados que pode ser recebida de uma vez
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # com o soquete criado, estamos definindo que iremos usar IPv4 e que o protocolo de transporte será o TCP (queremos que os dados cheguem inteiros)
    conectar_servidor = (host, port) # é o que vai associar o nosso soquete criado com o endereço IP e a porta que estamos utilizando
    print('Inicializando servidor -> %s port %s' %conectar_servidor)
    soquete.bind(conectar_servidor)
    soquete.listen(5) # aqui podemos colocar um parâmetro que indica quantas conexões pendentes serão permitidas antes de recusar novas conexões
    print('Esperando o motorista...')
 
    while True:
      motorista, endereco = soquete.accept()

      # ------ aqui o server identifica o motorista - gera as threads para cada "terminal"
      nome_motorista = motorista.recv(2048).decode('utf-8')
      # base_motoristas = json.loads('base_motoristas.json')
      
      # for i in base_motoristas:
      #    if nome_motorista == i:
      #       print(f'Saldo atual do motorista {i} = {base_motoristas[i]}')



      print(f'Motorista {nome_motorista} conectado.')


      # ------ thread 2 - gerar eventos de corrida
      thread2_evento = threading.Thread(target=gerar_evento, args=(motorista,) ) # parâmetro da função gerar evento
      thread2_evento.start()


      # ------ thread 1 - receber comando E atualiza a fila de motoristas (À SER FEITO)
      thread1_recebe = threading.Thread(target=recebe_comando, args=(motorista, carga_dados) ) # parâmetro da função gerar evento
      thread1_recebe.start()


# --------------- Execução do Programa
servidor()