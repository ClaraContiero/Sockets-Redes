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
  notif = "Distância para o Início da Corrida: {dist_inicial} Km\nDistância da Corrida: {dist_total} Km\nValor a Ser Recebido: {round(valor_total,2)} reais"
  return notif

   
def mostrar_status(status):
   if status == True:
    print('Disponível')
   else:
      print('Ocupado')


# operação local, porta TCP/UDP (local host indica basicamente o IP da nossa máquina)
def servidor(host='localhost', port=8082): 
    global status
    global sair
    
    # quantidade máxima de dados que pode ser recebida de uma vez
    data_payload =  2048 

    # com o soquete criado, estamos definindo que iremos usar IPv4 e que o protocolo de transporte será o TCP (queremos que os dados cheguem inteiros)
    soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    # é o que vai associar o nosso soquete criado com o endereço IP e a porta que estamos utilizando
    conectar_servidor = (host, port) 
    print('Inicializando servidor -> %s port %s' %conectar_servidor)
    soquete.bind(conectar_servidor)

    soquete.listen(5) # aqui podemos colocar um parâmetro que indica quantas conexões pendentes serão permitidas antes de recusar novas conexões


    while sair != True:
        print('Esperando mensagem do cliente.')
        
        motorista, endereco = soquete.accept()

        resposta = motorista.recv(data_payload) # aqui é onde ele recebe a mensagem do client
        resposta = resposta.decode().strip().upper()


        if resposta == ('ACEITAR'): # então o status muda pra ocupado
          status = False
          print("Data:' %s" %resposta)
          motorista.sendall("CORRIDA ACEITA".encode('utf-8'))

        elif resposta == ('CANCELAR'): # status muda pra disponível
          status = True
          print("Data:' %s" %resposta)
          motorista.sendall("CORRIDA CANCELADA".encode('utf-8'))

        elif resposta == ('MOSTRAR STATUS'):
          print("Data:' %s" %resposta)
          motorista.sendall(f"STATUS: {mostrar_status(status).encode('utf-8')}")

        elif resposta == ('SAIR'):
          sair = True
          print('Saindo da aplicação...')
          break
          motorista.close()
        else:
          print('Comando não identificado') # isso ainda precisa ser tratado..
          motorista.sendall('ERRO! Comando não identificado'.encode('utf-8'))
        motorista.close()

servidor()





    