import sqlite3

def conectar_banco(nome_banco):
    """Conecta ao banco de dados SQLite e retorna a conexão."""
    conexao = sqlite3.connect(nome_banco)
    return conexao

def delete_tabela(conexao, lista_nome_tabela):
    """Deleta a tabela especificada do banco de dados."""
    cursor = conexao.cursor()
    for nome_tabela in lista_nome_tabela:
        cursor.execute(f"DROP TABLE IF EXISTS {nome_tabela};")
    conexao.commit()

def criar_tabelas(conexao): 
    """Cria uma tabela de exemplo no banco de dados."""
    cursor = conexao.cursor()

    #Tabela Pessoa 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoa (
            pessoa_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            rua TEXT NOT NULL,
            numero INTEGER NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cep INTEGER NOT NULL
        )
    ''')

    #Tabela Cliente
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cliente (
            pessoa_id INTEGER PRIMARY KEY,
            cpf TEXT UNIQUE NOT NULL,
            cnh TEXT UNIQUE NOT NULL
        )
    ''')

    #Tabela Funcionário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionario (
            pessoa_id INTEGER PRIMARY KEY,
            matricula INTEGER UNIQUE NOT NULL,
            cargo TEXT CHECK(cargo IN ('Atendente', 'Vendedor', 'Gerente')) NOT NULL,
            salario REAL NOT NULL
        )
    ''')


    #Tabela Veículo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS veiculo (
            veiculo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            modelo TEXT NOT NULL,
            status TEXT NOT NULL,
            kmatual INTEGER NOT NULL
        )
    ''')

    #Tabela Manutenção
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manutencao (
            manutencao_id INTEGER PRIMARY KEY AUTOINCREMENT,
            veiculo_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            data_manutencao TEXT NOT NULL,
            custo REAL NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    

    #Tabela Reserva
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reserva (
            reserva_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER NOT NULL,
            veiculo_id INTEGER NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')

    #Tabela Pagamento
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamento (
            pagamento_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data_pagamento TEXT NOT NULL,
            FOREIGN KEY (reserva_id)
                REFERENCES reserva(reserva_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    ''')


    #Tabela Locacao
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locacao (
            reserva_id INTEGER PRIMARY KEY,
            data_retirada TEXT NOT NULL,
            data_devolucao_prevista TEXT NOT NULL,
            data_devolucao_real TEXT NOT NULL,
            kmretirada INTEGER NOT NULL,
            kmdevolucao INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (reserva_id) 
                   REFERENCES reserva(reserva_id) 
                   ON DELETE CASCADE
                   ON UPDATE CASCADE
        )
    ''')

    
    conexao.commit()

if __name__ == "__main__":
    nome_banco = 'locadora.db'
    conexao = conectar_banco(nome_banco)
    #delete_tabela(conexao, ['endereço','cliente', 'funcionario', 'manutencao', 'veiculo', 'reserva', 'locacao', 'pessoa', 'pagamento']) 
    criar_tabelas(conexao)
    conexao.close()
    print(f"Banco de dados '{nome_banco}' criado com sucesso e as tabelas adicionada.")