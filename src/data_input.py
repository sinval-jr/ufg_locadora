import sqlite3

class Pessoa:
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep):
        self.nome = nome
        self.telefone = telefone
        self.email = email
        self.rua = rua
        self.numero = numero
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def atualizar_contato(self, novo_telefone, novo_email):
        self.telefone = novo_telefone
        self.email = novo_email

class Veiculo:
    def __init__(self, placa, modelo, status, kmatual):
        self.placa = placa
        self.modelo = modelo
        self.status = status
        self.kmatual = kmatual

    def atualizar_status(self, novo_status):
        self.status = novo_status

    def registrar_manutencao(self, descricao, data_manutencao, custo, status):
        pass

    def disponivel_para_reserva(self):
        pass

    def incrementar_km(self, km):
        pass

class Manutencao:
    def __init__(self, veiculo_id, descricao, data_manutencao, custo, status):
        self.veiculo_id = veiculo_id
        self.descricao = descricao
        self.data_manutencao = data_manutencao
        self.custo = custo
        self.status = status

    def registrar_manutencao(self):
        pass

    def registrar_conclusao(self, data_conclusao):
        pass

    def gerar_relatorio(self):
        pass


class Cliente(Pessoa):
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, cpf, cnh):
        super().__init__(nome, telefone, email, rua, numero, cidade, estado, cep)
        self.cpf = cpf
        self.cnh = cnh
    
    def alugar_veiculo(self, veiculo):
        pass
    
    def devolver_veiculo(self, veiculo):
        pass

    def pagar_reserva(self, valor):
        pass

class Funcionario(Pessoa):
    def __init__(self, nome, telefone, email, rua, numero, cidade, estado, cep, matricula, cargo, salario):
        super().__init__(nome, telefone, email, rua, numero, cidade, estado, cep)
        self.matricula = matricula
        self.cargo = cargo
        self.salario = salario

    def registrar_locacao(self, cliente, veiculo):
        pass

    def calcular_salario(self):
        pass
    
    def atualizar_cargo(self, novo_cargo):
        self.cargo = novo_cargo

class Reserva:
    def __init__(self, cliente_id, veiculo_id, data_reserva, data_devolucao, valor):
        self.cliente_id = cliente_id
        self.veiculo_id = veiculo_id
        self.data_reserva = data_reserva
        self.data_devolucao = data_devolucao
        self.valor = valor

    def confirmar_reserva(self):
        pass

    def cancelar_reserva(self):
        pass

    def gerar_recibo(self):
        pass