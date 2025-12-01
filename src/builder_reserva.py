from builder_locacao import Locacao
from builder_veiculo_manutencao import Veiculo
from builder_client_func import Cliente, Funcionario
from builder_pagamento import Pagamento
from datetime import date

class Reserva:

    def __init__(self, cliente: Cliente, veiculo: Veiculo, data_reserva, data_devolucao, id=None):
        self._id = id
        
        self._cliente = cliente
        self._veiculo = veiculo
        self._data_reserva = data_reserva
        self._data_devolucao = data_devolucao
        
        self._valor_total_previsto = self.calcular_custo_previsto()
        self._pagamentos = []
        self._status = "pendente"

    @property
    def id(self):
        return self._id

    @property
    def valor_total_previsto(self):
        return self._valor_total_previsto

    @property
    def data_reserva(self):
        return self._data_reserva

    @property
    def data_devolucao(self):
        return self._data_devolucao

    def calcular_custo_previsto(self):
        diferenca = self._data_devolucao - self._data_reserva
        dias = diferenca.days
        dias = 1 if dias == 0 else dias 
            
        if dias < 0:
            raise ValueError("Data de devolução inválida.")
            
        total = dias * self._veiculo.valor_diaria
        return total

    @data_reserva.setter
    def data_reserva(self, nova_data):
        if isinstance(nova_data, date):
            self._data_reserva = nova_data
            if hasattr(self, '_data_devolucao'):
                self._valor_total_previsto = self.calcular_custo_previsto()
        else:
            raise TypeError("data_reserva deve ser um objeto datetime.date.")

    @data_devolucao.setter
    def data_devolucao(self, nova_data):
        if isinstance(nova_data, date):
            if nova_data >= self._data_reserva:
                self._data_devolucao = nova_data
                self._valor_total_previsto = self.calcular_custo_previsto()
            else:
                raise ValueError("A data de devolução não pode ser anterior à data da reserva.")
        else:
            raise TypeError("data_devolucao deve ser um objeto datetime.date.")

    def adicionar_pagamento(self, pagamento: Pagamento):
        self._pagamentos.append(pagamento)
        print(f"   Pagamento de R${pagamento._valor:.2f} ({pagamento._tipo}) adicionado.")
        print(f"   Total pago na reserva: R${self.total_pago():.2f}")


    def total_pago(self):
        return sum(p._valor for p in self._pagamentos)

    def iniciar_locacao(self, funcionario: 'Funcionario'):
        if self.total_pago() >= self._valor_total_previsto:
            self._status = "locado"
            self._veiculo.status = "alugado"
            
            nova_locacao = Locacao(
                reserva=self,
                data_retirada=date.today(),
                km_retirada=self._veiculo.kmatual,
                status="em andamento",
                funcionario=funcionario
            )
            return nova_locacao
        else:
            restante = self._valor_total_previsto - self.total_pago()
            raise ValueError(f"Pagamento insuficiente. Faltam R${restante:.2f}")
        
    def cancelar_reserva(self):
        """
        Cancela a reserva se ela estiver pendente e libera o veículo.
        """
        if self._status != "pendente":
            raise ValueError(f"Não é possível cancelar reserva com status '{self._status}'.")
        
        self._status = "cancelada"
        
        if self._veiculo:
            self._veiculo.status = "disponivel"
            
        print(f"Reserva {self._id} foi marcada como cancelada.")
 