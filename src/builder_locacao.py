from builder_reserva import Reserva
from builder_pagamento import Pagamento
from builder_client_func import Funcionario
from datetime import date

class Locacao:
    
    def __init__(self, reserva: Reserva, data_retirada, km_retirada, status, funcionario: Funcionario = None, id=None):
        self._id = id
        
        self._reserva = reserva
        self._data_retirada = data_retirada
        self._km_retirada = km_retirada
        self._status = status
        self._funcionario = funcionario
        
        self._data_devolucao_real = None
        self._km_devolucao = None
        self._custo_extra_km = 0.0

    @property
    def id(self):
        return self._id

    def encerrar(self, km_atual, data_entrega, preco_por_km):
        self._km_devolucao = km_atual
        self._data_devolucao_real = data_entrega
        
        km_inicial = self._km_retirada if self._km_retirada else 0
        km_rodados = self._km_devolucao - km_inicial
        
        if km_rodados < 0:
            raise ValueError("Erro: KM de devolução menor que o de retirada.")

        custo_km = km_rodados * preco_por_km
        self._custo_extra_km = custo_km
        
        self._reserva._veiculo.kmatual = km_atual
        self._reserva._veiculo.status = "disponivel"
        self._status = "finalizada"
        
        return custo_km 

    def realizar_pagamento_final(self, metodo_pagamento):
        if self._custo_extra_km > 0:
            pagamento_extra = Pagamento(metodo_pagamento, self._custo_extra_km, date.today(), "fechamento")
            self._reserva.adicionar_pagamento(pagamento_extra)
        else:
            print("   Sem saldo devedor para encerramento.")

    def emitir_recibo(self, funcionario_final: Funcionario):
        cliente = self._reserva._cliente
        veiculo = self._reserva._veiculo
        pagamentos = self._reserva._pagamentos
        funcionario = funcionario_final
        
        print("\n" + "="*45)
        print(f"{'RECIBO FINAL DE LOCAÇÃO':^45}")
        print("="*45)
        
        print(f"CLIENTE: {cliente.nome} (CPF: {cliente.cpf})")
        
        if funcionario:
            print(f"ATENDENTE: {funcionario.nome} (Mat: {funcionario.matricula})")
        else:
            print(f"ATENDENTE: Reserva online (sem atendente inicial)")
            
        print("-" * 45)
        print(f"VEÍCULO: {veiculo.modelo} (Placa: {veiculo.placa})")
        print(f"Retirada:  {self._data_retirada} (KM: {self._km_retirada})")
        print(f"Devolução: {self._data_devolucao_real} (KM: {self._km_devolucao})")
        
        total_rodado = (self._km_devolucao or 0) - (self._km_retirada or 0)
        print(f"Total Rodado: {total_rodado} Km")
        
        print("-" * 45)
        print(f"{'DETALHAMENTO FINANCEIRO':^45}")
        print("-" * 45)
        
        print(f"Valor Diárias:".ljust(30, '.') + f" R$ {self._reserva.valor_total_previsto:.2f}")
        print(f"Custo KM Extra:".ljust(30, '.') + f" R$ {self._custo_extra_km:.2f}")
        print("-" * 45)

        for i, p in enumerate(pagamentos, 1):
            desc = f"Pagto {i} ({p._tipo.upper()} / {p._metodo})"
            print(f"{desc}".ljust(30, '.') + f" R$ {p._valor:.2f}")
        
        print("." * 45)
        total_geral = self._reserva.total_pago()
        print(f"TOTAL PAGO:".ljust(30) + f" R$ {total_geral:.2f}")
        print("="*45 + "\n")
