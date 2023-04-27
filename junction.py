import threading
import time
import random
import pandas as pd
from queue import Queue

# Classe para representar uma interface de rede do roteador
class InterfaceRede:
    def __init__(self, nome):
        self.nome = nome
        self.fila_entrada = Queue()
    
    def enviar_pacote(self, pacote, interface_destino):
        print(f"Pacote de {pacote.origem} para {pacote.destino} enviado de {self.nome} para {interface_destino.nome}")
        interface_destino.fila_entrada.put(pacote)

# Classe para representar um pacote IP
class PacoteIP:
    def __init__(self, origem, destino, ttl, tos):
        self.origem = origem # Endereço de origem
        self.destino = destino # Endereço de destino
        self.ttl = ttl # Tempo de vida do pacote
        self.tos = tos # Tipo de serviço do pacote

# Classe para representar o roteador
class Roteador:
    def __init__(self, nome):
        self.nome = nome
        self.interfaces = {
            "Interface1": InterfaceRede("Interface1"),
            "Interface2": InterfaceRede("Interface2"),
            "Interface3": InterfaceRede("Interface3"),
            "Interface4": InterfaceRede("Interface4")
        }

    def receber_pacote(self, interface_origem, pacote):
        print(f"Pacote de {pacote.origem} para {pacote.destino} recebido em {self.nome} na interface {interface_origem}")

    def encaminhar_pacote(self, pacote):
        destino = pacote.destino

        if destino in self.tabela_roteamento:
            interface_saida, metrica = self.tabela_roteamento[destino]

            if interface_saida in self.interfaces:
                self.interfaces[interface_saida].fila_entrada.put(pacote)
                print(f"Pacote para {destino} encaminhado para {interface_saida} (Métrica: {metrica})")
            else:
                print(f"Interface de saída {interface_saida} não encontrada")
        else:
            print(f"Destino {destino} não encontrado na tabela de roteamento")


        tabela_roteamento = {
            "rede1": ("Interface1", 1),
            "rede2": ("Interface2", 2),
            "rede3": ("Interface3", 3),
            "rede4": ("Interface4", 4)
        }

        if pacote.destino in tabela_roteamento:
            interface_destino, metrica = tabela_roteamento[pacote.destino]
            self.interfaces[interface_destino].enviar_pacote(pacote, self.interfaces[interface_destino])
        else:
            print(f"Pacote de {pacote.origem} para {pacote.destino} descartado em {self.nome} (destino desconhecido)")

    def executar(self):
        print(f"Roteador {self.nome} em execução...")
df = pd.read_csv('dados.csv')
df.drop_duplicates(inplace=True)


# Função para gerar pacotes IP simulados
def gerar_pacotes():
  while True:
    origem = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    destino = f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
    ttl = random.randint(1, 10)
    tos = random.randint(0, 255)
    pacote = PacoteIP(origem, destino, ttl, tos)
    interface_origem = random.choice(list(roteador.interfaces.values()))
    interface_origem.fila_entrada.put(pacote)
    print(
      f"Pacote de {origem} para {destino} gerado em {interface_origem.nome}")
    time.sleep(1)

# Instanciar o roteador
roteador = Roteador("Roteador1")

# Iniciar as threads para as interfaces de rede
for interface in roteador.interfaces.values():
  threading.Thread(target=interface.enviar_pacote,
                   args=(None, interface)).start()

# Iniciar a thread para a geração de pacotes IP simulados
threading.Thread(target=gerar_pacotes).start()

# Iniciar a execução do roteador
roteador.executar()
