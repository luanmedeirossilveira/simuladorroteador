from classes.pacote_ip import PacoteIP

TIPO_PACOTE_IP = 0
TIPO_PACOTE_ROTEAMENTO = 1


class Roteador:

  def __init__(self):
    self.interface1 = []
    self.interface2 = []
    self.interface3 = []
    self.interface4 = []
    self.tabela_roteamento = {}

  def atualiza_tabela_roteamento(self, rede_destino, interface_saida, metrica):
    self.tabela_roteamento[rede_destino] = (interface_saida, metrica)

  def analisa_cabecalho(self, pacote):
    if not isinstance(pacote, PacoteIP):
      print("Erro: o objeto não é um pacote IP")
      return

    if pacote.ttl <= 0:
      print("Pacote descartado: TTL expirado")
      return

    if pacote.destino not in self.interfaces:
      print(f"Pacote descartado: destino {pacote.destino} não encontrado")
      return

    print(
      f"Pacote recebido: origem {pacote.origem}, destino {pacote.destino}, TTL {pacote.ttl}, TOS {pacote.tos}"
    )

  def analisa_protocolo(self, pacote):
    """
    Analisa o protocolo do pacote de roteamento recebido e atualiza a tabela de roteamento
    """
    if pacote.protocolo == 'OSPF':
      # Atualiza a tabela de roteamento com as informações do pacote OSPF
      self.atualiza_tabela_roteamento(pacote.tabela_roteamento)
    elif pacote.protocolo == 'RIP':
      # Atualiza a tabela de roteamento com as informações do pacote RIP
      self.atualiza_tabela_roteamento(pacote.tabela_roteamento)
    else:
      print(f"Protocolo {pacote.protocolo} não suportado")

  def interpreta_funcoes(self, pacote):
    # Verifica o tipo de pacote
    if pacote.tipo == TIPO_PACOTE_IP:
      self.analisa_cabecalho(pacote)
    elif pacote.tipo == TIPO_PACOTE_ROTEAMENTO:
      self.analisa_protocolo(pacote)

  def encaminha_pacote(self, pacote):
    # Obter o endereço IP de destino do pacote
    endereco_destino = pacote.endereco_destino

    # Verificar se o endereço IP de destino está na tabela de roteamento
    if endereco_destino in self.tabela_roteamento:
      # Obter a interface de saída correspondente para o endereço de destino
      interface_saida = self.tabela_roteamento[endereco_destino]["interface"]

      # Verificar se a interface de saída está ativa
      if self.interfaces[interface_saida]["ativa"]:
        # Adicionar o pacote à fila de saída da interface de saída correspondente
        self.interfaces[interface_saida]["fila_saida"].append(pacote)
      else:
        # Interface de saída inativa, descartar o pacote
        print(
          f"Interface {interface_saida} inativa, descartando pacote: {pacote}")
    else:
      # Endereço de destino não encontrado na tabela de roteamento, descartar o pacote
      print(
        f"Endereço de destino {endereco_destino} não encontrado na tabela de roteamento, descartando pacote: {pacote}"
      )

  def inicializa_vetor_distancia(self):
    self.vetor_distancia = {}
    for destino in self.tabela_roteamento:
      self.vetor_distancia[destino] = self.tabela_roteamento[destino][2]
    self.vetor_distancia[self.endereco_ip] = 0

  def atualiza_vetor_distancia(self, pacote):
    if pacote.tipo == TIPO_PACOTE_ROTEAMENTO:
      origem = pacote.origem
      vetor_rota = pacote.conteudo
      for destino, metrica in vetor_rota.items():
        if destino not in self.vetor_distancia[origem] or self.vetor_distancia[
            origem][destino] > metrica + self.enlaces[origem][destino]:
          self.vetor_distancia[origem][
            destino] = metrica + self.enlaces[origem][destino]
          self.atualiza_tabela_roteamento()

  def algoritmo_vetor_distancia(self):
    # Inicializa o vetor de distância
    self.inicializa_vetor_distancia()

    # Executa o algoritmo até que a tabela de roteamento não mude mais
    while True:
      # Define uma flag para indicar se a tabela de roteamento mudou
      tabela_mudou = False

      # Percorre as redes de destino na tabela de roteamento
      for rede_destino in self.tabela_roteamento.keys():
        # Se a rede de destino for a própria rede do roteador, ignora
        if rede_destino == self.endereco_rede:
          continue

        # Inicializa a métrica mínima como infinito
        metrica_minima = float('inf')

        # Percorre as interfaces de rede do roteador para encontrar a melhor rota para a rede de destino
        for interface in self.interfaces_rede.values():
          # Obtém a entrada da tabela de roteamento para a rede de destino e a interface atual
          entrada_tabela = self.tabela_roteamento[(rede_destino,
                                                   interface.nome)]

          # Se a métrica da entrada da tabela for menor que a métrica mínima atual,
          # atualiza a métrica mínima e a interface de saída para a rede de destino
          if entrada_tabela['metrica'] < metrica_minima:
            metrica_minima = entrada_tabela['metrica']
            interface_saida = interface

        # Obtém a entrada atual da tabela de roteamento para a rede de destino
        entrada_tabela_atual = self.tabela_roteamento[(rede_destino,
                                                       interface_saida.nome)]

        # Inicializa a nova métrica como a métrica da entrada atual
        nova_metrica = entrada_tabela_atual['metrica']

        # Percorre as interfaces de rede do roteador para atualizar a tabela de roteamento para a rede de destino
        for interface in self.interfaces_rede.values():
          # Obtém a entrada atual da tabela de roteamento para a rede de destino e a interface atual
          entrada_tabela_atual = self.tabela_roteamento[(rede_destino,
                                                         interface.nome)]

          # Obtém a métrica para a interface atual
          metrica_interface = self.vetor_distancia[(interface.nome,
                                                    rede_destino)]

          # Calcula a nova métrica para a interface atual
          nova_metrica_interface = metrica_interface + self.vetor_distancia[
            (interface_saida.nome, interface.nome)]

          # Se a nova métrica for menor que a métrica atual da entrada da tabela, atualiza a entrada da tabela
          if nova_metrica_interface < nova_metrica:
            nova_metrica = nova_metrica_interface
            entrada_tabela_atual['metrica'] = nova_metrica
            entrada_tabela_atual['interface_saida'] = interface_saida

            # Define a flag para indicar que a tabela de roteamento mudou
            tabela_mudou = True

      # Se a tabela de roteamento não mudou, sai do loop
      if not tabela_mudou:
        break
