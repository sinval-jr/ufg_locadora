from datetime import date
from builder_veiculo_manutencao import Veiculo
from builder_pagamento import Pagamento

# -----------------------------------------------------------------
# CLASSE BASE
# -----------------------------------------------------------------
class Pessoa:
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, id = None):
        self.__id = id
        self.__nome = nome
        self.__telefone = telefone
        self.__email = email
        self.__rua = rua
        self.__numero = numero
        self.__cidade = cidade
        self.__estado = estado
        self.__cep = cep
    
    @property
    def id(self):
        return self.__id

    @property
    def nome(self):
        return self.__nome

    @property
    def telefone(self):
        return self.__telefone
    
    @property
    def rua(self):
        return self.__rua
    
    @property
    def numero(self):
        return self.__numero
    
    @property
    def cidade(self):
        return self.__cidade
    
    @property
    def estado(self):
        return self.__estado
    
    @property
    def cep(self):
        return self.__cep

    @telefone.setter
    def telefone(self, novo_telefone):
        if len(str(novo_telefone)) >= 8:
            self.__telefone = novo_telefone
        else:
            raise ValueError("Número de telefone inválido.")

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, novo_email):
        if "@" in novo_email:
            self.__email = novo_email
        else:
            raise ValueError("E-mail inválido.")

# -----------------------------------------------------------------
# ATORES (CLIENTE E FUNCIONÁRIO)
# -----------------------------------------------------------------
class Cliente(Pessoa):
    def __init__(self,nome, telefone, email, rua, numero, cidade, estado, cep, cpf, cnh, id = None):
        super().__init__(nome, telefone, email, rua, numero, cidade, estado, cep, id)
        self.__cpf = cpf
        self.__cnh = cnh

    @property
    def cpf(self):
        return self.__cpf

    @cpf.setter
    def cpf(self, novo_cpf):
        if len(str(novo_cpf)) == 11:
            self.__cpf = novo_cpf
        else:
            raise ValueError("Tamanho de CPF Inválido. Deve possuir 11 digitos!")

    @property
    def cnh(self):
        return self.__cnh

    @cnh.setter
    def cnh(self, novo_cnh):
        if novo_cnh.upper() in ["A", "B", "AB"]:
            self.__cnh = novo_cnh.upper()
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
        self.__matricula = matricula
        self.__cargo = cargo
        self.__salario = salario

    @property
    def matricula(self):
        return self.__matricula

    @property
    def cargo(self):
        return self.__cargo

    @property
    def salario(self):
        return self.__salario
    
    @cargo.setter
    def cargo(self, novo_cargo):
        if novo_cargo.lower() in ["atendente", "vendedor", "supervisor", "gerente"]:
            self.__cargo = novo_cargo
        else:
            raise ValueError("Cargo não Existente")

    @salario.setter
    def salario(self, novo_salario):
        if novo_salario >= 0:
            self.__salario = novo_salario
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
            print(f"✅ Locação [ID: {locacao.id}] registrada. Bom proveito, {reserva.cliente.nome}!")
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
        
        veiculo = locacao.reserva.veiculo
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
        self.__id = id
        self.__cliente = cliente
        self.__veiculo = veiculo
        self.__data_reserva = data_reserva
        self.__data_devolucao = data_devolucao
        self.__valor_total_previsto = self.calcular_custo_previsto()
        self.__pagamentos = []
        self.__status = "pendente"

    # propriedades públicas para compatibilidade
    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def cliente(self):
        return self.__cliente

    @cliente.setter
    def cliente(self, novo_cliente):
        self.__cliente = novo_cliente

    @property
    def veiculo(self):
        return self.__veiculo

    @property
    def valor_total_previsto(self):
        return self.__valor_total_previsto

    @property
    def pagamentos(self):
        return list(self.__pagamentos)

    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, novo_status):
        self.__status = novo_status.lower()

    def calcular_custo_previsto(self):
        diferenca = self.__data_devolucao - self.__data_reserva
        dias = diferenca.days
        dias = 1 if dias == 0 else dias 
            
        if dias < 0:
            raise ValueError("Data de devolução inválida.")
            
        total = dias * self.veiculo.valor_diaria
        return total
    
    @property
    def data_reserva(self):
        return self.__data_reserva

    @data_reserva.setter
    def data_reserva(self, nova_data):
        if isinstance(nova_data, date):
            self.__data_reserva = nova_data
            if hasattr(self, '_Reserva__data_devolucao'):
                self.__valor_total_previsto = self.calcular_custo_previsto()
        else:
            raise TypeError("data_reserva deve ser um objeto datetime.date.")

    @property
    def data_devolucao(self):
        return self.__data_devolucao

    @data_devolucao.setter
    def data_devolucao(self, nova_data):
        if isinstance(nova_data, date):
            if nova_data >= self.__data_reserva:
                self.__data_devolucao = nova_data
                self.__valor_total_previsto = self.calcular_custo_previsto()
            else:
                raise ValueError("A data de devolução não pode ser anterior à data da reserva.")
        else:
            raise TypeError("data_devolucao deve ser um objeto datetime.date.")

    def adicionar_pagamento(self, pagamento: Pagamento):
        
        if pagamento.tipo != "reserva":
            raise ValueError("O pagamento deve ser do tipo 'reserva' para ser adicionado aqui.")
        self.__pagamentos.append(pagamento)
        if self.total_pago() >= self.__valor_total_previsto:
            if self.__status != "finalizado": # Evita mudar se já estiver finalizada
                self.__status = "finalizado"
                # Esta mensagem será exibida na execução, confirmando a mudança
                print("🚨 Status da Reserva alterado para 'finalizado' (Pagamento integral recebido).")
        


    def total_pago(self):
        return sum(p.valor for p in self.__pagamentos)

    def iniciar_locacao(self, funcionario: 'Funcionario'):
        if self.total_pago() >= self.__valor_total_previsto:
            self.status = "locado"
            self.veiculo.status = "alugado"
            
            nova_locacao = Locacao(
                reserva=self,
                data_retirada=date.today(),
                km_retirada=self.veiculo.kmatual,
                status="em andamento",
                funcionario=funcionario
            )
            return nova_locacao
        else:
            restante = self.valor_total_previsto - self.total_pago()
            raise ValueError(f"Pagamento insuficiente. Faltam R${restante:.2f}")
        
    def cancelar_reserva(self):
        """
        Cancela a reserva se ela estiver pendente e libera o veículo.
        """
        if self.__status != "pendente":
            raise ValueError(f"Não é possível cancelar reserva com status '{self._status}'.")
        
        self.__status = "cancelada"
        
        if self.veiculo:
            self.veiculo.status = "disponivel"
            
        print(f"Reserva {self._id} foi marcada como cancelada.")


class Locacao:
    
    def __init__(self, reserva: Reserva, data_retirada, km_retirada, status, funcionario: Funcionario = None, id=None):
        self.__id = id
        self.__reserva = reserva
        self.__data_retirada = data_retirada
        self.__km_retirada = km_retirada
        self.__status = status
        self.__data_devolucao_real = None
        self.__km_devolucao = None
        self.__custo_extra_km = 0.0,
        self.__funcionario = funcionario

    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def reserva(self):
        return self.__reserva
    
    @reserva.setter
    def reserva(self, reserva):
        self.__reserva = reserva
    
    @property
    def km_retirada(self):
        return self.__km_retirada
    
    @property
    def status(self):
        return self.__status
    
    @status.setter
    def status(self, status):
        self.__status = status
    
    @property
    def km_devolucao(self):
        return self.__km_devolucao
    
    @km_devolucao.setter
    def km_devolucao(self, km_devolucao):
        self.__km_devolucao = km_devolucao

    @property
    def data_retirada(self):
        return self.__data_retirada
    
    @property
    def custo_extra_km(self):
        return self.__custo_extra_km
    
    @custo_extra_km.setter
    def custo_extra_km(self, custo_extra_km):
        self.__custo_extra_km = custo_extra_km
    
    @property
    def data_devolucao_real(self):
        return self.__data_devolucao_real
    
    @data_devolucao_real.setter
    def data_devolucao_real(self, data_devolucao_real):
        self.__data_devolucao_real = data_devolucao_real
    
    @property
    def funcionario(self):
        return self.__funcionario

    def encerrar(self, km_atual, data_entrega, preco_por_km):
        self.km_devolucao = km_atual
        self.data_devolucao_real = data_entrega
        
        km_inicial = self.km_retirada if self.km_retirada else 0
        km_rodados = self.km_devolucao - km_inicial
        
        if km_rodados < 0:
            raise ValueError("Erro: KM de devolução menor que o de retirada.")

        custo_km = km_rodados * preco_por_km
        self.custo_extra_km = custo_km
        
        self.reserva.veiculo.kmatual = km_atual
        self.reserva.veiculo.status = "disponivel"
        self.status = "finalizada"
        
        return custo_km 

    def realizar_pagamento_final(self, metodo_pagamento):
        if self.custo_extra_km > 0:
            pagamento_extra = Pagamento(metodo_pagamento, self.custo_extra_km, date.today(), "fechamento")
            
            self.reserva.adicionar_pagamento(pagamento_extra)
        else:
            print("   Sem saldo devedor para encerramento.")

    def emitir_recibo(self, funcionario_final: Funcionario):
        cliente = self.reserva.cliente
        veiculo = self.reserva.veiculo
        pagamentos = self.reserva.pagamentos
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
        print(f"Retirada:  {self.data_retirada} (KM: {self.km_retirada})")
        print(f"Devolução: {self.data_devolucao_real} (KM: {self.km_devolucao})")
        
        total_rodado = (self.km_devolucao or 0) - (self.km_retirada or 0)
        print(f"Total Rodado: {total_rodado} Km")
        
        print("-" * 45)
        print(f"{'DETALHAMENTO FINANCEIRO':^45}")
        print("-" * 45)
        
        print(f"Valor Diárias:".ljust(30, '.') + f" R$ {self.reserva.valor_total_previsto:.2f}")
        print(f"Custo KM Extra:".ljust(30, '.') + f" R$ {self.custo_extra_km:.2f}")
        print("-" * 45)

        for i, p in enumerate(pagamentos, 1):
            desc = f"Pagto {i} ({p.tipo.upper()} / {p.metodo})"
            print(f"{desc}".ljust(30, '.') + f" R$ {p._valor:.2f}")
        
        print("." * 45)
        total_geral = self.reserva.total_pago()
        print(f"TOTAL PAGO:".ljust(30) + f" R$ {total_geral:.2f}")
        print("="*45 + "\n")
