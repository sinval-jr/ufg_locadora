import customtkinter as ctk
from tkinter import messagebox as tkmb

#Temas
ctk.set_appearance_mode("dark")            
ctk.set_default_color_theme("dark-blue")   

#Usuarios Exemplo, trocar por dados na tabela
usuarios = {
    # trocar depois o usuário do funcionário para matrícula
    "joao@aaa.com": {"senha": "1234", "tipo": "cliente"},
    "pedro@bbb.com": {"senha": "1230489", "tipo": "funcionario"}
}


def abrir_tela_cliente(app):
    """Abre a interface do cliente"""
    app.destroy()  # Fecha a janela anterior
    janela_cliente = ctk.CTk()
    janela_cliente.title("Cliente")
    janela_cliente.geometry("400x350")

    ctk.CTkLabel(janela_cliente, text="Bem-vindo, Cliente!", font=("Inter", 18, "bold")).pack(pady=20)
    ctk.CTkButton(janela_cliente, text="Fazer Reserva", width=200).pack(pady=10)
    ctk.CTkButton(janela_cliente, text="Fazer Pagamento", width=200).pack(pady=10)
    ctk.CTkButton(janela_cliente, text="Sair", width=100, fg_color="gray", command=janela_cliente.destroy).pack(pady=20)
    janela_cliente.mainloop()


def abrir_tela_funcionario(app):
    #Fecha a janaela anterior
    app.destroy()
    janela_func = ctk.CTk()
    janela_func.title("Funcionário")
    janela_func.geometry("400x350")

    #Textos e botões
    ctk.CTkLabel(janela_func, text="Bem-vindo, Funcionário!", font=("Inter", 18, "bold")).pack(pady=20)
    ctk.CTkButton(janela_func, text="Registrar Locação", width=220).pack(pady=10)
    ctk.CTkButton(janela_func, text="Sair", width=100, fg_color="gray", command=janela_func.destroy).pack(pady=20)
    janela_func.mainloop()



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
        if any(v == "" for v in dados.values()):
            tkmb.showwarning("Campos vazios", "Preencha todos os campos antes de continuar.")
            return
        
        # Simulação de cadastro (no futuro, integrar ao banco SQLite)
        usuarios[dados["Email"]] = {"senha": dados["CPF"], "tipo": "cliente"}
        tkmb.showinfo("Sucesso", "Cliente cadastrado com sucesso!")

        cadastro.destroy()
        abrir_login()

    # Botões
    ctk.CTkButton(scroll_frame, text="Cadastrar", fg_color="green", command=salvar_cadastro).pack(pady=20)
    ctk.CTkButton(scroll_frame, text="Cancelar", fg_color="gray",
                  command=lambda: [cadastro.destroy(), abrir_login()]).pack(pady=5)

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

    user_pass = ctk.CTkEntry(master=frame, placeholder_text="CPF", show="*")
    user_pass.pack(pady=10, padx=10)

    #Verifica se o Login esta correto
    def login():
        usuario = user_entry.get()
        senha = user_pass.get()

        if usuario in usuarios and senha == usuarios[usuario]["senha"]:
            tipo = usuarios[usuario]["tipo"]
            tkmb.showinfo("Login bem-sucedido", f"Bem-vindo, {tipo.capitalize()}!")

            if tipo == "cliente":
                abrir_tela_cliente(app)
            else:
                abrir_tela_funcionario(app)
        else:
            tkmb.showerror("Falha no login", "Usuário ou senha incorretos.")

    ctk.CTkButton(master=frame, text="Entrar", command=login).pack(pady=10)
    ctk.CTkButton(master=frame, text="Cadastrar Cliente", fg_color="#1E8449", hover_color="#117A37",
                  command=lambda: cadastrar_cliente(app)).pack(pady=10)
    app.mainloop()

#Exe
if __name__ == "__main__":
    abrir_login()