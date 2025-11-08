# Sistema de Locadora de Veículos (OOP + SQLite3)
Uma implementação de um sistema de gerenciamento para locadoras de veículos, focado na aplicação de Programação Orientada a Objetos (POO) e persistência de dados.

Projeto desenvolvido por estudantes do curso de Gestão da Informação da Universidade Federal de Goiás (UFG).

### 🎯 Objetivo
O objetivo deste projeto é aplicar e consolidar conceitos de Programação Orientada a Objetos, modelagem de sistemas com UML (Diagrama de Classes) e persistência de dados utilizando um banco de dados relacional leve (SQLite3) para construir um sistema funcional de gerenciamento de locação de veículos.

### 📊 O Domínio do Sistema
O sistema foi modelado para gerenciar as principais entidades e processos de uma locadora do mundo real. Ele lida com os seguintes componentes:

**Entidades (Pessoas)**: Gerenciamento de Pessoa, que se divide em Cliente (com dados de CNH) e Funcionário (com dados de matrícula e cargo), utilizando Herança.

**Frota**: Cadastro e controle de Veiculo, incluindo o registro de Manutencao (descrição, data e custo).

**Operações**: Gerenciamento do fluxo de negócio principal, desde a Reserva inicial, passando pelo Pagamento, até a Locacao efetiva (retirada e devolução).

### 🏗️ Arquitetura e Modelagem (POO)
A arquitetura do sistema foi projetada utilizando um Diagrama de Classes UML para garantir um código coeso, desacoplado e aderente aos princípios da POO.

Herança: A classe abstrata Pessoa é utilizada como base para Cliente e Funcionário, reutilizando atributos comuns (nome, telefone, etc.) e especializando as subclasses.

Associação e Composição: As classes se relacionam para refletir o negócio:

* Um Cliente faz uma Reserva.

* Uma Reserva está associada a um Veiculo e um Pagamento.

* Uma Reserva confirmada se torna uma Locacao.

* Um Funcionario registra Locacao.

* Um Veiculo possui múltiplas Manutencao.

**Banco de Dados**: O SQLite3 é utilizado para a persistência dos dados, garantindo que as informações dos objetos (clientes, veículos, locações) sejam salvas e recuperadas.

### 🛠️ Tecnologias Utilizadas
As principais ferramentas e bibliotecas utilizadas no desenvolvimento do sistema.

Linguagem: Python

Banco de Dados: SQLite3

Design e Modelagem: UML (Diagrama de Classes) - LucidChard

# 📈 Funcionalidades Implementadas
O sistema atualmente suporta as seguintes operações centrais de negócio:

* Cadastro e atualização de Clientes e Funcionários.

* Registro e gerenciamento da frota de Veículos.

* Criação, confirmação e cancelamento de Reservas.

* Registro completo de Locações (processo de retirada e devolução).

* Controle de Manutenções periódicas dos veículos.

* Processamento de Pagamentos associados às locações.