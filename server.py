# --------------- Imports
import socket
import numpy as np
import threading
import time
import random
import json


# --------------- Para impedir que haja 'competição' entre as  threads, vamos usar o lock para isso

max_conexoes = 2
conexoes_ativas = 0
lock_conexoes = threading.Lock()
lock_dados = threading.Lock()

# --------------- Parte 1: Gerar Eventos de Corrida

def gerar_evento(client, dados):
    primeira_corrida = True 
    
    while not dados['sair']: 
        try:
            espera = 0 if primeira_corrida else 10
            time.sleep(espera)
            
            # interrompe o programa se sair = True
            if dados['sair'] == True:
                break

            # chamando a função de gerar evento e calculando valor atual
            if dados['status'] == True:
                dist_inicial = np.random.randint(1, 20)
                dist_total = np.random.randint(1, 100)
                
                dados['valor_atual'] = round((dist_total * 2.50) * 0.25, 2)
                
                notif = (f"\n--- OLÁ MOTORISTA! ---\nDistância Inicial: {dist_inicial} Km\n"
                         f"Distância Corrida: {dist_total} Km\n"
                         f"Valor: R$ {dados['valor_atual']}\n")
                
                client.sendall(notif.encode('utf-8'))
                

                # se passar 8 segundos e cliente ainda não aceitou
                time.sleep(8)
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
                client.sendall('\n[Finalize ou cancele a corrida atual para receber novas!]'.encode('utf-8'))
                time.sleep(5)
                # ou seja, aqui só envia novas corridas se o status for True (disponível)
            
        except (OSError, ConnectionResetError):
            break

# --------------- Parte 2: Receber Comandos

def recebe_comando(client, data, dados, dicio_base):
    global conexoes_ativas

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
                  
        except Exception as e:
            print('Erro:', e)
            break


    client.close()

    # quando ele sair, vamos diminuir as conexões
    with lock_conexoes:
        conexoes_ativas -= 1



# --------------- Servidor Completo
def servidor(dicio_base, host='localhost', port=8082): # operação local, porta TCP/UDP (local host indica basicamente o IP da nossa máquina)
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

        # ------ verificação do limite de conexões
        with lock_conexoes:
            if conexoes_ativas >= max_conexoes:
                motorista.sendall('LIMITE ATINGIDO.'.encode('utf-8'))
                motorista.close()
                continue
            else:
                conexoes_ativas += 1
                motorista.sendall('OK.'.encode('utf-8'))
                
        nome_motorista = motorista.recv(2048).decode('utf-8')

        # ------ testando se o motorista atual está na lista, caso não, botamos ele lá
        if nome_motorista not in dicio_base:
            dicio_base[nome_motorista] = {
                'valor_atual': 0,
                'saldo_total': 0,
                'status': True,
                'sair': False
            }

            # ------ salvamos o novo motorista usando o lock para evitar concorrência
            with lock_dados:
                with open("saldos.json", "w") as arquivo:
                    json.dump(dicio_base, arquivo, indent=4)
                    

        dados_motorista = dicio_base[nome_motorista]
        dados_motorista['sair'] = False


        # ------ thread 2 - gerar eventos de corrida
        thread2_evento = threading.Thread(target=gerar_evento, args=(motorista, dados_motorista) ) # parâmetro da função gerar evento
        thread2_evento.start()


        # ------ thread 1 - receber comando E atualiza a fila de motoristas (À SER FEITO)
        thread1_recebe = threading.Thread(target=recebe_comando, args=(motorista, carga_dados, dados_motorista, dicio_base) ) # parâmetro da função gerar evento
        thread1_recebe.start()


# --------------- Execução do Programa
if __name__ == "__main__":

    # ------ primeiramente tentamos abrir o arquivo se ele existe, caso não, criamos um dicionário vazio
    try:
        with open("saldos.json", "r") as arquivo:
            dicio_base = json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        dicio_base = {}

    # ------ caso dê algum problema, ao menos vai ficar salvo no arquivo
    try: 
        servidor(dicio_base)
    except KeyboardInterrupt:
        print('Servidor interrompido pelo motorista.')
        with lock_dados:
            with open("saldos.json", "w") as f:
                json.dump(dicio_base, f, indent=4)
        print("Dados salvos. Encerrando programa...")
 