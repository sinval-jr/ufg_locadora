from datetime import date
from builder_veiculo_manutencao import Veiculo
from builder_pagamento import Pagamento

# -----------------------------------------------------------------
# CLASSE BASE
# -----------------------------------------------------------------
class Pessoa:
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, id = None):
        self._id = id 
        self._nome = nome
        self._telefone = telefone
        self._email = email
        self._rua = rua
        self._numero = numero
        self._cidade = cidade
        self._estado = estado
        self._cep = cep
    
    @property
    def id(self):
        return self._id
    
    @property
    def nome(self):
        return self._nome

    @property
    def telefone(self):
        return self._telefone

    @telefone.setter
    def telefone(self, novo_telefone):
        if len(str(novo_telefone)) >= 8:
            self._telefone = novo_telefone
        else:
            raise ValueError("Número de telefone inválido.")

    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, novo_email):
        if "@" in novo_email:
            self._email = novo_email
        else:
            raise ValueError("E-mail inválido.")

# -----------------------------------------------------------------
# ATORES (CLIENTE E FUNCIONÁRIO)
# -----------------------------------------------------------------
class Cliente(Pessoa):
    def __init__(self,nome, telefone, email, rua, numero, cidade, estado, cep, cpf, cnh, id = None):
        super().__init__(nome, telefone, email, rua, numero, cidade, estado, cep, id)
        self._cpf = cpf
        self._cnh = cnh

    @property
    def cpf(self):
        return self._cpf

    @property
    def cnh(self):
        return self._cnh
    
    @cpf.setter
    def cpf(self, novo_cpf):
        # Validação simples
        if len(str(novo_cpf)) == 11:
            self._cpf = novo_cpf
        else:
            raise ValueError("Tamanho de CPF Inválido. Deve possuir 11 digitos!")
    
    @cnh.setter
    def cnh(self, novo_cnh):
        if novo_cnh.upper() in ["A", "B", "AB"]:
            self._cnh = novo_cnh.upper()
        else:
            raise ValueError("Tipo de CNH inválido.")

    # --- MÉTODO NOVO ---
    def fazer_reserva(self, veiculo: Veiculo, data_inicio: date, data_fim: date):
        """
        Ação do CLIENTE para criar uma reserva (ex: via site).
        Não há funcionário associado nesta etapa.
        """
        print(f"--- Cliente {self.nome} iniciando reserva (ex: via site) ---")
        
        # 1. Validação
        if veiculo.status != "disponivel":
            raise ValueError(f"Desculpe, o veículo {veiculo.modelo} não está disponível (Status: {veiculo.status}).")
        
        # 2. Criação (sem funcionário)
        nova_reserva = Reserva(
            cliente=self,
            veiculo=veiculo,
            data_reserva=data_inicio,
            data_devolucao=data_fim
        )
        
        # 3. Mudança de Estado
        veiculo.status = "reservado"
        print(f"✅ Reserva [ID: {nova_reserva.id}] criada com sucesso.")
        print(f"   Veículo {veiculo.modelo} agora está 'reservado' aguardando pagamento.")
        return nova_reserva


class Funcionario(Pessoa):
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, matricula, cargo, salario, id = None):
        super().__init__(nome, telefone, email, rua, numero, cidade, estado, cep, id)
        self._matricula = matricula
        self._cargo = cargo
        self._salario = salario

    @property
    def matricula(self):
        return self._matricula

    @property
    def cargo(self):
        return self._cargo

    @property
    def salario(self):
        return self._salario
    
    @cargo.setter
    def cargo(self, novo_cargo):
        if novo_cargo.lower() in ["atendente", "vendedor", "supervisor", "gerente"]:
            self._cargo = novo_cargo
        else:
            raise ValueError("Cargo não Existente")

    @salario.setter
    def salario(self, novo_salario):
        if novo_salario >= 0:
            self._salario = novo_salario
        else:
            raise ValueError("O salário não pode ser negativo.")

    # --- MÉTODOS DE NEGÓCIO DO FUNCIONÁRIO ---

    def entregar_veiculo(self, reserva: 'Reserva'):
        """
        Ação do funcionário para entregar o carro ao cliente.
        Aqui ele "registra" a locação, transformando a reserva em locação.
        """
        print(f"--- Atendente {self.nome} REGISTRANDO LOCAÇÃO (entregando veículo) ---")
        try:
            locacao = reserva.iniciar_locacao(self)
            print(f"✅ Locação [ID: {locacao.id}] registrada. Bom proveito, {reserva._cliente.nome}!")
                
            return locacao
        except ValueError as e:
            print(f"❌ ERRO NA ENTREGA: {e}")
            return None 

    def finalizar_locacao(self, locacao: 'Locacao', km_devolucao: int, metodo_pagamento_final: str):
        """
        Ação do funcionário para receber o veículo de volta, calcular custos
        de KM, processar o pagamento final e emitir o recibo.
        """
        print(f"--- Atendente {self.nome} recebendo veículo ---")
        
        veiculo = locacao._reserva._veiculo
        custo_km_extra = locacao.encerrar(
            km_atual=km_devolucao,
            data_entrega=date.today(),
            preco_por_km=veiculo.preco_por_km
        )
        
        print(f"   Veículo {veiculo.modelo} devolvido. Status: {veiculo.status}")
        
        if custo_km_extra > 0:
            print(f"   Custo extra de R$ {custo_km_extra:.2f} (KM) a ser pago.")
            locacao.realizar_pagamento_final(metodo_pagamento_final)
        else:
            print("   Sem custos extras de quilometragem.")
            
        locacao.emitir_recibo(funcionario_final=self)

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
        
        if pagamento.tipo != "reserva":
            raise ValueError("O pagamento deve ser do tipo 'reserva' para ser adicionado aqui.")
        self._pagamentos.append(pagamento)
        if self.total_pago() >= self._valor_total_previsto:
            if self._status != "finalizado": # Evita mudar se já estiver finalizada
                self._status = "finalizado"
                # Esta mensagem será exibida na execução, confirmando a mudança
                print("🚨 Status da Reserva alterado para 'finalizado' (Pagamento integral recebido).")
        


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
