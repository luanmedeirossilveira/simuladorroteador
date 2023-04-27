import random
import threading
from classes.pacote_ip import PacoteIP
from classes.roteador import Roteador
roteador = Roteador()

# Interfaces
def gerar_pacotes():
  
  interfaces = [
    roteador.interface1, roteador.interface2, roteador.interface3,
    roteador.interface4
  ]

  # Tabela de roteamento
  roteador.atualiza_tabela_roteamento("10.0.0.0/24", roteador.interface1, 1)
  roteador.atualiza_tabela_roteamento("172.16.0.0/16", roteador.interface2, 1)
  roteador.atualiza_tabela_roteamento("192.168.0.0/16", roteador.interface3, 1)
  roteador.atualiza_tabela_roteamento("0.0.0.0/0", roteador.interface4, 1)

  for interface in interfaces:
    origem = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
    destino = f"10.0.{random.randint(1, 255)}.{random.randint(1, 255)}"
    ttl = random.randint(1, 10) 
    tos = random.randint(0, 255)

    pacote = PacoteIP(origem, destino, ttl, tos)
    interface.append(pacote)


# Iniciar as threads para as interfaces de rede
for interface in roteador.interface1:
  threading.Thread(target=interface.enviar_pacote,
                   args=(None, interface)).start()
  
for interface in roteador.interface2:
  threading.Thread(target=interface.enviar_pacote,
                   args=(None, interface)).start()

for interface in roteador.interface3:
  threading.Thread(target=interface.enviar_pacote,
                   args=(None, interface)).start()

for interface in roteador.interface4:
  threading.Thread(target=interface.enviar_pacote,
                   args=(None, interface)).start()

# Iniciar a thread para a geração de pacotes IP simulados
threading.Thread(target=gerar_pacotes).start()
