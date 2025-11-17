from daos import ClienteDAO, FuncionarioDAO, BaseDAO
from cliente_ui import abrir_tela_cliente
from funcionario_ui import abrir_tela_funcionario
from model import Cliente
import customtkinter as ctk #pip install customtkinter
from tkinter import messagebox as tkmb 

#Conexão com o banco de dados
CAMINHO_DB = "locadora.db"

base = BaseDAO(CAMINHO_DB)
base.criar_tabelas()

cliente_dao = ClienteDAO(CAMINHO_DB)
funcionario_dao = FuncionarioDAO(CAMINHO_DB)

#Temas
ctk.set_appearance_mode("dark")            
ctk.set_default_color_theme("dark-blue")   

def cadastrar_cliente(app):
    # Fecha a janela anterior
    app.destroy()
    cadastro = ctk.CTk()
    cadastro.title("Cadastro de Cliente")
    cadastro.geometry("480x600")

    ctk.CTkLabel(cadastro, text="Cadastro de Cliente", font=("Inter", 18, "bold")).pack(pady=15)
    # Adicionado scrolbar porque antes não estava cabendo dentro da janela
    scroll_frame = ctk.CTkScrollableFrame(cadastro, width=440, height=480)
    scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)

    # Campos do formulário
    campos = {
        "Nome": None,
        "Telefone": None,
        "Email": None,
        "Rua": None,
        "Número": None,
        "Cidade": None,
        "Estado": None,
        "CEP": None,
        "CPF": None,
        "CNH": None,
    }

    entradas = {}
    for campo in campos.keys():
        ctk.CTkLabel(scroll_frame, text=campo).pack(pady=2)
        entradas[campo] = ctk.CTkEntry(scroll_frame, placeholder_text=f"Digite seu {campo.lower()}")
        entradas[campo].pack(pady=4)

    # Função para salvar o cadastro
    def salvar_cadastro():
        dados = {campo: entrada.get() for campo, entrada in entradas.items()}
        # Verifica se há campos vazios
        if any(v.strip() == "" for v in dados.values()):
            tkmb.showwarning("Campos vazios", "Preencha todos os campos antes de continuar.")
            return
            # Cria e insere a pessoa
        try:
            cliente = Cliente(
                dados["Nome"],
                dados["Telefone"],
                dados["Email"],
                dados["Rua"],
                int(dados["Número"]),
                dados["Cidade"],
                dados["Estado"],
                dados["CEP"],
                dados["CPF"],
                dados["CNH"]
            )

            cliente_dao.salvar(cliente)
        except Exception as e:
            tkmb.showerror("Erro", f"Erro ao salvar: {e}")
            return
        
        tkmb.showinfo("Sucesso", "Cliente cadastrado com sucesso!")
        cadastro.destroy()
        abrir_login()
    # Botões
    ctk.CTkButton(scroll_frame, text="Cadastrar", fg_color="green", command=salvar_cadastro).pack(pady=20)
    ctk.CTkButton(scroll_frame, text="Cancelar", fg_color="gray",command=lambda: [cadastro.destroy(), abrir_login()]).pack(pady=5)

    cadastro.mainloop()


#Função Principal
def abrir_login():
    #Tela principal
    app = ctk.CTk()
    app.geometry("400x400")
    app.title("Sistema de Locadora - Login")

    ctk.CTkLabel(app, text="SISTEMA DE LOCADORA", font=("Inter", 20, "bold")).pack(pady=20)

    frame = ctk.CTkFrame(master=app)
    frame.pack(pady=20, padx=40, fill="both", expand=True)

    ctk.CTkLabel(master=frame, text="LOGIN", font=("Inter", 16, "bold")).pack(pady=12)

    user_entry = ctk.CTkEntry(master=frame, placeholder_text="Usuário")
    user_entry.pack(pady=10, padx=10)

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="Senha")
    user_pass.pack(pady=10, padx=10)

    #Verifica se o Login esta correto
    def login():
        usuario = user_entry.get()
        senha = user_pass.get()

        conn = base.get_connection()
        cursor = conn.cursor()

        # Verifica se é cliente (usa email e CPF)
        cursor.execute("""
        SELECT p.email, p.nome
        FROM pessoa p
        JOIN cliente c ON c.pessoa_id = p.pessoa_id
        WHERE p.email = ? AND c.cpf = ?
        """, (usuario, senha))
        cliente = cursor.fetchone()


        if cliente:
            tkmb.showinfo("Login", f"Bem-vindo, {cliente[0]} (Cliente)")
            abrir_tela_cliente(app, cliente[0])
            return

        # Verifica se é funcionário (usa email e matricula)
        cursor.execute("""
            SELECT p.nome, f.matricula 
            FROM pessoa p
            JOIN funcionario f ON f.pessoa_id = p.pessoa_id
            WHERE p.email = ? AND f.matricula = ?
        """, (usuario, senha))
        funcionario = cursor.fetchone()

        if funcionario:
            tkmb.showinfo("Login", f"Bem-vindo, {funcionario[0]} (Funcionário)")
            abrir_tela_funcionario(app, funcionario[0])
            return

        tkmb.showerror("Erro", "Usuário ou senha incorretos.")

    ctk.CTkButton(master=frame, text="Entrar", command=login).pack(pady=10)
    ctk.CTkButton(master=frame, text="Cadastrar Cliente", fg_color="#1E8449", hover_color="#117A37",
                  command=lambda: cadastrar_cliente(app)).pack(pady=10)
    app.mainloop()

#abrir janela
if __name__ == "__main__":
    abrir_login()