import sys
import os
from datetime import date, datetime
from model import Cliente, Funcionario, Veiculo, Pagamento
from daos import BaseDAO, ClienteDAO, FuncionarioDAO, VeiculoDAO, ReservaDAO, LocacaoDAO, PagamentoDAO

# Procura por todos os locadora.db dentro da pasta do projeto (pode demorar pouco)
for root, dirs, files in os.walk(os.getcwd()):
    if "locadora.db" in files:
        print("found:", os.path.join(root, "locadora.db"))

# --- SETUP INICIAL DOS DAOS    ---
base_dao = BaseDAO()
base_dao.criar_tabelas()

veiculo_dao = VeiculoDAO()
cliente_dao = ClienteDAO("locadora.db")
funcionario_dao = FuncionarioDAO("locadora.db")
pagamento_dao = PagamentoDAO()

reserva_dao = ReservaDAO(cliente_dao, veiculo_dao, funcionario_dao, pagamento_dao, "locadora.db")
locacao_dao = LocacaoDAO(reserva_dao, "locadora.db")

# --- FUNÇÕES UTILITÁRIAS ---
def input_data(mensagem):
    """Solicita uma data no formato YYYY-MM-DD"""
    while True:
        try:
            data_str = input(f"{mensagem} (AAAA-MM-DD): ")
            return datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            print("❌ Formato inválido! Tente novamente.")

def listar_veiculos_disponiveis():
    print("\n--- Veículos Disponíveis ---")
    conn = veiculo_dao.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, modelo, placa, valor_diaria FROM veiculos WHERE status='disponivel'")
    veiculos = cursor.fetchall()
    conn.close()
    
    if not veiculos:
        print("Nenhum veículo disponível.")
        return []
    
    for v in veiculos:
        print(f"[ID: {v[0]}] {v[1]} - {v[2]} (R$ {v[3]:.2f}/dia)")
    return [v[0] for v in veiculos]

def selecionar_funcionario():
    """Simula login de um funcionário (pega o primeiro do banco ou pede ID)"""
    # Simplificação: Pede o ID
    try:
        id_func = int(input("Digite seu ID de Funcionário: "))
        func = funcionario_dao.buscar_por_id(id_func)
        if func:
            return func
        print("❌ Funcionário não encontrado.")
    except:
        print("❌ ID inválido.")
    return None

# --- MENUS DE AÇÃO ---

def menu_cliente():
    print("\n=== ÁREA DO CLIENTE ===")
    print("1. Novo Cadastro")
    print("2. Fazer Reserva")
    print("3. Pagar Reserva")
    print("0. Voltar")
    
    op = input("Escolha: ")
    
    if op == "1":
        print("\n--- Cadastro de Cliente ---")
        nome = input("Nome: ")
        cpf = input("CPF (11 dígitos): ")
        cnh = input("CNH (B): ")
        tel = input("Telefone: ")
        email = input("Email: ")
        # Endereço fixo para simplificar o exemplo
        cli = Cliente(nome, tel, email, "Rua Cliente", 0, "Cidade", "UF", "00000", cpf, cnh)
        try:
            cliente_dao.salvar(cli)
            print(f"✅ Cliente {cli.nome} cadastrado com ID: {cli.id}")
        except Exception as e:
            print(f"❌ Erro ao cadastrar: {e}")

    elif op == "2":
        print("\n--- Nova Reserva ---")
        try:
            cli_id = int(input("Digite seu ID de Cliente: "))
            cliente = cliente_dao.buscar_por_id(cli_id)
            if not cliente:
                print("Cliente não encontrado.")
                return

            ids_validos = listar_veiculos_disponiveis()
            if not ids_validos: return
            
            v_id = int(input("Digite o ID do veículo desejado: "))
            veiculo = veiculo_dao.buscar_por_id(v_id)
            
            dt_ini = input_data("Data de Retirada")
            dt_fim = input_data("Data de Devolução")
            
            reserva = cliente.fazer_reserva(veiculo, dt_ini, dt_fim)
            
            # Persistir mudanças
            reserva_dao.salvar(reserva)
            veiculo_dao.salvar(veiculo) # Atualiza status para 'reservado'
            
            print(f"✅ Reserva salva! ID: {reserva.id}. Valor previsto: R$ {reserva.valor_total_previsto:.2f}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

    elif op == "3":
        print("\n--- Pagamento de Reserva ---")
        try:
            res_id = int(input("ID da Reserva: "))
            reserva = reserva_dao.buscar_por_id(res_id)
            if not reserva:
                print("Reserva não encontrada.")
                return
            
            print(f"Valor Pendente: R$ {reserva.valor_total_previsto:.2f}")
            val = float(input("Valor a pagar: "))
            
            # 1. Cria o objeto Pagamento em memória
            pgto = Pagamento("pix", val, date.today(), "reserva")
            
            # 2. Adiciona na lista da reserva (Lógica de Negócio)
            reserva.adicionar_pagamento(pgto)
            
            # 3. SALVA NO BANCO DE DADOS (AQUI É A MUDANÇA)
            # Salvamos o pagamento vinculando-o ao ID da reserva
            pagamento_dao.salvar(pgto, reserva.id)
            
            # Opcional: Salvar a reserva também para garantir que se o status 
            # mudou (ex: pagou tudo), o status novo fique salvo.
            reserva_dao.salvar(reserva)

            print(f"✅ Pagamento de R${val:.2f} registrado no Banco de Dados!")
            
        except ValueError:
            print("Valor inválido.")

def menu_funcionario():
    func = selecionar_funcionario()
    if not func: return

    print(f"\n=== ÁREA DO FUNCIONÁRIO: {func.nome} ===")
    
    print("1. Registrar Locação (Entregar Veículo)")
    print("2. Receber Veículo (Finalizar)")
    print("3. Cadastrar Novo Veículo")
    print("0. Voltar")
    
    op = input("Escolha: ")
    
    if op == "1":
        try:
            res_id = int(input("ID da Reserva para retirar: "))
            reserva = reserva_dao.buscar_por_id(res_id)
            
            if reserva:
                # Associa este funcionário à reserva
                reserva._funcionario = func
                reserva_dao.salvar(reserva) 
                
                locacao = func.entregar_veiculo(reserva)
                
                if locacao:
                    locacao_dao.salvar(locacao)
                    veiculo_dao.salvar(reserva._veiculo) # Atualiza status 'alugado'
                    print(f"✅ Locação iniciada! ID Locação: {locacao.id}")
            else:
                print("Reserva não encontrada.")
        except Exception as e:
            print(f"❌ Erro no processo: {e}")

    elif op == "2":
        try:
            loc_id = int(input("ID da Locação para encerrar: "))
            locacao = locacao_dao.buscar_por_id(loc_id)
            
            if locacao:
                km_atual = int(input("KM atual do veículo: "))
                func.finalizar_locacao(locacao, km_atual, "dinheiro")
                
                # Salvar atualizações
                locacao_dao.salvar(locacao)
                veiculo_dao.salvar(locacao._reserva._veiculo) # Atualiza status e km
                
                print("✅ Locação Finalizada e Veículo Liberado.")
            else:
                print("Locação não encontrada.")
        except Exception as e:
            print(f"❌ Erro: {e}")

    elif op == "3":
        print("\n--- Novo Veículo ---")
        modelo = input("Modelo: ")
        placa = input("Placa: ")
        km = int(input("KM Atual: "))
        diaria = float(input("Valor Diária: "))
        
        v = Veiculo(placa, modelo, "disponivel", km, diaria, 0.50)
        veiculo_dao.salvar(v)
        print(f"✅ Veículo {v.modelo} cadastrado com ID {v.id}")

def menu_veiculo():
    print("\n=== GESTÃO DE VEÍCULOS ===")
    print("1. Listar Todos")
    print("2. Adicionar Manutenção")
    print("0. Voltar")
    
    op = input("Escolha: ")
    
    if op == "1":
        listar_veiculos_disponiveis()
        
    elif op == "2":
        print("Funcionalidade de manutenção (simulação):")
        v_id = input("ID do Veículo: ")
        desc = input("Descrição da manutenção: ")
        print(f"✅ Manutenção '{desc}' registrada para o veículo {v_id}.")

# --- LOOP PRINCIPAL ---

if __name__ == "__main__":
    if not funcionario_dao.buscar_por_id(1):
        admin = Funcionario("Admin", "000", "admin@loc.com", "Rua A", 1, "City", "UF", "000", "MAT01", "Gerente", 5000)
        funcionario_dao.salvar(admin)
        print("⚠️ Funcionário ADMIN criado automaticamente (ID: 1)")

    while True:
        print("\n" + "="*30)
        print("🚗 SISTEMA LOCADORA - MENU PRINCIPAL")
        print("="*30)
        print("1. Menu Cliente")
        print("2. Menu Funcionário")
        print("3. Menu Veículos")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            menu_cliente()
        elif opcao == "2":
            menu_funcionario()
        elif opcao == "3":
            menu_veiculo()
        elif opcao == "0":
            print("Saindo do sistema... Até logo!")
            break
        else:
            print("Opção inválida!")
