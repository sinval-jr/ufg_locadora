import customtkinter as ctk
from tkinter import messagebox as tkmb
from datetime import date, datetime
from daos import BaseDAO, ClienteDAO, VeiculoDAO, ReservaDAO, PagamentoDAO, FuncionarioDAO, LocacaoDAO, ManutencaoDAO
from model import Cliente, Locacao, Manutencao

#Caminho
CAMINHO_DB = "locadora.db"

#Janela do Funcionário (Chamada do arquivo ui_main.py)
def abrir_tela_funcionario(prev_window, nome_funcionario):

    try:
        prev_window.destroy()
    except:
        pass

    base = BaseDAO(CAMINHO_DB)
    funcionario_dao = FuncionarioDAO(CAMINHO_DB)

    # Janela principal
    menu = ctk.CTk()
    menu.title("Área do Funcionário")
    menu.geometry("500x400")

    ctk.CTkLabel(
        menu,
        text=f"Bem-vindo(a), {nome_funcionario}",
        font=("Inter", 20, "bold")
    ).pack(pady=20)

    frame = ctk.CTkFrame(menu)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    #botões
    ctk.CTkButton(frame, text="Registrar Locação", height= 50, command=lambda: abrir_tela_registrar_locacao(menu)).pack(pady=10)
    ctk.CTkButton(frame, text="Registrar Veículo", height=50, command=lambda: abrir_tela_registrar_veiculo(menu)).pack(pady=10)
    ctk.CTkButton(frame, text="Registrar Manutenção", height=50, command=lambda: abrir_tela_registrar_manutencao(menu)).pack(pady=10)

    #Função voltar
    def voltar_login():
        menu.destroy()
        from ui_main import abrir_login
        abrir_login()

    ctk.CTkButton(frame, text="Sair", fg_color="gray", command=voltar_login ).pack(pady=20)

    menu.mainloop()

#Registrar locação
def abrir_tela_registrar_locacao(prev_window):

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

    #Busca no DB reservas com status "confirmada"
    conn = base.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.reserva_id, r.veiculo_id, r.data_inicio, r.data_fim,
               v.modelo, v.placa, v.kmatual
        FROM reserva r
        JOIN veiculo v ON v.veiculo_id = r.veiculo_id
        WHERE r.status = 'confirmada'
    """)
    reservas = cursor.fetchall()
    conn.close()

    win = ctk.CTk()
    win.title("Registrar Locação")
    win.geometry("600x500")

    ctk.CTkLabel(win, text="Registrar Locação", font=("Inter", 20, "bold")).pack(pady=20)

    #Caso não encontre
    if not reservas:
        tkmb.showinfo("Aviso", "Nenhuma reserva confirmada disponível.")
        win.destroy()
        return

    frame = ctk.CTkFrame(win)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    #Display e salvamento na base
    opcoes = []
    mapa_reservas = {}

    for r in reservas:
        id_res, id_veic, d1, d2, modelo, placa, kmatual = r
        display = f"ID {id_res} — {modelo} ({placa}) — km {kmatual}"
        mapa_reservas[display] = r
        opcoes.append(display)

    var_sel = ctk.StringVar(value=opcoes[0])

    ctk.CTkLabel(frame, text="Selecione a reserva:").pack(anchor="w")
    ctk.CTkOptionMenu(frame, values=opcoes, variable=var_sel).pack(pady=10)

    #Função para confimar locação
    def confirmar_locacao():
        selecao = var_sel.get()
        id_res, id_veic, d1, d2, modelo, placa, kmatual = mapa_reservas[selecao]

        try:
            # Criar objeto Reserva
            reserva = reserva_dao.buscar_por_id(id_res)

            # Criar locação (status 'em andamento')
            hoje = date.today()
            locacao = Locacao(
                reserva=reserva,
                data_retirada=hoje,
                km_retirada=kmatual,
                status="em andamento"
            )
            
            #Salar
            locacao_dao.salvar(locacao)

            # Atualizar reserva para "em andamento"
            conn2 = base.get_connection()
            cursor2 = conn2.cursor()
            cursor2.execute("""
                UPDATE reserva
                SET status = 'em andamento'
                WHERE reserva_id = ?
            """, (id_res,))
            conn2.commit()
            conn2.close()

            tkmb.showinfo("Sucesso",
                          f"Locação registrada!\nReserva {id_res} agora está em andamento.")


        except Exception as e:
            tkmb.showerror("Erro", f"Falha ao registrar locação:\n{e}")

    ctk.CTkButton(frame, text="Confirmar Locação", fg_color ="green", command=confirmar_locacao).pack(pady=20)
    ctk.CTkButton(frame, text="Voltar", fg_color="gray", command=lambda: abrir_tela_funcionario(win, "Funcionário")).pack()

    win.mainloop()

#Registrar Veículo
def abrir_tela_registrar_veiculo(prev_window):

    try:
        prev_window.destroy()
    except:
        pass

    base = BaseDAO(CAMINHO_DB)
    veiculo_dao = VeiculoDAO(CAMINHO_DB)

    win = ctk.CTk()
    win.title("Registrar Veículo")
    win.geometry("480x600")

    ctk.CTkLabel(win, text="Registrar Veículo", font=("Inter", 18, "bold")).pack(pady=15)

    #Criar scrol pra tela
    scroll = ctk.CTkScrollableFrame(win, width=440, height=480)
    scroll.pack(padx=20, pady=10, fill="both", expand=True)

    campos = {
        "Placa": None,
        "Modelo": None,
        "KM Atual": None,
        "Valor da Diária": None,
        "Preço por KM": None
    }

    entradas = {}
    for campo in campos.keys():
        ctk.CTkLabel(scroll, text=campo).pack(pady=2)
        entradas[campo] = ctk.CTkEntry(scroll, placeholder_text=f"Digite o {campo.lower()}")
        entradas[campo].pack(pady=4)

    #Função para salvar registro
    def salvar_veiculo():
        dados = {c: entradas[c].get().strip() for c in entradas}

        # Verificação básica
        if any(v == "" for v in dados.values()):
            tkmb.showwarning("Campos vazios", "Preencha todos os campos antes de continuar.")
            return

        try:
            placa = dados["Placa"]
            modelo = dados["Modelo"]
            km = int(dados["KM Atual"])
            diaria = float(dados["Valor da Diária"])
            preco_km = float(dados["Preço por KM"])

            from model import Veiculo
            veiculo = Veiculo(
                placa=placa,
                modelo=modelo,
                status="disponivel",  # novo veículo sempre disponível
                kmatual=km,
                valor_diaria=diaria,
                preco_por_km=preco_km
            )

            veiculo_dao.salvar(veiculo)

            tkmb.showinfo("Sucesso", "Veículo cadastrado com sucesso!")

        except ValueError:
            tkmb.showerror("Erro", "KM, diária e preço por KM devem ser números válidos.")
        except Exception as e:
            tkmb.showerror("Erro", f"Erro ao salvar veículo:\n{e}")

    # Botões
    ctk.CTkButton(scroll, text="Cadastrar Veículo", fg_color="green", command=salvar_veiculo).pack(pady=20)
    ctk.CTkButton(scroll, text="Voltar", fg_color="gray", command=lambda: abrir_tela_funcionario(win, "Funcionário")).pack(pady=5)

    win.mainloop()

#Registrar Manutenção
def abrir_tela_registrar_manutencao(prev_window):

    try:
        prev_window.destroy()
    except:
        pass

    base = BaseDAO(CAMINHO_DB)
    veiculo_dao = VeiculoDAO(CAMINHO_DB)
    manut_dao = ManutencaoDAO(veiculo_dao)

    #Busca veículos disponíveis para manutenção através da busca do status "disponivel"
    conn = base.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT veiculo_id, modelo, placa, kmatual
        FROM veiculo
        WHERE status = 'disponivel'
    """)
    veiculos = cursor.fetchall()
    conn.close()

    win = ctk.CTk()
    win.title("Registrar Manutenção")
    win.geometry("480x600")

    ctk.CTkLabel(win, text="Registrar Manutenção", font=("Inter", 18, "bold")).pack(pady=15)

    scroll = ctk.CTkScrollableFrame(win, width=440, height=480)
    scroll.pack(padx=20, pady=10, fill="both", expand=True)

    #Se não achar nenhum
    if not veiculos:
        tkmb.showinfo("Aviso", "Nenhum veículo disponível para manutenção.")
        win.destroy()
        return

    #Display e salvamento no DB
    ctk.CTkLabel(scroll, text="Selecione o veículo").pack(pady=5)

    opcoes = []
    mapa = {}

    for v in veiculos:
        idv, modelo, placa, km = v
        label = f"{modelo} — {placa} — {km} km"
        opcoes.append(label)
        mapa[label] = v

    var_veic = ctk.StringVar(value=opcoes[0])

    ctk.CTkOptionMenu(scroll, values=opcoes, variable=var_veic).pack(pady=10)

    #Criaão dos campos de texto para descrição
    ctk.CTkLabel(scroll, text="Descrição da manutenção").pack(pady=5)
    ent_desc = ctk.CTkEntry(scroll, placeholder_text="Digite uma descrição")
    ent_desc.pack(pady=5)

    ctk.CTkLabel(scroll, text="Custo (R$)").pack(pady=5)
    ent_custo = ctk.CTkEntry(scroll, placeholder_text="Somente números")
    ent_custo.pack(pady=5)

    ctk.CTkLabel(scroll, text="Data da manutenção (AAAA-MM-DD)").pack(pady=5)
    ent_data = ctk.CTkEntry(scroll, placeholder_text="Ex: 2025-10-10")
    ent_data.pack(pady=5)

    #Função para salvar o registro na DB
    def registrar_manutencao():
        selecao = var_veic.get()
        (idv, modelo, placa, km) = mapa[selecao]

        desc = ent_desc.get().strip()
        custo_raw = ent_custo.get().strip()
        data_raw = ent_data.get().strip()

        if desc == "" or custo_raw == "" or data_raw == "":
            tkmb.showwarning("Campos vazios", "Preencha todos os campos.")
            return

        try:
            custo = float(custo_raw)
            data_inicio = datetime.strptime(data_raw, "%Y-%m-%d").date()
        except ValueError:
            tkmb.showerror("Erro", "Custo ou data inválidos.")
            return

        veiculo = veiculo_dao.buscar_por_id(idv)

        # Criar objeto Manutencao
        from model import Manutencao
        man = Manutencao(
            veiculo=veiculo,
            descricao=desc,
            data_inicio=data_inicio,
            custo=custo
        )
        man._status = "em andamento"

        try:
            # Salvar a manutenção no banco
            manut_dao.salvar(man)

            # Atualizar veículo para status "manutencao"
            conn2 = base.get_connection()
            cursor2 = conn2.cursor()
            cursor2.execute("""
                UPDATE veiculo 
                SET status = 'manutencao'
                WHERE veiculo_id = ?
            """, (idv,))
            conn2.commit()
            conn2.close()

            tkmb.showinfo(
                "Sucesso",
                f"Manutenção registrada para o veículo {modelo} ({placa})."
            )

        except Exception as e:
            tkmb.showerror("Erro", f"Erro ao registrar manutenção:\n{e}")

    ctk.CTkButton(scroll, text="Registrar Manutenção", fg_color="green",command=registrar_manutencao).pack(pady=20)
    ctk.CTkButton(scroll, text="Voltar", fg_color="gray", command=lambda: abrir_tela_funcionario(win, "Funcionário")).pack(pady=5)

    win.mainloop()