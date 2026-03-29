# --------------- Imports
import socket
import numpy as np
import threading
import time
import random
import json


# --------------- Impedindo que haja 'competição' entre as  threads, vamos usar o lock para isso
lock_dados = threading.Lock()

# --------------- Parte 1: Gerar Eventos de Corrida

def gerar_evento(client, dados):
    primeira_corrida = True 
    
    while not dados['sair']: 
        try:
            espera = 0 if primeira_corrida else 10
            time.sleep(espera)
            
            if dados['sair']:
                break

            if dados['status'] == True:
                dist_inicial = np.random.randint(1, 20)
                dist_total = np.random.randint(1, 100)
                
                dados['valor_atual'] = round((dist_total * 2.50) * 0.25, 2)
                
                notif = (f"\n--- OLÁ MOTORISTA! ---\nDistância Inicial: {dist_inicial} Km\n"
                         f"Distância Corrida: {dist_total} Km\n"
                         f"Valor: R$ {dados['valor_atual']}\n")
                
                client.sendall(notif.encode('utf-8'))
                
                time.sleep(8)

                # notificação para quando demorar demais pra responder (status true significa que ainda não aceitou)
                if dados['status'] == True:
                  cancelar = 'CORRIDA CANCELADA'.encode('utf-8')
                  novo_preco = round(dados['valor_atual'] + (dados['valor_atual'] * 0.35), 2)
                  aumentar = f'NOVO PREÇO: {(round(novo_preco, 2))} reais'.encode('utf-8')
                  lista = [cancelar, aumentar]
                  sorteio = random.choice(lista)

                  if sorteio == aumentar:
                      dados['valor_atual'] = novo_preco

                  client.sendall(sorteio)

                primeira_corrida = False

            else:
                client.sendall('\n[Finalize a corrida atual para receber novas]'.encode('utf-8'))
                time.sleep(5)
            
        except (OSError, ConnectionResetError):
            break

# --------------- Parte 2: Receber Comandos

def mostrar_status(status):
  if status == True:
    return 'Status: DISPONÍVEL'
  else:
    return 'Status: OCUPADO'

def recebe_comando(client, data, dados, dicio_base):
    
    while True:
        try:
            resposta = client.recv(data).decode('utf-8').strip()

            if resposta == ':aceitar': 
                dados['status'] = False 
                client.sendall('CORRIDA ACEITA!'.encode('utf-8'))

            elif resposta == ':finalizada':
                dados['status'] = True
   
                dados['saldo_total'] = round(dados['saldo_total'] + dados['valor_atual'], 2)
                dados['valor_atual'] = 0 
                
                client.sendall(f'CORRIDA FINALIZADA! NOVO SALDO: R$ {dados["saldo_total"]}'.encode('utf-8'))

                with open("saldos.json", "w") as arquivo:
                    json.dump(dicio_base, arquivo, indent=4)
            
            elif resposta == ':status':
                mensagem = "DISPONÍVEL" if dados['status'] == True else "OCUPADO"
                client.sendall(f'Status atual: {mensagem}'.encode('utf-8'))

            elif resposta == ':cancelar':
                dados['status'] = True
                client.sendall(f'CORRIDA CANCELADA!'.encode('utf-8'))

            elif resposta == ':sair':
                dados['sair'] = True
                client.sendall('Saindo...'.encode('utf-8'))
                break
                  
        except:
            break

    client.close()


# --------------- Servidor Completo
def servidor(host='localhost', port=8082): # operação local, porta TCP/UDP (local host indica basicamente o IP da nossa máquina)
    
    # primeiramente tentamos abrir o arquivo se ele existe, caso não, criamos um dicionário 
    try:
        with open("saldos.json", "r") as arquivo:
            dicio_base = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        dicio_base = {}
  
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
      nome_motorista = motorista.recv(2048).decode('utf-8')

      # testando se o motorista atual está na lista, caso não, botamos ele lá
      if nome_motorista not in dicio_base:
          dicio_base[nome_motorista] = {
              'valor_atual': 0,
              'saldo_total': 0,
              'status': True,
              'sair': False
          }
          # Salva o novo motorista de forma protegida
          with lock_dados:
              with open("saldos.json", "w") as arquivo:
                  json.dump(dicio_base, arquivo, indent=4)
                  

      dados_motorista = dicio_base[nome_motorista]


      # ------ thread 2 - gerar eventos de corrida
      thread2_evento = threading.Thread(target=gerar_evento, args=(motorista, dados_motorista) ) # parâmetro da função gerar evento
      thread2_evento.start()


      # ------ thread 1 - receber comando E atualiza a fila de motoristas (À SER FEITO)
      thread1_recebe = threading.Thread(target=recebe_comando, args=(motorista, carga_dados,dados_motorista, dicio_base ) ) # parâmetro da função gerar evento
      thread1_recebe.start()


# --------------- Execução do Programa
servidor()