#Cliente faz reserva → paga → funcionário entrega → cliente devolve → sistema calcula custos → funcionário finaliza e emite recibo.

#Bibliotecas importadas
import sqlite3
from datetime import date

# -----------------------------------------------------------------
# CLASSE BASE
# -----------------------------------------------------------------
class Pessoa:
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, id=None):
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
# CLASSES DE ENTIDADE
# -----------------------------------------------------------------
class Veiculo:
    def __init__(self, placa, modelo, status, kmatual, valor_diaria, preco_por_km, id=None):
        self.__id = id
        self.__placa = placa
        self.__modelo = modelo
        self.__status = status
        self.__kmatual = kmatual
        self.__valor_diaria = valor_diaria
        self.__preco_por_km = preco_por_km

    @property
    def id(self):
        return self.__id

    @property
    def placa(self):
        return self.__placa

    @property
    def modelo(self):
        return self.__modelo

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, novo_status):
        status_veiculo = ["disponivel", "reservado", "alugado", "manutencao", "indisponivel"]
        if novo_status.lower() in status_veiculo:
            self.__status = novo_status.lower()
        else:
            raise ValueError("Status inválido!")

    @property
    def kmatual(self):
        return self.__kmatual

    @kmatual.setter
    def kmatual(self, novo_km):
        if novo_km >= self.__kmatual:
            self.__kmatual = novo_km
        else:
            raise ValueError("Nova kilometragem menor que a anterior")

    @property
    def valor_diaria(self):
        return self.__valor_diaria

    @valor_diaria.setter
    def valor_diaria(self, novo_valor):
        if novo_valor > 0:
            self.__valor_diaria = novo_valor
        else:
            raise ValueError("O valor da diária deve ser positivo.")

    @property
    def preco_por_km(self):
        return self.__preco_por_km

# -----------------------------------------------------------------
class Manutencao:
    def __init__(self, veiculo: Veiculo, descricao: str, data_inicio: date, custo: float = 0.0, id: int = None):
        self.__id = id
        self.__veiculo = veiculo
        self.__descricao = descricao
        self.__data_inicio = data_inicio
        self.__data_fim = None
        self.__custo = custo
        self.__status = "em andamento"

    @property
    def id(self):
        return self.__id

    @property
    def custo(self):
        return self.__custo

    @custo.setter
    def custo(self, novo_custo):
        if novo_custo >= 0:
            self.__custo = novo_custo
        else:
            raise ValueError("O custo não pode ser negativo.")

    def iniciar(self):
        if self.__veiculo.status != "disponivel":
            raise ValueError(f"Veículo {self.__veiculo.placa} não está disponível para manutenção (Status: {self.__veiculo.status}).")
        self.__status = "em andamento"
        self.__veiculo.status = "manutencao"
        print(f"Veículo {self.__veiculo.placa} enviado para manutenção.")

    def concluir(self, data_conclusao: date, custo_final: float):
        if self.__status != "em andamento":
            raise ValueError("Esta manutenção já foi concluída.")
        self.__status = "concluida"
        self.__data_fim = data_conclusao
        self.__custo = custo_final
        self.__veiculo.status = "disponivel"
        print(f"Manutenção (ID: {self.__id}) concluída. Veículo {self.__veiculo.placa} está 'disponivel'.")

# -----------------------------------------------------------------
# ATORES (CLIENTE E FUNCIONÁRIO)
# -----------------------------------------------------------------
class Cliente(Pessoa):
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, cpf, cnh, id=None):
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
        print(f"--- Cliente {self.nome} iniciando reserva (ex: via site) ---")
        if veiculo.status != "disponivel":
            raise ValueError(f"Desculpe, o veículo {veiculo.modelo} não está disponível (Status: {veiculo.status}).")
        nova_reserva = Reserva(cliente=self, veiculo=veiculo, data_reserva=data_inicio, data_devolucao=data_fim)
        veiculo.status = "reservado"
        print(f"✅ Reserva [ID: {nova_reserva.id}] criada com sucesso.")
        print(f"   Veículo {veiculo.modelo} agora está 'reservado' aguardando pagamento.")
        return nova_reserva


class Funcionario(Pessoa):
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, matricula, cargo, salario, id=None):
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
        print(f"--- Atendente {self.nome} REGISTRANDO LOCAÇÃO (entregando veículo) ---")
        try:
            locacao = reserva.iniciar_locacao()
            print(f"✅ Locação [ID: {locacao.id}] registrada. Bom proveito, {reserva.cliente.nome}!")
            if reserva.funcionario is None:
                reserva.funcionario = self
                print(f"   Atendente {self.nome} agora associado à reserva {reserva.id}.")
            return locacao
        except ValueError as e:
            print(f"❌ ERRO NA ENTREGA: {e}")
            return None

    def finalizar_locacao(self, locacao: 'Locacao', km_devolucao: int, metodo_pagamento_final: str):
        print(f"--- Atendente {self.nome} recebendo veículo ---")
        veiculo = locacao.reserva.veiculo
        custo_km_extra = locacao.encerrar(km_atual=km_devolucao, data_entrega=date.today(), preco_por_km=veiculo.preco_por_km)
        print(f"   Veículo {veiculo.modelo} devolvido. Status: {veiculo.status}")
        if custo_km_extra > 0:
            print(f"   Custo extra de R$ {custo_km_extra:.2f} (KM) a ser pago.")
            locacao.realizar_pagamento_final(metodo_pagamento_final)
        else:
            print("   Sem custos extras de quilometragem.")
        locacao.emitir_recibo(funcionario_final=self)

# -----------------------------------------------------------------
# CLASSES DE TRANSAÇÃO (PAGAMENTO, RESERVA, LOCAÇÃO)
# -----------------------------------------------------------------
class Pagamento:
    def __init__(self, metodo, valor, data_pagamento, tipo="inicial", id=None):
        self.__id = id
        self.__metodo = metodo
        self.__valor = valor
        self.__data_pagamento = data_pagamento
        self.__tipo = tipo

    @property
    def metodo(self):
        return self.__metodo

    @property
    def valor(self):
        return self.__valor

    @property
    def tipo(self):
        return self.__tipo

    def __repr__(self):
        return f"Pagamento({self.__tipo}: R$ {self.__valor:.2f} via {self.__metodo})"

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
        self.__funcionario = None

    # propriedades públicas para compatibilidade
    @property
    def id(self):
        return self.__id

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

    @property
    def funcionario(self):
        return self.__funcionario

    @funcionario.setter
    def funcionario(self, func):
        self.__funcionario = func

    def calcular_custo_previsto(self):
        diferenca = self.__data_devolucao - self.__data_reserva
        dias = diferenca.days
        dias = 1 if dias == 0 else dias
        if dias < 0:
            raise ValueError("Data de devolução inválida.")
        total = dias * self.__veiculo.valor_diaria
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
        self.__pagamentos.append(pagamento)
        print(f"   Pagamento de R${pagamento.valor:.2f} ({pagamento.tipo}) adicionado.")
        print(f"   Total pago na reserva: R${self.total_pago():.2f}")

    def total_pago(self):
        return sum(p.valor for p in self.__pagamentos)

    def iniciar_locacao(self):
        if self.total_pago() >= self.__valor_total_previsto:
            self.__status = "locado"
            self.__veiculo.status = "alugado"
            nova_locacao = Locacao(reserva=self, data_retirada=date.today(), km_retirada=self.__veiculo.kmatual, status="em andamento")
            return nova_locacao
        else:
            restante = self.__valor_total_previsto - self.total_pago()
            raise ValueError(f"Pagamento insuficiente. Faltam R${restante:.2f}")

    def cancelar_reserva(self):
        if self.__status != "pendente":
            raise ValueError(f"Não é possível cancelar reserva com status '{self.__status}'.")
        self.__status = "cancelada"
        if self.__veiculo:
            self.__veiculo.status = "disponivel"
        print(f"Reserva {self.__id} foi marcada como cancelada.")

class Locacao:
    def __init__(self, reserva: Reserva, data_retirada, km_retirada, status, id=None):
        self.__id = id
        self.__reserva = reserva
        self.__data_retirada = data_retirada
        self.__km_retirada = km_retirada
        self.__status = status
        self.__data_devolucao_real = None
        self.__km_devolucao = None
        self.__custo_extra_km = 0.0

    @property
    def id(self):
        return self.__id

    @property
    def reserva(self):
        return self.__reserva

    @property
    def data_retirada(self):
        return self.__data_retirada

    def encerrar(self, km_atual, data_entrega, preco_por_km):
        self.__km_devolucao = km_atual
        self.__data_devolucao_real = data_entrega
        km_inicial = self.__km_retirada if self.__km_retirada else 0
        km_rodados = self.__km_devolucao - km_inicial
        if km_rodados < 0:
            raise ValueError("Erro: KM de devolução menor que o de retirada.")
        custo_km = km_rodados * preco_por_km
        self.__custo_extra_km = custo_km
        # atualiza veículo e status
        self.__reserva.veiculo.kmatual = km_atual
        self.__reserva.veiculo.status = "disponivel"
        self.__status = "finalizada"
        return custo_km

    def realizar_pagamento_final(self, metodo_pagamento):
        if self.__custo_extra_km > 0:
            pagamento_extra = Pagamento(metodo_pagamento, self.__custo_extra_km, date.today(), "fechamento")
            self.__reserva.adicionar_pagamento(pagamento_extra)
        else:
            print("   Sem saldo devedor para encerramento.")

    def emitir_recibo(self, funcionario_final: Funcionario):
        cliente = self.__reserva.cliente
        veiculo = self.__reserva.veiculo
        pagamentos = self.__reserva.pagamentos
        funcionario = funcionario_final
        print("" + "="*45)
        print(f"{'RECIBO FINAL DE LOCAÇÃO':^45}")
        print("="*45)
        print(f"CLIENTE: {cliente.nome} (CPF: {cliente.cpf})")
        if funcionario:
            print(f"ATENDENTE: {funcionario.nome} (Mat: {funcionario.matricula})")
        else:
            print(f"ATENDENTE: Reserva online (sem atendente inicial)")
        print("-" * 45)
        print(f"VEÍCULO: {veiculo.modelo} (Placa: {veiculo.placa})")
        print(f"Retirada:  {self.__data_retirada} (KM: {self.__km_retirada})")
        print(f"Devolução: {self.__data_devolucao_real} (KM: {self.__km_devolucao})")
        total_rodado = (self.__km_devolucao or 0) - (self.__km_retirada or 0)
        print(f"Total Rodado: {total_rodado} Km")
        print("-" * 45)
        print(f"{'DETALHAMENTO FINANCEIRO':^45}")
        print("-" * 45)
        print(f"Valor Diárias:".ljust(30, '.') + f" R$ {self.__reserva.valor_total_previsto:.2f}")
        print(f"Custo KM Extra:".ljust(30, '.') + f" R$ {self.__custo_extra_km:.2f}")
        print("-" * 45)
        for i, p in enumerate(pagamentos, 1):
            desc = f"Pagto {i} ({p.tipo.upper()} / {p.metodo})"
            print(f"{desc}".ljust(30, '.') + f" R$ {p.valor:.2f}")
        print("." * 45)
        total_geral = self.__reserva.total_pago()
        print(f"TOTAL PAGO:".ljust(30) + f" R$ {total_geral:.2f}")
        print("="*45 + "\n")
