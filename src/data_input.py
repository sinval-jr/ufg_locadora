import sqlite3
from datetime import date

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
        

class Veiculo:
    def __init__(self, placa, modelo, status, kmatual, id = None):
        self._id = id
        self._placa = placa
        self._modelo = modelo
        self._status = status
        self._kmatual = kmatual

    @property
    def id(self):
        return self._id
    
    @property
    def placa(self):
        return self._placa
    
    @property
    def status(self):
        return self._status
    
    @property
    def kmatual(self):
        return self._kmatual

    @status.setter
    def status(self,novo_status):
        status_veiculo = ["disponivel", "reservado", "alugado", "manutencao", "indisponivel"]
        if novo_status.lower() in status_veiculo:
            self._status = novo_status.lower()
        else:
            raise ValueError("Status inválido!")
    
    @kmatual.setter
    def kmatual(self, novo_km):
        if novo_km >= self._kmatual:
            self._kmatual = novo_km
        else:
            raise ValueError("Nova kilometragem menor que a anterior")
    
    def atualizar_status(self, novo_status):
        self.status = novo_status

    def registrar_manutencao(self, descricao, data_manutencao, custo, status):
        pass

    def disponivel_para_reserva(self):
        pass

    def incrementar_km(self, km):
        pass

class Manutencao:
    def __init__(self, descricao, data_manutencao, custo, id = None):
        self._id = id
        self._descricao = descricao
        self._data_manutencao = data_manutencao
        self._custo = custo

    @property
    def id(self):
        return self._id

    @property
    def data_manutencao(self):
        return self._data_manutencao
    
    @property
    def custo(self):
        return self._custo

    @data_manutencao.setter
    def data_manutencao(self, nova_data):
        if isinstance(nova_data, date):
            self._data_manutencao = nova_data
        else:
            raise TypeError("A data de manutenção deve ser um objeto datetime.date.")

    @custo.setter
    def custo(self, novo_custo):
        if novo_custo >= 0:
            self._custo = novo_custo
        else:
            raise ValueError("O custo não pode ser negativo.")

    def __str__(self):
        return f"Manutenção {self._id}: {self._descricao} (R${self._custo:.2f} em {self._data_manutencao})"

    def registrar_manutencao(self):
        pass

    def registrar_conclusao(self, data_conclusao):
        pass

    def gerar_relatorio(self):
        pass

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
        if len(str(novo_cpf)) == 11:
            self._cpf = novo_cpf
        else:
            raise ValueError("Tamanho de CPF Inválid. Deve possuir 11 digitos!")
    
    @cnh.setter
    def cnh(self, novo_cnh):
        if novo_cnh.upper() in ["A", "B", "AB"]:
            self._cnh = novo_cnh.upper()
        else:
            raise ValueError("Tipo de CNH inválido.")
    
    def alugar_veiculo(self, reserva):
        pass
    
    def devolver_veiculo(self, veiculo):
        pass

    def pagar_reserva(self, valor):
        pass

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

    def registrar_locacao(self, cliente, veiculo):
        pass
 
class Pagamento:
    def __init__(self, metodo, valor, data_pagamento, tipo="inicial", id=None):
        self._id = id
        self._metodo = metodo
        self._valor = valor
        self._data_pagamento = data_pagamento
        self._tipo = tipo  # "inicial" ou "fechamento"

    def __repr__(self):
        return f"Pagamento({self._tipo}: R$ {self._valor:.2f} via {self._metodo})"

class Reserva:
    def __init__(self, cliente: Cliente, veiculo: Veiculo,data_reserva, data_devolucao, valor, id = None):
        self._id = id
        self._cliente = cliente  # Objeto Cliente
        self._veiculo = veiculo  # Objeto Veiculo
        self._data_reserva = data_reserva
        self._data_devolucao = data_devolucao
        self._valor_diarias = valor # Valor previsto apenas das diárias
        self._pagamentos = [] # Lista para armazenar histórico de pagamentos
        self._status = "pendente"
    @property
    def id(self):
        return self._id

    @property
    def data_reserva(self):
        return self._data_reserva
    
    @property
    def data_devolucao(self):
        return self._data_devolucao
    
    @property
    def valor(self):
        return self._valor

    @data_reserva.setter
    def data_reserva(self, nova_data):
        if isinstance(nova_data, date):
            self._data_reserva = nova_data
        else:
            raise TypeError("data_reserva deve ser um objeto datetime.date.")

    @data_devolucao.setter
    def data_devolucao(self, nova_data):
        if isinstance(nova_data, date):
            if nova_data >= self._data_reserva:
                self._data_devolucao = nova_data
            else:
                raise ValueError("A data de devolução não pode ser anterior à data da reserva.")
        else:
            raise TypeError("data_devolucao deve ser um objeto datetime.date.")

    @valor.setter
    def valor(self, novo_valor):
        if novo_valor >= 0:
            self._valor = novo_valor
        else:
            raise ValueError("O valor da reserva não pode ser negativo.")

    def adicionar_pagamento(self, pagamento: Pagamento):
        self._pagamentos.append(pagamento)
        print(f"Pagamento de R${pagamento._valor} registrado na reserva.")

    def total_pago(self):
        return sum(p._valor for p in self._pagamentos)
    def iniciar_locacao(self):
        # Regra de Negócio: Só inicia se pagou pelo menos as diárias (exemplo)
        if self.total_pago() >= self._valor_diarias:
            self._status = "locado"
            self._veiculo.status = "alugado"
            
            # Cria o objeto Locação vinculando a esta reserva
            nova_locacao = Locacao(
                reserva=self,  # Passamos a PRÓPRIA reserva para a locação
                data_retirada=date.today(),
                km_retirada=self._veiculo.kmatual,
                status="em andamento"
            )
            return nova_locacao
        else:
            raise ValueError(f"Pagamento insuficiente. Faltam R${self._valor_diarias - self.total_pago()}")
        

    def confirmar_reserva(self):
        pass

    def cancelar_reserva(self):
        pass

    def gerar_recibo(self):
        pass

class Locacao:
    def __init__(self, reserva: Reserva, data_retirada, km_retirada, status, id=None):
        self._id = id
        self._reserva = reserva  # Vínculo com a reserva anterior
        self._data_retirada = data_retirada
        self._km_retirada = km_retirada
        self._status = status
        
        # Estes serão preenchidos no encerramento
        self._data_devolucao_real = None
        self._km_devolucao = None
        self._custo_extra_km = 0.0

    @property
    def id(self):
        return self._id

    @property
    def data_devolucao_prevista(self):
        return self._data_devolucao_prevista

    @property
    def data_devolucao_real(self):
        return self._data_devolucao_real
    
    @property
    def km_devolucao(self):
        return self._km_devolucao

    @property
    def status(self):
        return self._status
    
    @data_devolucao_real.setter
    def data_devolucao_real(self, nova_data):
        if isinstance(nova_data, date):
            if nova_data >= self._data_retirada:
                self._data_devolucao_real = nova_data
            else:
                raise ValueError("A data de devolução real não pode ser anterior à data da reserva.")
        else:
            raise TypeError("data_devolucao_raeldeve ser um objeto datetime.date.")
    
    @km_devolucao.setter
    def km_devolucao(self, novo_km):
        if novo_km >= self._km_devolucao:
            self._km_devolucao = novo_km
        else:
            raise ValueError("Nova kilometragem não pode ser menor que a antiga")
    
    @data_devolucao_prevista.setter
    def data_devolucao_prevista(self, nova_data):
        if isinstance(nova_data, date):
            if nova_data >= self._data_retirada:
                self._data_devolucao_prevista = nova_data
            else:
                raise ValueError("A data de devolução prevista não pode ser anterior à data da reserva.")
        else:
            raise TypeError("data_devolucao_prevista deve ser um objeto datetime.date.")

    @status.setter
    def status(self, novo_status):
        if novo_status.lower() in ["em andamento", "finalizada", "atrasada", "cancelada"]:
            self._status = novo_status
        else:
            raise ValueError("Novo status é inválido!")

    def encerrar(self, km_atual, data_entrega, preco_por_km):
        self._km_devolucao = km_atual
        self._data_devolucao_real = data_entrega
        
        # 1. Calcular KM rodado
        km_rodados = self._km_devolucao - self._km_retirada
        
        # 2. Calcular custo do KM (Regra de negócio simples)
        custo_km = km_rodados * preco_por_km
        self._custo_extra_km = custo_km
        
        # 3. Atualizar veículo
        self._reserva._veiculo.kmatual = km_atual
        self._reserva._veiculo.status = "disponivel"
        self._status = "finalizada"
        
        print(f"--- Fechamento de Contrato ---")
        print(f"Veículo: {self._reserva._veiculo.modelo}")
        print(f"KM Rodados: {km_rodados}km (R${custo_km:.2f})")
        print(f"Já pago na reserva: R${self._reserva.total_pago():.2f}")
        
        return custo_km
    
    def realizar_pagamento_final(self, metodo_pagamento):
        if self._custo_extra_km > 0:
            pagamento_extra = Pagamento(metodo_pagamento, self._custo_extra_km, date.today(), "fechamento")
            self._reserva.adicionar_pagamento(pagamento_extra)
            print("Pagamento final por KM realizado com sucesso!")
        else:
            print("Não há custo extra de KM a pagar.")

    def emitir_recibo(self):
        pass

    def iniciar(self):
        pass

    def encerrar(self):
        pass

    def calcular_custo_final(self):
        pass


if __name__ == "__main__":
    # 1. Criação das Entidades Básicas
    cliente1 = Cliente("João Silva", "12345678", "joao@gmail.com", "Rua A", 123, "Goiania", "GO", "74000000", "12345678901", "B")
    veiculo1 = Veiculo("ABC-1234", "Fiat Mobi", "disponivel", 10000)

    # 2. Cliente faz a RESERVA (Valor das diárias fixado em R$ 200,00)
    print(">>> 1. Criando Reserva")
    reserva = Reserva(
        cliente=cliente1, 
        veiculo=veiculo1, 
        data_reserva=date(2023, 10, 1), 
        data_devolucao=date(2023, 10, 5), 
        valor=200.00 
    )

    # 3. Pagamento ANTES da locação (Sinal/Diárias)
    print("\n>>> 2. Processando Pagamento Inicial")
    pagto_inicial = Pagamento("pix", 200.00, date.today(), "sinal")
    reserva.adicionar_pagamento(pagto_inicial)

    # 4. Iniciar a Locação (Retirada do veículo)
    # O sistema verifica se o pagamento inicial foi feito
    try:
        print("\n>>> 3. Retirando Veículo")
        locacao = reserva.iniciar_locacao()
        print(f"Locação iniciada! KM Inicial: {locacao._km_retirada}")
    except ValueError as e:
        print(f"Erro: {e}")

    # --- O Cliente viaja e volta ---

    # 5. Encerrar Locação (Devolução)
    # Cliente andou 500km. Preço por KM é R$ 0.50
    print("\n>>> 4. Devolvendo Veículo")
    custo_km = locacao.encerrar(km_atual=10500, data_entrega=date.today(), preco_por_km=0.50)

    # 6. Pagamento Final (Sobre o KM)
    if custo_km > 0:
        print("\n>>> 5. Pagamento do KM Excedente")
        locacao.realizar_pagamento_final("cartao de credito")

    print(f"\n>>> Status Final do Veículo: {veiculo1.status} | KM: {veiculo1.kmatual}")
    print(f"Total Arrecadado na Reserva: R${reserva.total_pago():.2f}")