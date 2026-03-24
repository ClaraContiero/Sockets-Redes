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

# Limitação de conexões
max_conexoes = 2
conexoes_ativas = 0
lock_conexoes = threading.Lock()


# --------------- Parte 1: Gerar Eventos de Corrida
def gerar_corrida():
  global valor_total

  dist_inicial = np.random.randint(1, 20)
  dist_total = np.random.randint(1, 100)
  global valor_total
  valor_total = round((dist_total * 2.50) * 0.25, 2)
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
                novo_preco = round(valor_total + (valor_total * 0.35), 2)
                aumentar = f'NOVO PREÇO: {(round(novo_preco, 2))} reais'.encode('utf-8')
                valor_total = novo_preco
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

def recebe_comando(client, data, nome, saldo):
  global sair 
  global status
  global resposta
  global valor_total
  global conexoes_ativas

  while True:
    try:
      resposta = client.recv(data) # aqui é onde ele recebe a mensagem do client (se vai aceitar, cancelar, sair ou mostrar status)
      resposta_decode = resposta.decode('utf-8').strip()

      if resposta_decode == (':aceitar'): 
        status = False # então o status muda pra ocupado
        client.sendall('CORRIDA ACEITA!'.encode('utf-8'))

        with open("saldos.json", "w") as arquivo:
          dicio_base[nome] = round(saldo + valor_total, 2)
          saldo = round(dicio_base[nome], 2)
          json.dump(dicio_base, arquivo, indent=4)
        
      elif resposta_decode == (':cancelar'): 
        status = True # status muda pra disponível
        client.sendall('CORRIDA CANCELADA!'.encode('utf-8'))

      elif resposta_decode == (':status'):
        client.sendall(mostrar_status(status).encode('utf-8'))

      elif resposta_decode == (':carteira'):
          with open("saldos.json", "r") as arquivo:
            base = json.load(arquivo) 
            client.sendall(f'SALDO ATUAL: R$ {round(base[nome], 2)}'.encode('utf-8'))

      elif resposta_decode == (':sair'):
        sair = True
        try:
            client.sendall('Saindo da Aplicação...'.encode('utf-8'))
        except:
          pass
        break
    except:
      break

  client.close()

  # diminui a quantidade de conexões ativas quando o cliente sair
  with lock_conexoes:
    conexoes_ativas -= 1


      
# --------------- Servidor Completo
def servidor(host='localhost', port=8082): # operação local, porta TCP/UDP (local host indica basicamente o IP da nossa máquina)
    global status
    global sair
    global dicio_base
    global conexoes_ativas
   

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

      # ------ limitação do número de conexões
      with lock_conexoes:
        if conexoes_ativas >= max_conexoes:
          motorista.sendall('LIMITE DE CONEXÕES ATINGIDO. TENTE NOVAMENTE MAIS TARDE.'.encode('utf-8'))
          motorista.close()
          continue
        conexoes_ativas += 1

      # ------ aqui o server identifica o motorista - gera as threads para cada "terminal"
      nome_motorista = motorista.recv(2048).decode('utf-8')
      print(f'Motorista {nome_motorista} conectado.')

      # # ------ já aqui vamos criar nosso arquivo de "cadastro" dos motoristas

      try: # primeiro ele testa se o arquivo já existe e faz a "pesquisa" pra definir o saldo total atual
        with open("saldos.json", "r") as arquivo:
            dicio_base = json.load(arquivo)
            if nome_motorista in dicio_base:
              saldo_total = round(dicio_base[nome_motorista],2)
            else:
              with open("saldos.json", "w") as arquivo:
                dicio_base[nome_motorista] = 0
                json.dump(dicio_base, arquivo, indent=4)
                saldo_total = round(dicio_base[nome_motorista],2)

      except: # aqui caso não exista o arquivo, ele cria um novo e já define o nome com saldo = 0
              dicio_base = {}
              with open("saldos.json", "w") as arquivo:
                dicio_base[nome_motorista] = 0
                saldo_total = round(dicio_base[nome_motorista],2)
                json.dump(dicio_base, arquivo, indent=4)


      # ------ thread 2 - gerar eventos de corrida
      thread2_evento = threading.Thread(target=gerar_evento, args=(motorista,) ) # parâmetro da função gerar evento
      thread2_evento.start()


      # ------ thread 1 - receber comando E atualiza a fila de motoristas (À SER FEITO)
      thread1_recebe = threading.Thread(target=recebe_comando, args=(motorista, carga_dados, nome_motorista, saldo_total) ) # parâmetro da função gerar evento
      thread1_recebe.start()


# --------------- Execução do Programa
servidor()