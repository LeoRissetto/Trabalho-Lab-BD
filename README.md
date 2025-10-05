# Projeto Lar Temporário - Sistema de Gestão para ONG de Adoção de Gatos

Sistema de banco de dados para gerenciamento completo de uma ONG voltada para o resgate e adoção de gatos, desenvolvido como trabalho para a disciplina de Laboratório de Banco de Dados.

## Equipe

- **Leonardo Gueno Rissetto** - 13676482
- **Luciano Lopes Gonçalves** - 13676520
- **Pedro Guilherme de Barros Zenatte** - 13676919
- **Rauany Martinez Secci** - 13721217

**Professor:** Mirela Teixeira Cazzolato

## Descrição do Projeto

O **Projeto Lar Temporário** tem como objetivo principal desenvolver um sistema que otimize a gestão interna de uma ONG voltada para o resgate e adoção de gatos, oferecendo uma solução completa para a administração eficiente de todas as suas atividades. O sistema foi idealizado para suprir as necessidades de organização e gerenciamento dos animais, das pessoas envolvidas e dos eventos promovidos pela ONG, garantindo maior controle, transparência e agilidade em seus processos.

### Público-Alvo

- **Gestores e Administradores**: Controle de finanças, doações, campanhas e eventos
- **Voluntários**: Auxílio em resgates, cuidados, triagens e suporte às ações
- **Responsáveis por Lares Temporários**: Gestão de capacidade e registros de hospedagem
- **Veterinários**: Controle de procedimentos e histórico médico dos animais
- **Adotantes**: Processo completo de adoção e acompanhamento

### Funcionalidades Principais

#### Gestão de Pessoas
- **Cadastro completo** com CPF único, nome, telefone, e-mail e endereço
- **Categorização** por papel na ONG (veterinário, adotante, voluntário, contato)
- **Triagem de adotantes** com avaliação de residência e documentação

#### Gestão de Gatos
- **Registro detalhado** com ID único, nome, idade, data/local de resgate
- **Informações físicas** como cor, raça e fotos
- **Histórico médico** completo com procedimentos veterinários
- **Controle de hospedagem** em lares temporários

#### Gestão Veterinária
- **Cadastro de veterinários** com CRMV, especialidade e clínica
- **Registro de procedimentos** com data, tipo, custo e responsável
- **Histórico médico** completo dos animais

#### Gestão Financeira
- **Controle de doações** com data, valor e forma de pagamento
- **Registro de gastos** por gato ou lar temporário
- **Transparência financeira** para prestação de contas

#### Gestão de Eventos e Campanhas
- **Organização de eventos** para promoção de adoções
- **Campanhas promocionais** com prêmios e vencedores
- **Captação de novos contatos** e apoiadores

#### Gestão de Lares Temporários
- **Cadastro de lares** com capacidade máxima
- **Controle de ocupação** e disponibilidade
- **Registro de gastos** específicos por lar

#### Processo de Adoção Completo
- **Triagem rigorosa** de candidatos
- **Registro de adoções** com data e observações
- **Controle de devoluções** com motivos documentados
- **Possibilidade de múltiplas adoções** por pessoa

## Estrutura do Projeto

```
Trabalho-Lab-BD/
├── README.md
└── Código/
    ├── Python/
    │   ├── popular_bd.py      # Script para popular o banco com dados fictícios
    │   ├── requirements.txt   # Dependências Python
    │   └── resetar_bd.py      # Script para resetar o banco de dados
    └── SQL/
        ├── consultas.sql           # Consultas SQL de exemplo e relatórios
        └── tabelas_postgresql.sql  # Schema das tabelas PostgreSQL
```

## Modelo de Dados

O sistema implementa um modelo de entidade-relacionamento abrangente que inclui:

### Entidades Principais

- **Pessoa**: Entidade central que representa todos os indivíduos (CPF único)
- **Gato**: Animais do sistema com histórico completo
- **Veterinário**: Profissionais com CRMV e especialidades
- **Adotante**: Pessoas que adotam gatos
- **Voluntário**: Pessoas que auxiliam a ONG
- **Lar Temporário**: Locais de hospedagem dos gatos
- **Evento**: Ações promocionais da ONG
- **Campanha**: Iniciativas com prêmios
- **Doação**: Contribuições financeiras
- **Procedimento**: Atendimentos veterinários
- **Triagem**: Avaliação de candidatos à adoção
- **Gasto**: Controle financeiro detalhado

## Como Executar

### Pré-requisitos

- Docker
- Python 3.7+
- pip

### 1. Configurar o Banco de Dados PostgreSQL

Execute o seguinte comando Docker para criar e iniciar o container PostgreSQL:

```bash
docker run --name bd-trabalho -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

Este comando:
- Cria um container chamado `bd-trabalho`
- Mapeia a porta 5432 do container para a porta 5432 do host
- Define a senha do usuário `postgres` como `mysecretpassword`
- Executa o container em background (`-d`)

### 2. Criar as Tabelas

Execute o script SQL para criar a estrutura do banco:

```bash
# Conectar ao PostgreSQL e executar o script de criação das tabelas
docker exec -i bd-trabalho psql -U postgres -d postgres < Código/SQL/tabelas_postgresql.sql
```

### 3. Instalar Dependências Python

```bash
cd Código/Python
pip install -r requirements.txt
```

### 4. Popular o Banco com Dados Fictícios

```bash
python popular_bd.py
```

### 5. Executar Consultas

Você pode executar as consultas de exemplo:

```bash
docker exec -i bd-trabalho psql -U postgres -d postgres < Código/SQL/consultas.sql
```

## Scripts Úteis

### Resetar o Banco de Dados

Para limpar todos os dados e recriar as tabelas:

```bash
python resetar_bd.py
```

### Conectar Diretamente ao PostgreSQL

```bash
docker exec -it bd-trabalho psql -U postgres -d postgres
```

### Parar e Remover o Container

```bash
# Parar o container
docker stop bd-trabalho

# Remover o container (perderá todos os dados)
docker rm bd-trabalho
```

## Tecnologias Utilizadas

- **PostgreSQL**: Sistema de gerenciamento de banco de dados
- **Python**: Scripts de automação e população de dados
- **psycopg2**: Adapter PostgreSQL para Python
- **Faker**: Geração de dados fictícios
- **Docker**: Containerização do banco de dados

## Configuração do Banco

- **Host**: localhost
- **Porta**: 5432
- **Usuário**: postgres
- **Senha**: mysecretpassword
- **Database**: postgres

---

**Universidade de São Paulo - Instituto de Ciências Matemáticas e de Computação (ICMC)**  
**São Carlos, 2025**