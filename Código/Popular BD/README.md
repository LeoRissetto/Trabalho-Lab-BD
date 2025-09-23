# Populador de Banco de Dados - Sistema de Adoção de Gatos

Este script popula o banco de dados PostgreSQL do sistema de adoção de gatos com dados fictícios usando a biblioteca Faker.

## Pré-requisitos

1. **PostgreSQL** instalado e rodando
2. **Python 3.7+** instalado
3. Banco de dados criado e tabelas já executadas (arquivo `tabelas.sql`)

## Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

Antes de executar o script, edite as configurações de conexão no arquivo `popular_bd.py`:

```python
DB_CONFIG = {
    'host': 'localhost',           # Host do PostgreSQL
    'database': 'sistema_adocao_gatos',  # Nome do seu banco de dados
    'user': 'postgres',            # Usuário do PostgreSQL
    'password': 'sua_senha',       # Senha do PostgreSQL
    'port': 5432                   # Porta do PostgreSQL
}
```

## Como usar

1. Certifique-se de que o banco de dados existe e as tabelas foram criadas:
```sql
-- Execute primeiro o arquivo tabelas.sql no seu banco
```

2. Execute o script:
```bash
python popular_bd.py
```

## O que o script faz

O script popula todas as tabelas do sistema respeitando as foreign keys na ordem correta:

### Tabelas base:
- **100 Pessoas** com dados completos (CPF, nome, telefone, email, endereço)
- **50 Gatos** com informações de resgate, saúde e características
- **10 Campanhas** de arrecadação ou conscientização
- **20 Eventos** de adoção e outros
- **15 Lares temporários** para hospedar gatos

### Especializações:
- **30 Voluntários** (subconjunto das pessoas)
- **40 Adotantes** (subconjunto das pessoas)
- **8 Veterinários** (subconjunto das pessoas)

### Relacionamentos e transações:
- Funções dos voluntários
- Doações (80 registros)
- Participações em campanhas
- Contatos (100 registros)
- Cuidadores de lares
- Participações em eventos
- Fotos dos gatos
- Hospedagens em lares temporários
- Gastos (150 registros)
- Procedimentos veterinários (100 registros)
- Preferências de adotantes
- Triagens de adotantes
- Fotos de triagens
- Adoções (20 registros)
- Devoluções (3 registros)

## Características do script

- **CPFs válidos**: Gera CPFs com dígitos verificadores corretos
- **Dados realistas**: Usa Faker em português brasileiro
- **Integridade referencial**: Respeita todas as foreign keys
- **Tratamento de erros**: Rollback automático em caso de erro
- **Logs detalhados**: Mostra progresso da inserção
- **Dados variados**: Usa listas predefinidas para cores, raças, tipos, etc.

## Volumes de dados

O script é configurado para inserir volumes moderados ideais para teste:
- Total aproximado: ~1000 registros distribuídos entre todas as tabelas
- Tempo estimado de execução: 30-60 segundos

## Troubleshooting

### Erro de conexão
- Verifique se o PostgreSQL está rodando
- Confirme as credenciais no `DB_CONFIG`
- Teste a conexão manualmente

### Erro de foreign key
- Certifique-se de que as tabelas foram criadas na ordem correta
- Verifique se não há dados existentes que possam causar conflito

### Erro de CPF duplicado
- O script tenta evitar duplicatas, mas em casos raros pode tentar inserir CPFs iguais
- Execute novamente o script

## Customização

Para alterar as quantidades de registros, edite os parâmetros nas chamadas das funções na `main()`:

```python
popular_pessoas(cursor, 200)  # Aumenta para 200 pessoas
popular_gatos(cursor, 100)    # Aumenta para 100 gatos
# etc...
```