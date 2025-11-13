import sqlite3
from datetime import date

# Conexão ao Banco de dados locadora.db
def conectar_banco(nome_db):
    return sqlite3.connect(nome_db)

#Cadastrar Pessoa
def inserir_pessoa(conexao, pessoa):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO pessoa (nome, telefone, email, rua, numero, cidade, estado, cep)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pessoa._nome, pessoa._telefone, pessoa._email, pessoa._rua,
        pessoa._numero, pessoa._cidade, pessoa._estado, pessoa._cep))
    conexao.commit()
    pessoa._id = cursor.lastrowid
    print(f"Pessoa '{pessoa._nome}' inserida com ID {pessoa._id}.")

#Cadastrar Pessoa como Cliente
def inserir_cliente(conexao, cliente):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO cliente (pessoa_id, cpf, cnh)
        VALUES (?, ?, ?)
    ''', (cliente._id, cliente._cpf, cliente._cnh))
    conexao.commit()
    print(f"Cliente '{cliente._nome}' adicionado com sucesso.")

#Cadastrar Pessoa como Funcionário
def inserir_funcionario(conexao, funcionario):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO funcionario (pessoa_id, matricula, cargo, salario)
        VALUES (?, ?, ?, ?)
    ''', (funcionario._id, funcionario._matricula, funcionario._cargo, funcionario._salario))
    conexao.commit()
    print(f"Funcionário '{funcionario._nome}' adicionado com sucesso.")

#Cadastrar Veículo
def inserir_veiculo(conexao, veiculo):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO veiculo (placa, modelo, status, kmatual)
        VALUES (?, ?, ?, ?)
    ''', (veiculo._placa, veiculo._modelo, veiculo._status, veiculo._kmatual))
    conexao.commit()
    veiculo._id = cursor.lastrowid
    print(f"Veículo '{veiculo._modelo}' inserido com ID {veiculo._id}.")

#Cadastrar Locação
def inserir_locacao(conexao, locacao):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO locacao (reserva_id, data_retirada, data_devolucao_prevista, kmretirada, kmdevolucao, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (locacao._reserva_id, locacao._data_retirada, locacao._data_devolucao_prevista,
          locacao._km_retirada, locacao._km_devolucao, locacao._status))
    conexao.commit()

#Cadastrar Reserva
def inserir_reserva(conexao, reserva):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO reserva (pessoa_id, veiculo_id, data_inicio, data_fim, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (reserva._pessoa_id, reserva._veiculo_id, reserva._data_inicio, reserva._data_fim, reserva._status))
    conexao.commit()

#Cadastrar Manutenção
def inserir_manutencao(conexao, manutencao):
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO manutencao (veiculo_id, descricao, data_manutencao, custo, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (manutencao._veiculo_id, manutencao._descricao, manutencao._data_manutencao, manutencao._custo, manutencao._status))
    conexao.commit()

#################
#Funções do CRUD
##################

#Listar Tabela
def listar_tabela(conexao, nome_tabela):
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM {nome_tabela}")
    registros = cursor.fetchall()
    for r in registros:
        print(r)
    return registros

#Buscar pessoa por nome
def buscar_por_nome(conexao, nome_tabela, nome_coluna, valor_nome):
    if nome_tabela.lower() != ["pessoa", "cliente", "funcionario"]:
        print("Tabela inválida! Use apenas algum destes 'pessoa', 'cliente', 'funcionario'.")
        return
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {nome_coluna} = ?", (valor_nome,))
    return cursor.fetchall()

#Buscar veículo por modelo
def buscar_por_modelo(conexao, nome_tabela, nome_coluna, valor_modelo):
    if nome_tabela.lower() != "veiculo":
        print("Tabela inválida! Use apenas 'veiculo'.")
        return
    cursor = conexao.cursor()
    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {nome_coluna} = ?", (valor_modelo,))
    return cursor.fetchall()

#Atualizar pessoa
def atualizar_pessoa(conexao, pessoa):
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE pessoa
        SET nome = ?, telefone = ?, email = ?, rua = ?, numero = ?, cidade = ?, estado = ?, cep = ?
        WHERE pessoa_id = ?
    ''', (pessoa._nome, pessoa._telefone, pessoa._email, pessoa._rua,
          pessoa._numero, pessoa._cidade, pessoa._estado, pessoa._cep, pessoa._id))
    conexao.commit()
    print(f"Pessoa ID {pessoa._id} atualizada com sucesso.")

#Atualizar status do veículo
def atualizar_status_veiculo(conexao, veiculo_id, novo_status):
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE veiculo
        SET status = ?
        WHERE veiculo_id = ?
    ''', (novo_status, veiculo_id))
    conexao.commit()
    print(f"Status do veículo {veiculo_id} atualizado para '{novo_status}'.")

#Delete por pessoa por nome
def deletar_pessoa(conexao, nome_tabela, nome_coluna, valor_nome, coluna_id="pessoa_id"):
    if nome_tabela.lower() != ["pessoa", "cliente", "funcionario"]:
        print("Tabela inválida, favor selecionar 'pessoa', 'cliente', 'funcionario'.")
        return 
    cursor = conexao.cursor()
    #Busca todos os nomes procurados
    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {nome_coluna} = ?", (valor_nome,))
    registros = cursor.fetchall()
    #Caso não ache nenhum objeto com o nome procurado
    if not registros:
        print(f"Nenhum registro encontrado com {nome_coluna} = '{valor_nome}'.")
        return
    #Caso ache algum objeto com o nome procurado
    print(f"\nRegistros encontrados com {nome_coluna} = '{valor_nome}':")
    for i in registros:
        print(i)
    #Pergunta qual ID e deleta o escohlido
    id_escolhido = input("\nDigite o ID do registro que deseja excluir: ")
    cursor.execute(f"DELETE FROM {nome_tabela} WHERE {coluna_id} = ?", (id_escolhido,))
    conexao.commit()
    #Verifica se foi excluido e printa o resultado
    if cursor.rowcount > 0:
        print(f"Registro com ID {id_escolhido} removido da tabela {nome_tabela}.")
    else:
        print("Nenhum registro foi removido (ID inválido).")
    cursor.close()

def deletar_veiculo(conexao, nome_tabela, nome_coluna, valor_placa):
    if nome_tabela.lower() != "veiculo":
        print("Tabela inválida, favor selecionar 'veiculo'.")
        return
    cursor = conexao.cursor()
    #Busca todos as placas procuradas
    cursor.execute(f"SELECT * FROM {nome_tabela} WHERE {nome_coluna} = ?", (valor_placa,))
    registros = cursor.fetchall()
    #Caso não ache nenhum objeto com a placa procurad
    if not registros:
        print(f"Nenhum registro encontrado com {nome_coluna} = '{valor_placa}'.")
        return
    #Caso ache algum objeto com a placa procurada
    print(f"\nRegistro encontrado com {nome_coluna} = '{valor_placa}':")
    #Deleta a placa pesquisada
    cursor.execute(f"DELETE FROM {nome_tabela} WHERE {nome_coluna} = ?", (valor_placa,))
    conexao.commit()
    #Verifica se foi excluido e printa o resultado
    if cursor.rowcount > 0:
        print(f"Veículo com placa '{valor_placa}' removido da tabela {nome_tabela}.")
    else:
        print("Nenhum registro foi removido (ID inválido).")
    cursor.close()

#Se for aberta como Função principal executar
if __name__ == "__main__":
    from data_input import Pessoa, Cliente, Funcionario, Veiculo 

    conexao = conectar_banco("locadora.db")

    p1 = Pessoa("João", "99998888", "joao@email.com", "Rua A", 123, "Fortaleza", "CE", 60000000)
    inserir_pessoa(conexao, p1)

    c1 = Cliente(p1._nome, p1._telefone, p1._email, p1._rua, p1._numero, p1._cidade, p1._estado, p1._cep, "12345678901", "B", id=p1._id)
    inserir_cliente(conexao, c1)

    listar_tabela(conexao, "pessoa")

    conexao.close()