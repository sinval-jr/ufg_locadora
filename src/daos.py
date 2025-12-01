
import sqlite3
import os
from datetime import date, datetime
from builder_client_func import Cliente, Funcionario, Reserva, Locacao
from builder_pagamento import Pagamento
from builder_veiculo_manutencao import Veiculo, Manutencao

# -----------------------------------------------------------------
# BASE DAO (Gerencia Conexão e Tabelas)
# -----------------------------------------------------------------
class BaseDAO:
    def __init__(self, db_name="locadora.db"):
        # padroniza para caminho absoluto para evitar múltiplos arquivos
        self._db_name = os.path.abspath(db_name)

    def get_connection(self):
        # habilita foreign keys e timeout razoável
        conn = sqlite3.connect(self._db_name, timeout=30)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def criar_tabelas(self):
        """Cria as tabelas no banco de dados (nomes NO SINGULAR)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela pessoa (singular)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoa (
            pessoa_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            rua TEXT NOT NULL,
            numero INTEGER NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            cep TEXT NOT NULL
        )""")

        # Tabela cliente (singular)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cliente (
            pessoa_id INTEGER PRIMARY KEY,
            cpf TEXT NOT NULL,
            cnh TEXT NOT NULL
        )""")

        # Tabela funcionario (singular)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionario (
            pessoa_id INTEGER PRIMARY KEY,
            matricula TEXT UNIQUE,
            cargo TEXT,
            salario REAL
        )""")

        # Tabela veiculo (singular)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculo (
            veiculo_id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE NOT NULL,
            modelo TEXT NOT NULL,
            status TEXT NOT NULL,
            kmatual INTEGER NOT NULL,
            valor_diaria REAL DEFAULT 0.0,
            preco_por_km REAL DEFAULT 0.0
        )""")

        #Tabela Manutenção
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manutencao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                data_inicio TEXT,
                data_fim TEXT,
                custo REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        # Tabela Reserva
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserva (
            reserva_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER NOT NULL,
            veiculo_id INTEGER NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            status TEXT,
            FOREIGN KEY(pessoa_id) REFERENCES cliente(pessoa_id),
            FOREIGN KEY(veiculo_id) REFERENCES veiculo(veiculo_id)
        )""")

        # pagamento
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamento (
            pagamento_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER NOT NULL,
            tipo TEXT,
            valor REAL,
            data_pagamento TEXT,
            FOREIGN KEY(reserva_id) REFERENCES reserva(reserva_id) ON DELETE CASCADE
        )""")

        # locacao
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locacao (
            locacao_id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER NOT NULL,
            funcionario_id INTEGER,
            data_retirada TEXT,
            km_retirada INTEGER,
            data_devolucao_real TEXT,
            km_devolucao INTEGER,
            status TEXT,
            FOREIGN KEY(reserva_id) REFERENCES reserva(reserva_id) ON DELETE CASCADE
        )""")

        conn.commit()
        conn.close()

# -----------------------------------------------------------------
# VEICULO DAO
# -----------------------------------------------------------------
class VeiculoDAO(BaseDAO):
    def __init__(self, db_name="locadora.db"):
        super().__init__(db_name)

    def salvar(self, veiculo: Veiculo):
        conn = self.get_connection()
        cursor = conn.cursor()

        if getattr(veiculo, "id", None) is None:
            cursor.execute("""
                INSERT INTO veiculo (placa, modelo, status, kmatual, valor_diaria, preco_por_km)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (veiculo.placa, veiculo.modelo, veiculo.status, veiculo.kmatual, getattr(veiculo, "_valor_diaria", 0.0), getattr(veiculo, "_preco_por_km", 0.0)))
            veiculo.__id = cursor.lastrowid
        else:
            cursor.execute("UPDATE veiculo SET status=?, kmatual=? WHERE veiculo_id=?", (veiculo.status, veiculo.kmatual, veiculo.id))

        conn.commit()
        conn.close()
        return veiculo

    def buscar_por_id(self, id_):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veiculo WHERE veiculo_id=?", (id_,))
        row = cursor.fetchone()
        conn.close()
        if row:
            # row: veiculo_id, placa, modelo, status, kmatual, valor_diaria, preco_por_km
            return Veiculo(row[1], row[2], row[3], row[4], row[5], row[6], id=row[0])
        return None

# -----------------------------------------------------------------
# PAGAMENTO DAO
# -----------------------------------------------------------------
class PagamentoDAO(BaseDAO):
    def __init__(self, db_name="locadora.db"):
        super().__init__(db_name)

    def salvar(self, pagamento: Pagamento, reserva_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        dt_pgto = pagamento.data_pagamento.isoformat() if isinstance(pagamento.data_pagamento, date) else str(pagamento.data_pagamento)
        if pagamento.id is None:
            cursor.execute("""
                INSERT INTO pagamento (reserva_id, tipo, valor, data_pagamento)
                VALUES (?, ?, ?, ?)
            """, (reserva_id, pagamento.tipo, pagamento.valor, dt_pgto))
            pagamento.id = cursor.lastrowid
        else:
            cursor.execute("UPDATE pagamento SET tipo=?, valor=?, data_pagamento=? WHERE pagamento_id=?", (pagamento.tipo, pagamento.valor, dt_pgto, pagamento.id))
        conn.commit()
        conn.close()
        return pagamento

    def listar_por_reserva(self, reserva_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pagamento WHERE reserva_id=?", (reserva_id,))
        rows = cursor.fetchall()
        conn.close()
        lista = []
        for r in rows:
            dt = date.fromisoformat(r[4]) if r[4] else date.today()
            p = Pagamento(metodo=None, valor=r[3], data_pagamento=dt, tipo=r[2], id=r[0])
            lista.append(p)
        return lista

# -----------------------------------------------------------------
# PESSOA / CLIENTE / FUNCIONARIO DAO
# -----------------------------------------------------------------
class PessoaDAO(BaseDAO):
    def __init__(self, db_name="locadora.db"):
        super().__init__(db_name)

    def _salvar_pessoa(self, pessoa, cursor):
        if pessoa.id is None:
            cursor.execute("""
                INSERT INTO pessoa (nome, telefone, email, rua, numero, cidade, estado, cep)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (pessoa.nome, pessoa.telefone, pessoa.email, pessoa.rua, pessoa.numero, pessoa.cidade, pessoa.estado, pessoa.cep))
            return cursor.lastrowid
        else:
            return pessoa.id

class ClienteDAO(PessoaDAO):
    def __init__(self, db_name="locadora.db"):
        super().__init__(db_name)

    def salvar(self, cliente: Cliente):
        conn = self.get_connection()
        cursor = conn.cursor()

        pessoa_id = self._salvar_pessoa(cliente, cursor)
        cliente.__id = pessoa_id

        cursor.execute("SELECT pessoa_id FROM cliente WHERE pessoa_id=?", (pessoa_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO cliente (pessoa_id, cpf, cnh) VALUES (?, ?, ?)", (pessoa_id, cliente.cpf, cliente.cnh))

        conn.commit()
        conn.close()
        return cliente

    def buscar_por_id(self, id_):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.pessoa_id, p.nome, p.telefone, p.email, p.rua, p.numero, p.cidade, p.estado, p.cep, c.cpf, c.cnh
            FROM pessoa p
            JOIN cliente c ON p.pessoa_id = c.pessoa_id
            WHERE p.pessoa_id = ?
        """, (id_,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Cliente(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], id=row[0])
        return None

class FuncionarioDAO(PessoaDAO):
    def __init__(self, db_name="locadora.db"):
        super().__init__(db_name)

    def salvar(self, funcionario: Funcionario):
        conn = self.get_connection()
        cursor = conn.cursor()

        pessoa_id = self._salvar_pessoa(funcionario, cursor)
        funcionario.__id = pessoa_id

        cursor.execute("SELECT pessoa_id FROM funcionario WHERE pessoa_id=?", (pessoa_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO funcionario (pessoa_id, matricula, cargo, salario) VALUES (?, ?, ?, ?)",
                           (pessoa_id, funcionario.matricula, funcionario.cargo, funcionario.salario))

        conn.commit()
        conn.close()
        return funcionario

    def buscar_por_id(self, id_):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.pessoa_id, p.nome, p.telefone, p.email, p.rua, p.numero, p.cidade, p.estado, p.cep, f.matricula, f.cargo, f.salario
            FROM pessoa p
            JOIN funcionario f ON p.pessoa_id = f.pessoa_id
            WHERE p.pessoa_id = ?
        """, (id_,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Funcionario(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], id=row[0])
        return None

# -----------------------------------------------------------------
# RESERVA / LOCACAO DAO
# -----------------------------------------------------------------
class ReservaDAO(BaseDAO):
    def __init__(self, cliente_dao, veiculo_dao, pagamento_dao, db_name="locadora.db"):
        super().__init__(db_name)
        self.cliente_dao = cliente_dao
        self.veiculo_dao = veiculo_dao
        self.pagamento_dao = pagamento_dao

    def salvar(self, reserva: Reserva):
        conn = self.get_connection()
        cursor = conn.cursor()

        dt_ini = reserva.data_reserva.isoformat()
        dt_fim = reserva.data_devolucao.isoformat()

        if getattr(reserva, "id", None) is None:
            cursor.execute("""
                INSERT INTO reserva (pessoa_id, veiculo_id, data_inicio, data_fim, status)
                VALUES (?, ?, ?, ?, ?)
            """, (reserva.cliente.id, reserva.veiculo.id, dt_ini, dt_fim, reserva.status))
            reserva.id = cursor.lastrowid
        else:
            cursor.execute("UPDATE reserva SET status=? WHERE reserva_id=?", (reserva.status, reserva.id))

        conn.commit()
        conn.close()

        for pgto in reserva.pagamentos:
            self.pagamento_dao.salvar(pgto, reserva.id)

        return reserva

    def buscar_por_id(self, id_):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reserva WHERE reserva_id=?", (id_,))
        row = cursor.fetchone()
        conn.close()
        if row:
            cliente = self.cliente_dao.buscar_por_id(row[1])
            veiculo = self.veiculo_dao.buscar_por_id(row[2])
            dt_ini = date.fromisoformat(row[3])
            dt_fim = date.fromisoformat(row[4])
            reserva = Reserva(cliente, veiculo, dt_ini, dt_fim, id=row[0])
            reserva.__status = row[5] if len(row) > 5 else "pendente"
            reserva.__pagamentos = self.pagamento_dao.listar_por_reserva(reserva.id)
            return reserva
        return None

class LocacaoDAO(BaseDAO):
    def __init__(self, reserva_dao, funcionario_dao, db_name="locadora.db"):
        super().__init__(db_name)
        self.reserva_dao = reserva_dao
        self.funcionario_dao = funcionario_dao

    def salvar(self, locacao: Locacao):
        conn = self.get_connection()
        cursor = conn.cursor()

        dt_ret = locacao.data_retirada.isoformat() if locacao.data_retirada else None
        dt_dev_real = locacao.data_devolucao_real.isoformat() if locacao.data_devolucao_real else None

        func_id = locacao.funcionario.id if locacao.funcionario else None

        if getattr(locacao, "id", None) is None:
            cursor.execute("""
                INSERT INTO locacao (reserva_id, funcionario_id, data_retirada, km_retirada, data_devolucao_real, km_devolucao, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (locacao.reserva.id, func_id, dt_ret, locacao.km_retirada, dt_dev_real, locacao.km_devolucao, locacao.status))
            locacao.id = cursor.lastrowid
        else:
            cursor.execute("UPDATE locacao SET data_devolucao_real=?, km_devolucao=?, status=? WHERE locacao_id=?", (dt_dev_real, locacao.km_devolucao, locacao.status, locacao.id))

        conn.commit()
        conn.close()
        return locacao

    def buscar_por_id(self, id_):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locacao WHERE locacao_id=?", (id_,))
        row = cursor.fetchone()
        conn.close()
        if row:
            reserva = self.reserva_dao.buscar_por_id(row[1])
            funcionario = self.funcionario_dao.buscar_por_id(row[2])
            dt_ret = date.fromisoformat(row[3]) if row[3] else None
            locacao = Locacao(reserva, dt_ret, row[4], row[7], funcionario, id=row[0])
            if row[5]:
                locacao.data_devolucao_real = date.fromisoformat(row[5])
            if row[6]:
                locacao.km_devolucao = row[6]
            return locacao
        return None
    
class ManutencaoDAO(BaseDAO):
    def __init__(self, veiculo_dao: VeiculoDAO):
        super().__init__()
        self.veiculo_dao = veiculo_dao # Necessário para re-hidratar o objeto Veiculo

    def salvar(self, manutencao: Manutencao):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # --- CORREÇÃO AQUI ---
        # Acessando os atributos privados (ex: _data_inicio) diretamente
        # para evitar o erro de @property faltante.
        dt_ini = manutencao.data_inicio.isoformat() 
        dt_fim = manutencao.data_fim.isoformat() if manutencao.__data_fim else None
        
        if manutencao.id is None:
            # Inserir
            cursor.execute("""
                INSERT INTO manutencao (veiculo_id, descricao, data_inicio, data_fim, custo, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (manutencao.veiculo.id, manutencao.descricao, dt_ini, dt_fim, manutencao.custo, manutencao.status))
            manutencao.__id = cursor.lastrowid
        else:
            # Atualizar (ex: ao concluir)
            cursor.execute("""
                UPDATE manutencao 
                SET data_fim=?, custo=?, status=?
                WHERE id=?
            """, (dt_fim, manutencao.custo, manutencao.status, manutencao.id))
            
        conn.commit()
        conn.close()
        return manutencao

    def buscar_em_andamento_por_veiculo(self, veiculo_id: int):
        """ Encontra a manutenção ATIVA para um veículo. """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM manutencao WHERE veiculo_id=? AND status='em andamento'", (veiculo_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Re-hidratação
            veiculo = self.veiculo_dao.buscar_por_id(row[1])
            dt_ini = date.fromisoformat(row[3])
            
            man = Manutencao(veiculo, row[2], dt_ini, row[5], id=row[0])
            man.__status = row[6] # Garante status
            return man
        return None
