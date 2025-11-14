import sqlite3
from datetime import date, datetime
from model import Cliente, Funcionario, Veiculo, Reserva, Locacao, Pagamento

# -----------------------------------------------------------------
# BASE DAO (Gerencia Conexão e Tabelas)
# -----------------------------------------------------------------
class BaseDAO:
    def __init__(self, db_name="locadora.db"):
        self._db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self._db_name)

    def criar_tabelas(self): 
        """Cria as tabelas no banco de dados."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Tabela Veiculos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT, modelo TEXT, status TEXT, 
            kmatual INTEGER, valor_diaria REAL, preco_por_km REAL
        )""")

        # Tabela Pessoas (Base para Clientes e Funcionários)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, telefone TEXT, email TEXT,
            rua TEXT, numero INTEGER, cidade TEXT, estado TEXT, cep TEXT
        )""")

        # Tabela Clientes (CORRIGIDO AQUI)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            pessoa_id INTEGER PRIMARY KEY,
            cpf TEXT UNIQUE NOT NULL, 
            cnh TEXT NOT NULL,
            FOREIGN KEY(pessoa_id) REFERENCES pessoas(id)
        )""")

        # Tabela Funcionarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            pessoa_id INTEGER PRIMARY KEY,
            matricula TEXT, cargo TEXT, salario REAL,
            FOREIGN KEY(pessoa_id) REFERENCES pessoas(id)
        )""")

        # Tabela Reservas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER, veiculo_id INTEGER, funcionario_id INTEGER,
            data_reserva TEXT, data_devolucao TEXT, valor_previsto REAL, status TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(pessoa_id),
            FOREIGN KEY(veiculo_id) REFERENCES veiculos(id)
        )""")

        # Tabela Locacoes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS locacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER, data_retirada TEXT, km_retirada INTEGER,
            data_devolucao_real TEXT, km_devolucao INTEGER, status TEXT,
            FOREIGN KEY(reserva_id) REFERENCES reservas(id)
        )""")

        #Tabela Manutenção
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS manutencao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                veiculo_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                data_manutencao TEXT NOT NULL,
                custo REAL NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        # Tabela Pagamentos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reserva_id INTEGER NOT NULL,
            tipo TEXT,
            metodo TEXT,
            valor REAL,
            data_pagamento TEXT,
            FOREIGN KEY(reserva_id) REFERENCES reservas(id)
        )""")

        conn.commit()
        conn.close()

# -----------------------------------------------------------------
# VEICULO DAO
# -----------------------------------------------------------------
class VeiculoDAO(BaseDAO):
    def salvar(self, veiculo: Veiculo):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if veiculo.id is None: # Inserir novo
            cursor.execute("""
                INSERT INTO veiculos (placa, modelo, status, kmatual, valor_diaria, preco_por_km)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (veiculo.placa, veiculo.modelo, veiculo.status, veiculo.kmatual, veiculo.valor_diaria, veiculo.preco_por_km))
            veiculo._id = cursor.lastrowid
        else: # Atualizar existente
            cursor.execute("""
                UPDATE veiculos SET status=?, kmatual=? WHERE id=?
            """, (veiculo.status, veiculo.kmatual, veiculo.id))
            
        conn.commit()
        conn.close()
        return veiculo

    def buscar_por_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veiculos WHERE id=?", (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            
            return Veiculo(row[1], row[2], row[3], row[4], row[5], row[6], id=row[0])
        return None
    
class PagamentoDAO(BaseDAO):
    def salvar(self, pagamento: Pagamento, reserva_id: int):
        """
        Salva um pagamento vinculando-o a um ID de reserva.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        dt_pgto = pagamento._data_pagamento.isoformat()
        
        if pagamento._id is None:
            cursor.execute("""
                INSERT INTO pagamentos (reserva_id, tipo, metodo, valor, data_pagamento)
                VALUES (?, ?, ?, ?, ?)
            """, (reserva_id, pagamento._tipo, pagamento._metodo, pagamento._valor, dt_pgto))
            pagamento._id = cursor.lastrowid
        else:
            
            cursor.execute("""
                UPDATE pagamentos SET tipo=?, metodo=?, valor=?, data_pagamento=?
                WHERE id=?
            """, (pagamento._tipo, pagamento._metodo, pagamento._valor, dt_pgto, pagamento._id))
            
        conn.commit()
        conn.close()
        return pagamento

    def listar_por_reserva(self, reserva_id):
        """
        Retorna uma LISTA de objetos Pagamento pertencentes a uma reserva.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pagamentos WHERE reserva_id=?", (reserva_id,))
        rows = cursor.fetchall()
        conn.close()
        
        lista_pagamentos = []
        for row in rows:
            
            dt_pgto = date.fromisoformat(row[5])

            p = Pagamento(
                metodo=row[3],
                valor=row[4],
                data_pagamento=dt_pgto,
                tipo=row[2],
                id=row[0]
            )
            lista_pagamentos.append(p)
            
        return lista_pagamentos

# -----------------------------------------------------------------
# PESSOA DAO (Classe Pai para salvar dados comuns)
# -----------------------------------------------------------------
class PessoaDAO(BaseDAO):
    def _salvar_pessoa(self, pessoa, cursor):
        """Método interno para salvar na tabela 'pessoas' e retornar o ID"""
        if pessoa.id is None:
            cursor.execute("""
                INSERT INTO pessoas (nome, telefone, email, rua, numero, cidade, estado, cep)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (pessoa.nome, pessoa.telefone, pessoa.email, pessoa._rua, pessoa._numero, pessoa._cidade, pessoa._estado, pessoa._cep))
            return cursor.lastrowid
        else:
            return pessoa.id

# -----------------------------------------------------------------
# CLIENTE DAO (Herança)
# -----------------------------------------------------------------
class ClienteDAO(PessoaDAO):
    def salvar(self, cliente: Cliente):
        conn = self.get_connection()
        cursor = conn.cursor()
        

        pessoa_id = self._salvar_pessoa(cliente, cursor)
        cliente._id = pessoa_id # Atualiza o ID no objeto
        
        cursor.execute("SELECT pessoa_id FROM clientes WHERE pessoa_id=?", (pessoa_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO clientes (pessoa_id, cpf, cnh) VALUES (?, ?, ?)", 
                           (pessoa_id, cliente.cpf, cliente.cnh))
        
        conn.commit()
        conn.close()
        return cliente

    def buscar_por_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.cpf, c.cnh 
            FROM pessoas p
            JOIN clientes c ON p.id = c.pessoa_id
            WHERE p.id = ?
        """, (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Cliente(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], id=row[0])
        return None

# -----------------------------------------------------------------
# FUNCIONARIO DAO (Herança)
# -----------------------------------------------------------------
class FuncionarioDAO(PessoaDAO):
    def salvar(self, funcionario: Funcionario):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        pessoa_id = self._salvar_pessoa(funcionario, cursor)
        funcionario._id = pessoa_id
        
        cursor.execute("SELECT pessoa_id FROM funcionarios WHERE pessoa_id=?", (pessoa_id,))
        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO funcionarios (pessoa_id, matricula, cargo, salario) 
                VALUES (?, ?, ?, ?)""", 
                (pessoa_id, funcionario.matricula, funcionario.cargo, funcionario.salario))
        
        conn.commit()
        conn.close()
        return funcionario

    def buscar_por_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, f.matricula, f.cargo, f.salario
            FROM pessoas p
            JOIN funcionarios f ON p.id = f.pessoa_id
            WHERE p.id = ?
        """, (id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Funcionario(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], id=row[0])
        return None

# -----------------------------------------------------------------
# RESERVA DAO (Injeção de Dependência)
# -----------------------------------------------------------------
class ReservaDAO(BaseDAO):
    def __init__(self, cliente_dao, veiculo_dao, funcionario_dao, pagamento_dao):
        super().__init__()
        self.cliente_dao = cliente_dao
        self.veiculo_dao = veiculo_dao
        self.funcionario_dao = funcionario_dao
        self.pagamento_dao = pagamento_dao 

    def salvar(self, reserva: Reserva):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        dt_reserva = reserva.data_reserva.isoformat()
        dt_devolucao = reserva.data_devolucao.isoformat()
        func_id = reserva._funcionario.id if reserva._funcionario else None
        
        if reserva.id is None: 
            cursor.execute("""
                INSERT INTO reservas (cliente_id, veiculo_id, funcionario_id, data_reserva, data_devolucao, valor_previsto, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (reserva._cliente.id, reserva._veiculo.id, func_id, dt_reserva, dt_devolucao, reserva.valor_total_previsto, reserva._status))
            reserva._id = cursor.lastrowid
        else:
            cursor.execute("UPDATE reservas SET status=?, funcionario_id=? WHERE id=?", 
                           (reserva._status, func_id, reserva.id))
            
        conn.commit()
        conn.close()

        for pgto in reserva._pagamentos:
            self.pagamento_dao.salvar(pgto, reserva.id)

        return reserva

    def buscar_por_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reservas WHERE id=?", (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            cliente = self.cliente_dao.buscar_por_id(row[1])
            veiculo = self.veiculo_dao.buscar_por_id(row[2])
            funcionario = self.funcionario_dao.buscar_por_id(row[3]) if row[3] else None
            dt_reserva = date.fromisoformat(row[4])
            dt_devolucao = date.fromisoformat(row[5])
            
            reserva = Reserva(cliente, veiculo, dt_reserva, dt_devolucao, funcionario, id=row[0])
            reserva._status = row[7]

            reserva._pagamentos = self.pagamento_dao.listar_por_reserva(reserva.id)
            
            return reserva
        return None
    
class LocacaoDAO(BaseDAO):
    def __init__(self, reserva_dao):
        super().__init__()
        self.reserva_dao = reserva_dao

    def salvar(self, locacao: Locacao):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        dt_ret = locacao._data_retirada.isoformat()
        dt_dev_real = locacao._data_devolucao_real.isoformat() if locacao._data_devolucao_real else None
        
        if locacao.id is None or (isinstance(locacao.id, int) and locacao.id < 1000):
            cursor.execute("""
                INSERT INTO locacoes (reserva_id, data_retirada, km_retirada, data_devolucao_real, km_devolucao, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (locacao._reserva.id, dt_ret, locacao._km_retirada, dt_dev_real, locacao._km_devolucao, locacao._status))
            locacao._id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE locacoes 
                SET data_devolucao_real=?, km_devolucao=?, status=?
                WHERE id=?
            """, (dt_dev_real, locacao._km_devolucao, locacao._status, locacao.id))
            
        conn.commit()
        conn.close()
        return locacao

    def buscar_por_id(self, id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM locacoes WHERE id=?", (id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            reserva = self.reserva_dao.buscar_por_id(row[1])
            dt_ret = date.fromisoformat(row[2])
            
            locacao = Locacao(reserva, dt_ret, row[3], row[6], id=row[0])
            
            # Preenche dados de devolução se houver
            if row[4]:
                locacao._data_devolucao_real = date.fromisoformat(row[4])
            if row[5]:
                locacao._km_devolucao = row[5]
                
            return locacao
        return None
    
class ManutencaoDAO(BaseDAO):
    def salvar(self, manutencao):
        conn = self.get_connection()
        cursor = conn.cursor()
        dt_manut = manutencao._data_manutencao.isoformat()
        
        if manutencao._id is None:
            cursor.execute('''
                INSERT INTO manutencao (veiculo_id, descricao, data_manutencao, custo, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (manutencao._veiculo_id, manutencao._descricao, dt_manut, manutencao._custo, manutencao._status))
            manutencao._id = cursor.lastrowid
        else:
            cursor.execute('''
                UPDATE manutencao
                SET veiculo_id=?, descricao=?, data_manutencao=?, custo=?, status=?
                WHERE id=?
            ''', (manutencao._veiculo_id, manutencao._descricao, dt_manut, manutencao._custo, manutencao._status, manutencao._id))
        
        conn.commit()
        conn.close()
        return manutencao