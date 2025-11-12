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

    def atualizar_contato(self, novo_telefone, novo_email):
        self.telefone = novo_telefone
        self.email = novo_email

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
    
    def alugar_veiculo(self, veiculo):
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

    def calcular_salario(self):
        pass
    
    def atualizar_cargo(self, novo_cargo):
        self._cargo = novo_cargo

class Reserva:
    def __init__(self, data_reserva, data_devolucao, valor, id = None):
        self._id = id
        self._data_reserva = data_reserva
        self._data_devolucao = data_devolucao
        self._valor = valor
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

    def confirmar_reserva(self):
        pass

    def cancelar_reserva(self):
        pass

    def gerar_recibo(self):
        pass

class Locacao:
    def __init__(self, data_retirada, data_devolucao_prevista, km_retirada, status, id=None, data_devolucao_real = None, km_devolucao = None):
        self._id = id
        self._data_retirada = data_retirada
        self._data_devolucao_prevista = data_devolucao_prevista
        self._data_devolucao_real = data_devolucao_real
        self._km_retirada = km_retirada
        self._km_devolucao = km_devolucao
        self._status = status

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

    def emitir_recibo(self):
        pass

    def iniciar(self):
        pass

    def encerrar(self):
        pass

    def calcular_custo_final(self):
        pass
