import customtkinter as ctk
from tkinter import messagebox as tkmb
from datetime import datetime, date
from daos import BaseDAO, ClienteDAO, VeiculoDAO, ReservaDAO, PagamentoDAO, LocacaoDAO
from model import Cliente

# caminho unificado
CAMINHO_DB = "locadora.db"  

#Janela do cliente (Chamada pelo Arquivo ui_main.py)
def abrir_tela_cliente(prev_window, email_cliente):
    from ui_main import abrir_login
    # Fecha tela anterior
    try:
        prev_window.destroy()
    except:
        pass

    # Inicializar DAO
    base = BaseDAO(CAMINHO_DB)
    cliente_dao = ClienteDAO(CAMINHO_DB)
    veiculo_dao = VeiculoDAO(CAMINHO_DB)
    pagamento_dao = PagamentoDAO(CAMINHO_DB)
    reserva_dao = ReservaDAO(cliente_dao, veiculo_dao, pagamento_dao, CAMINHO_DB)

    # Buscar cliente pelo email
    conn = base.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.pessoa_id, p.nome, p.telefone, p.email, p.rua, p.numero,
               p.cidade, p.estado, p.cep, c.cpf, c.cnh
        FROM pessoa p
        JOIN cliente c ON c.pessoa_id = p.pessoa_id
        WHERE p.email = ?
    """, (email_cliente,))
    row = cursor.fetchone()
    conn.close()

    #Caso não encontre o cliente
    if not row:
        tkmb.showerror("Erro", "Cliente não encontrado.")
        return

    # Reconstruir cliente (integrado ao Model real)
    cliente = Cliente(
        row[1], row[2], row[3], row[4], row[5],
        row[6], row[7], row[8], row[9], row[10],
        id=row[0]
    )

    #Menu da janela cliente
    menu = ctk.CTk()
    menu.title("Área do Cliente")
    menu.geometry("500x400")

    ctk.CTkLabel(menu, text=f"Bem-vindo(a), {cliente.nome}", font=("Inter", 20, "bold")).pack(pady=20)
    frame = ctk.CTkFrame(menu)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    #Botões 
    ctk.CTkButton(frame, text="Realizar Reserva", height=50, command=lambda: abrir_tela_reserva(menu, cliente)).pack(pady=10)
    ctk.CTkButton(frame, text="Pagar Reserva", height=50, command=lambda: abrir_tela_pagamento(menu, cliente)).pack(pady=10)
    ctk.CTkButton(frame, text="Devolver Veículo", height=50,command=lambda: abrir_tela_devolver_veiculo(menu, cliente)).pack(pady=10)
    
    #Função de Voltar (Não vou ficar abrindo e fechando toda hora)
    def voltar_login():
        menu.destroy()
        abrir_login()

    #Botão de voltar para o menu de login
    ctk.CTkButton(frame, text="Sair", fg_color="gray", command=voltar_login).pack(pady=20)

    menu.mainloop()

#Realizar reserva
def abrir_tela_reserva(prev_window, cliente):
    from ui_main import abrir_login
    try:
        prev_window.destroy()
    except:
        pass

    base = BaseDAO(CAMINHO_DB)
    cliente_dao = ClienteDAO(CAMINHO_DB)
    veiculo_dao = VeiculoDAO(CAMINHO_DB)
    pagamento_dao = PagamentoDAO(CAMINHO_DB)
    reserva_dao = ReservaDAO(cliente_dao, veiculo_dao, pagamento_dao, CAMINHO_DB)
    
    #Cria janela e proporções
    win = ctk.CTk()
    win.geometry("600x500")
    win.title("Realizar Reserva")

    ctk.CTkLabel(win, text="Realizar Reserva", font=("Inter", 20, "bold")).pack(pady=10)

    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    #Busca na base de dados e lista todos os veículos com status "disponível"
    conn = base.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT veiculo_id, modelo, placa, valor_diaria
        FROM veiculo
        WHERE status='disponivel'
    """)
    veiculos = cursor.fetchall()
    conn.close()
    
    #Se não encontrar nenhum retorna a mensagem de aviso e volta para login (Inserir mais veículos se for o caso)
    if not veiculos:
        tkmb.showinfo("Sem veículos", "Nenhum veículo disponível.")
        win.destroy()
        abrir_login()
        return
    
    #Mostra as opções para o usuario em opcoes e guarda a id do veiculo em um dicionario mapa
    opcoes = []
    mapa = {}

    for idv, modelo, placa, diaria in veiculos:
        display = f"[{idv}] {modelo} - {placa} - R$ {diaria:.2f}/dia"
        mapa[display] = idv
        opcoes.append(display)

    ctk.CTkLabel(frame, text="Selecione o veículo:").pack(anchor="w")
    var_sel = ctk.StringVar(value=opcoes[0])
    menu_veiculo = ctk.CTkOptionMenu(frame, values=opcoes, variable=var_sel)
    menu_veiculo.pack(pady=5)

    #Datas
    ctk.CTkLabel(frame, text="Data de retirada (AAAA-MM-DD)").pack(anchor="w", pady=(10,2))
    entrada_ini = ctk.CTkEntry(frame)
    entrada_ini.pack(fill="x")

    ctk.CTkLabel(frame, text="Data de devolução (AAAA-MM-DD)").pack(anchor="w", pady=(10,2))
    entrada_fim = ctk.CTkEntry(frame)
    entrada_fim.pack(fill="x")

    #Criar Reserva
    def criar_reserva():
        # validar datas
        try:
            d1 = datetime.strptime(entrada_ini.get(), "%Y-%m-%d").date()
            d2 = datetime.strptime(entrada_fim.get(), "%Y-%m-%d").date()
        except:
            tkmb.showerror("Erro", "Datas inválidas.")
            return

        if d2 < d1:
            tkmb.showerror("Erro", "Devolução não pode ser antes da retirada.")
            return

        #Obter veículo selecionado
        idv = mapa[var_sel.get()]
        veiculo = veiculo_dao.buscar_por_id(idv)

        #Chama o método do cliente para fazer a reserva
        try:
            reserva = cliente.fazer_reserva(veiculo, d1, d2)
            reserva_dao.salvar(reserva)
            veiculo_dao.salvar(veiculo)
        except Exception as e:
            tkmb.showerror("Erro", str(e))
            return

        tkmb.showinfo("Successo", f"Reserva criada! ID: {reserva.id}")

    #Botão de criar a reserva e voltar
    ctk.CTkButton(frame, text="Confirmar Reserva", fg_color="#1E8449", command=criar_reserva).pack(pady=15)
    ctk.CTkButton(frame, text="Voltar", fg_color="gray", command=lambda: abrir_tela_cliente(win, cliente.email)).pack()

    win.mainloop()

#Realizar Pagamento
def abrir_tela_pagamento(prev_window, cliente):
    from ui_main import abrir_login
    try:
        prev_window.destroy()
    except:
        pass

    base = BaseDAO(CAMINHO_DB)
    cliente_dao = ClienteDAO(CAMINHO_DB)
    veiculo_dao = VeiculoDAO(CAMINHO_DB)
    pagamento_dao = PagamentoDAO(CAMINHO_DB)
    reserva_dao = ReservaDAO(cliente_dao, veiculo_dao, pagamento_dao, CAMINHO_DB)

    #Busca na base de dados reservas que estão com o status de pagamento "pendente"
    conn = base.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
    r.reserva_id,
    r.veiculo_id,
    r.data_inicio,
    r.data_fim,
    v.modelo,
    v.placa,
    v.valor_diaria
    FROM reserva r
    JOIN veiculo v ON r.veiculo_id = v.veiculo_id
    WHERE r.pessoa_id = ? AND r.status = 'pendente'
    """, (cliente.id,))
    reservas = cursor.fetchall()
    conn.close()

    win = ctk.CTk()
    win.title("Pagamento de Reserva")
    win.geometry("600x550")

    ctk.CTkLabel(win, text="Pagamento de Reserva", font=("Inter", 20, "bold")).pack(pady=20)

    #Se não encontrar nenhuma reserva retorna para login
    if not reservas:
        tkmb.showinfo("Nenhuma reserva", "Você não possui reservas pendentes de pagamento.")
        win.destroy()
        abrir_login()
        return

    #Listas reservas
    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    opcoes = []
    mapa_reservas = {}

    for r in reservas:
        (id_res, id_veic, d_ini, d_fim, modelo, placa, diaria) = r

        # converter datas
        dt_ini = datetime.strptime(d_ini, "%Y-%m-%d").date()
        dt_fim = datetime.strptime(d_fim, "%Y-%m-%d").date()

        dias = (dt_fim - dt_ini).days
        if dias < 1:
            dias = 1  # mínimo 1 diária

        #Calcula valor total (Deveria estar no model zzz)
        valor_total = dias * diaria

        display = f"ID {id_res} — {modelo} ({placa}) — {dias} dias — R$ {valor_total:.2f}"

        #Guarda dados completos
        mapa_reservas[display] = {"id_reserva": id_res,"valor": valor_total}
        opcoes.append(display)

    var_sel = ctk.StringVar(value=opcoes[0])

    ctk.CTkLabel(frame, text="Selecione a reserva:").pack(anchor="w")
    ctk.CTkOptionMenu(frame, values=opcoes, variable=var_sel).pack(pady=10)

    #Tipos de Pagamento
    metodos = ["Cartao", "Boleto", "Dinheiro", "Transferencia"]
    var_metodo = ctk.StringVar(value="Cartao")

    ctk.CTkLabel(frame, text="Forma de pagamento:").pack(anchor="w", pady=(10,2))
    ctk.CTkOptionMenu(frame, values=metodos, variable=var_metodo).pack(pady=5)

    #Confimar pagamento para o BD
    def confirmar_pagamento():
        selecao = var_sel.get()
        dados = mapa_reservas[selecao]

        id_reserva = dados["id_reserva"]
        valor_total = dados["valor"]
        metodo = var_metodo.get()

        try:
            # Atualizar status da reserva
            conn2 = base.get_connection()
            cursor2 = conn2.cursor()

            cursor2.execute("""
                UPDATE reserva
                SET status = 'confirmada'
                WHERE reserva_id = ?
            """, (id_reserva,))

            conn2.commit()
            conn2.close()

            tkmb.showinfo(
                "Sucesso",
                f"Pagamento confirmado!\nReserva {id_reserva} paga com {metodo}."
            )

            win.destroy()
            abrir_tela_cliente(None, cliente.email)

        except Exception as e:
            tkmb.showerror("Erro", f"Falha ao processar pagamento:\n{e}")

    ctk.CTkButton(frame, text="Confirmar Pagamento", fg_color="#1E8449", command=confirmar_pagamento).pack(pady=20)
    ctk.CTkButton(frame, text="Voltar", fg_color="gray", command=lambda: abrir_tela_cliente(win, cliente.email)).pack()

    win.mainloop()

#Realizar devolução de Veículo
def abrir_tela_devolver_veiculo(prev_window, cliente):
    from ui_main import abrir_login
    try:
        prev_window.destroy()
    except:
        pass

    base = BaseDAO(CAMINHO_DB)
    cliente_dao = ClienteDAO(CAMINHO_DB)
    veiculo_dao = VeiculoDAO(CAMINHO_DB)
    pagamento_dao = PagamentoDAO(CAMINHO_DB)
    reserva_dao = ReservaDAO(cliente_dao, veiculo_dao, pagamento_dao, CAMINHO_DB)
    locacao_dao = LocacaoDAO(reserva_dao, CAMINHO_DB)

    #Busca na BD locações com o status "em andamento"
    conn = base.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            l.locacao_id,
            l.reserva_id,
            r.veiculo_id,
            v.modelo,
            v.placa,
            r.data_inicio,
            r.data_fim
        FROM locacao l
        JOIN reserva r ON r.reserva_id = l.reserva_id
        JOIN veiculo v ON v.veiculo_id = r.veiculo_id
        WHERE r.pessoa_id = ? AND l.status = 'em andamento'
    """, (cliente.id,))
    locacoes = cursor.fetchall()
    conn.close()

    #Cria menu
    win = ctk.CTk()
    win.title("Devolver Veículo")
    win.geometry("600x500")

    ctk.CTkLabel(win, text="Devolver Veículo",font=("Inter", 20, "bold")).pack(pady=20)

    if not locacoes:
        tkmb.showinfo("Nenhuma locação", "Você não possui locações em andamento.")
        win.destroy()
        abrir_tela_cliente(None, cliente.email)
        return

    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Lista de locações
    opcoes = []
    mapa = {}

    for loco in locacoes:
        (id_loc, id_res, id_veic, modelo, placa, d1, d2) = loco
        texto = f"Locação {id_loc} — {modelo} ({placa})"
        opcoes.append(texto)
        mapa[texto] = loco

    var_sel = ctk.StringVar(value=opcoes[0])

    ctk.CTkLabel(frame, text="Selecione a locação:").pack(anchor="w")
    ctk.CTkOptionMenu(frame, values=opcoes, variable=var_sel).pack(pady=10)

    #Processamento da devolução
    def confirmar_devolucao():
        selecao = var_sel.get()
        (id_loc, id_res, id_veic, modelo, placa, d1, d2) = mapa[selecao]

        hoje = date.today()

        try:
            #Atualizar locação
            conn1 = base.get_connection()
            cur1 = conn1.cursor()
            cur1.execute("""
                UPDATE locacao 
                SET data_devolucao_real = ?, km_devolucao = 100, status = 'finalizada'
                WHERE locacao_id = ?
            """, (hoje.isoformat(), id_loc))
            conn1.commit()
            conn1.close()

            #Atualizar veículo para disponível
            conn2 = base.get_connection()
            cur2 = conn2.cursor()
            cur2.execute("""
                UPDATE veiculo
                SET status = 'disponivel'
                WHERE veiculo_id = ?
            """, (id_veic,))
            conn2.commit()
            conn2.close()

            tkmb.showinfo("Sucesso", f"Veículo {modelo} ({placa}) devolvido com sucesso!")

        except Exception as e:
            tkmb.showerror("Erro", f"Erro ao processar devolução:\n{e}")

    ctk.CTkButton(frame, text="Confirmar Devolução", fg_color="#1E8449", command=confirmar_devolucao).pack(pady=20)
    ctk.CTkButton(frame, text="Voltar", fg_color="gray", command=lambda: abrir_tela_cliente(win, cliente.email)).pack()

    win.mainloop()