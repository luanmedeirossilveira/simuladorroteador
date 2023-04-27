from collections import deque

class Interface:
  def __init__(self):
    # inicializa a fila de entrada da interface
    self.input_queue = deque()
      
  def receive_packet(self, packet):
    # adiciona o pacote à fila de entrada da interface
    self.input_queue.append(packet)
