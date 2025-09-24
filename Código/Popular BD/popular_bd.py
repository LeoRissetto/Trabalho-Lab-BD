import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
import sys
from decimal import Decimal

# Configuração do Faker para português brasileiro
fake = Faker('pt_BR')

# Configurações de conexão com o banco de dados
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'mysecretpassword',
    'port': 5432
}

# Listas para armazenar IDs gerados e reutilizar nas foreign keys
pessoas_cpfs = []
voluntarios_cpfs = []
adotantes_cpfs = []
veterinarios_cpfs = []
gatos_ids = []
campanhas_ids = []
eventos_ids = []
lares_ids = []
enderecos_ids = []
enderecos_usados_lares = []  # Para controlar endereços únicos de lares


def limpar_banco(cursor):
    """Limpa todas as tabelas do banco de dados"""
    print("Limpando tabelas existentes...")
    
    # Ordem de limpeza respeitando as foreign keys
    tabelas = [
        'devolucao', 'adocao', 'fotos_triagem', 'triagem', 'preferencia',
        'procedimento', 'gasto', 'hospedagem', 'fotos_gato', 'gatos_evento',
        'voluntarios_evento', 'cuida_lar', 'contato', 'participantes',
        'doacao', 'funcao', 'lar_temporario', 'veterinario', 'adotante',
        'voluntario', 'evento', 'campanha', 'gato', 'pessoa', 'endereco'
    ]
    
    for tabela in tabelas:
        cursor.execute(f"DELETE FROM {tabela}")
        print(f"  Tabela {tabela} limpa")


def conectar_bd():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        sys.exit(1)


def gerar_cpf_valido():
    """Gera um CPF válido fictício"""
    # Gera 9 primeiros dígitos
    cpf = [random.randint(0, 9) for _ in range(9)]
    
    # Calcula primeiro dígito verificador
    soma = sum(a * b for a, b in zip(cpf, range(10, 1, -1)))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    
    # Calcula segundo dígito verificador
    soma = sum(a * b for a, b in zip(cpf, range(11, 1, -1)))
    resto = soma % 11
    cpf.append(0 if resto < 2 else 11 - resto)
    
    return ''.join(map(str, cpf))


def popular_enderecos(cursor, quantidade=200):
    """Popula a tabela endereco"""
    print(f"Inserindo {quantidade} endereços...")
    
    estados_br = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE']
    complementos = ['Apto 101', 'Bloco A', 'Casa 2', 'Fundos', 'Sobrado', 'Apto 201', 'Casa dos fundos']
    
    for _ in range(quantidade):
        cep = fake.postcode().replace('-', '')
        rua = fake.street_name()
        numero = str(random.randint(1, 9999))
        bairro = fake.neighborhood()
        complemento = random.choice(complementos) if random.choice([True, False, False]) else None  # 33% chance
        cidade = fake.city()
        estado = random.choice(estados_br)
        
        cursor.execute("""
            INSERT INTO endereco (cep, rua, numero, bairro, complemento, cidade, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (cep, rua, numero, bairro, complemento, cidade, estado))
        
        endereco_id = cursor.fetchone()[0]
        enderecos_ids.append(endereco_id)


def popular_pessoas(cursor, quantidade=100):
    """Popula a tabela pessoa"""
    print(f"Inserindo {quantidade} pessoas...")
    
    for _ in range(quantidade):
        cpf = gerar_cpf_valido()
        while cpf in pessoas_cpfs:  # Evita CPFs duplicados
            cpf = gerar_cpf_valido()
        
        pessoas_cpfs.append(cpf)
        
        nome = fake.name()
        telefone = fake.phone_number()[:15]
        email = fake.unique.email()
        endereco_id = random.choice(enderecos_ids) if random.choice([True, False, False]) else None  # 33% têm endereço
        
        cursor.execute("""
            INSERT INTO pessoa (cpf, nome, telefone, email, endereco_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (cpf, nome, telefone, email, endereco_id))


def popular_gatos(cursor, quantidade=50):
    """Popula a tabela gato"""
    print(f"Inserindo {quantidade} gatos...")
    
    cores = ['Preto', 'Branco', 'Cinza', 'Laranja', 'Malhado', 'Siamês', 'Rajado']
    racas = ['SRD', 'Persa', 'Siamês', 'Maine Coon', 'British Shorthair', 'Ragdoll']
    
    for _ in range(quantidade):
        nome = fake.first_name()
        idade = random.randint(0, 15)
        data_resgate = fake.date_between(start_date='-2y', end_date='today')
        endereco_resgate_id = random.choice(enderecos_ids)
        cor = random.choice(cores)
        raca = random.choice(racas)
        condicao_saude = fake.text(max_nb_chars=200)
        adotado = random.choice([True, False])
        
        cursor.execute("""
            INSERT INTO gato (nome, idade, data_resgate, endereco_resgate_id, cor, raca, condicao_saude, adotado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (nome, idade, data_resgate, endereco_resgate_id, cor, raca, condicao_saude, adotado))
        
        gato_id = cursor.fetchone()[0]
        gatos_ids.append(gato_id)


def popular_campanhas(cursor, quantidade=10):
    """Popula a tabela campanha"""
    print(f"Inserindo {quantidade} campanhas...")
    
    nomes_usados = []
    
    for i in range(quantidade):
        nome = f"Campanha {fake.catch_phrase()} {i+1}"
        while nome in nomes_usados:  # Evita nomes duplicados
            nome = f"Campanha {fake.catch_phrase()} {i+1}"
        
        nomes_usados.append(nome)
        
        data_inicio = fake.date_between(start_date='-1y', end_date='today')
        data_fim = fake.date_between(start_date=data_inicio, end_date='+6m')
        premio = fake.text(max_nb_chars=100)
        vencedor_cpf = random.choice(pessoas_cpfs) if random.choice([True, False]) else None
        
        cursor.execute("""
            INSERT INTO campanha (nome, data_inicio, data_fim, premio, vencedor_cpf)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (nome, data_inicio, data_fim, premio, vencedor_cpf))
        
        campanha_id = cursor.fetchone()[0]
        campanhas_ids.append(campanha_id)


def popular_eventos(cursor, quantidade=20):
    """Popula a tabela evento"""
    print(f"Inserindo {quantidade} eventos...")
    
    for _ in range(quantidade):
        nome = f"Evento {fake.catch_phrase()}"
        data_inicio = fake.date_between(start_date='-6m', end_date='+6m')
        data_fim = fake.date_between(start_date=data_inicio, end_date=data_inicio + timedelta(days=3)) if random.choice([True, False]) else None
        endereco_id = random.choice(enderecos_ids)
        
        cursor.execute("""
            INSERT INTO evento (nome, data_inicio, data_fim, endereco_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (nome, data_inicio, data_fim, endereco_id))
        
        evento_id = cursor.fetchone()[0]
        eventos_ids.append(evento_id)


def popular_lares_temporarios(cursor, quantidade=15):
    """Popula a tabela lar_temporario"""
    print(f"Inserindo {quantidade} lares temporários...")
    
    # Garante que temos endereços suficientes disponíveis
    enderecos_disponiveis = [e for e in enderecos_ids if e not in enderecos_usados_lares]
    quantidade = min(quantidade, len(enderecos_disponiveis))
    
    for i in range(quantidade):
        endereco_id = enderecos_disponiveis[i]
        enderecos_usados_lares.append(endereco_id)  # Marca como usado
        capacidade_maxima = random.randint(5, 30)
        
        # Inserir sem responsável inicialmente (será atualizado depois)
        cursor.execute("""
            INSERT INTO lar_temporario (endereco_id, capacidade_maxima, responsavel_cpf)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (endereco_id, capacidade_maxima, None))
        
        lar_id = cursor.fetchone()[0]
        lares_ids.append(lar_id)


def popular_voluntarios(cursor, quantidade=30):
    """Popula a tabela voluntario"""
    print(f"Inserindo {quantidade} voluntários...")
    
    cpfs_disponiveis = [cpf for cpf in pessoas_cpfs if cpf not in voluntarios_cpfs]
    quantidade = min(quantidade, len(cpfs_disponiveis))
    
    for i in range(quantidade):
        cpf = cpfs_disponiveis[i]
        voluntarios_cpfs.append(cpf)
        
        cursor.execute("""
            INSERT INTO voluntario (cpf)
            VALUES (%s)
        """, (cpf,))


def popular_adotantes(cursor, quantidade=40):
    """Popula a tabela adotante"""
    print(f"Inserindo {quantidade} adotantes...")
    
    cpfs_disponiveis = [cpf for cpf in pessoas_cpfs if cpf not in voluntarios_cpfs and cpf not in adotantes_cpfs]
    quantidade = min(quantidade, len(cpfs_disponiveis))
    
    for i in range(quantidade):
        cpf = cpfs_disponiveis[i]
        adotantes_cpfs.append(cpf)
        
        procurando_gato = random.choice([True, False])
        
        cursor.execute("""
            INSERT INTO adotante (cpf, procurando_gato)
            VALUES (%s, %s)
        """, (cpf, procurando_gato))


def popular_veterinarios(cursor, quantidade=8):
    """Popula a tabela veterinario"""
    print(f"Inserindo {quantidade} veterinários...")
    
    especialidades = ['Clínica Geral', 'Cirurgia', 'Dermatologia', 'Cardiologia', 'Oncologia']
    
    cpfs_disponiveis = [cpf for cpf in pessoas_cpfs 
                       if cpf not in voluntarios_cpfs 
                       and cpf not in adotantes_cpfs 
                       and cpf not in veterinarios_cpfs]
    quantidade = min(quantidade, len(cpfs_disponiveis))
    
    for i in range(quantidade):
        cpf = cpfs_disponiveis[i]
        veterinarios_cpfs.append(cpf)
        
        # Formato correto: número-estado (ex: 1234-SP)
        crmv = f"{random.randint(1000, 9999)}-SP"
        especialidade = random.choice(especialidades)
        clinica = f"Clínica {fake.company()}"
        
        cursor.execute("""
            INSERT INTO veterinario (cpf, crmv, especialidade, clinica)
            VALUES (%s, %s, %s, %s)
        """, (cpf, crmv, especialidade, clinica))


def popular_funcoes(cursor):
    """Popula a tabela funcao"""
    print("Inserindo funções dos voluntários...")
    
    funcoes = ['Resgate', 'Cuidador', 'Transporte', 'Triagem', 'Administração', 'Captação de Recursos']
    
    for voluntario_cpf in voluntarios_cpfs:
        num_funcoes = random.randint(1, 3)
        funcoes_escolhidas = random.sample(funcoes, num_funcoes)
        
        for funcao in funcoes_escolhidas:
            cursor.execute("""
                INSERT INTO funcao (voluntario_cpf, funcao)
                VALUES (%s, %s)
            """, (voluntario_cpf, funcao))


def popular_doacoes(cursor, quantidade=80):
    """Popula a tabela doacao"""
    print(f"Inserindo {quantidade} doações...")
    
    formas_pagamento = ['PIX', 'CARTAO_CREDITO', 'TRANSFERENCIA', 'DINHEIRO', 'CARTAO_DEBITO']
    
    for _ in range(quantidade):
        data = fake.date_between(start_date='-1y', end_date='today')
        valor = Decimal(str(random.uniform(10.0, 500.0))).quantize(Decimal('0.01'))
        forma_pagamento = random.choice(formas_pagamento)
        pessoa_cpf = random.choice(pessoas_cpfs)
        
        cursor.execute("""
            INSERT INTO doacao (data, valor, forma_pagamento, pessoa_cpf)
            VALUES (%s, %s, %s, %s)
        """, (data, valor, forma_pagamento, pessoa_cpf))


def popular_participantes(cursor):
    """Popula a tabela participantes"""
    print("Inserindo participantes das campanhas...")
    
    for campanha_id in campanhas_ids:
        num_participantes = random.randint(5, 20)
        participantes = random.sample(pessoas_cpfs, min(num_participantes, len(pessoas_cpfs)))
        
        for pessoa_cpf in participantes:
            cursor.execute("""
                INSERT INTO participantes (pessoa_cpf, campanha_id)
                VALUES (%s, %s)
            """, (pessoa_cpf, campanha_id))


def popular_contatos(cursor, quantidade=100):
    """Popula a tabela contato"""
    print(f"Inserindo {quantidade} contatos...")
    
    assuntos = [
        'Interesse em adoção', 'Dúvidas sobre voluntariado', 'Relato de animal abandonado',
        'Solicitação de castração', 'Doação de ração', 'Informações sobre evento'
    ]
    
    for _ in range(quantidade):
        pessoa_cpf = random.choice(pessoas_cpfs)
        data_hora = fake.date_time_between(start_date='-1y', end_date='now')
        assunto = random.choice(assuntos)
        
        cursor.execute("""
            INSERT INTO contato (pessoa_cpf, data_hora, assunto)
            VALUES (%s, %s, %s)
        """, (pessoa_cpf, data_hora, assunto))


def popular_cuida_lar(cursor):
    """Popula a tabela cuida_lar"""
    print("Inserindo cuidadores de lares temporários...")
    
    for lar_id in lares_ids:
        num_cuidadores = random.randint(1, 3)
        cuidadores = random.sample(voluntarios_cpfs, min(num_cuidadores, len(voluntarios_cpfs)))
        
        for voluntario_cpf in cuidadores:
            cursor.execute("""
                INSERT INTO cuida_lar (lar_id, voluntario_cpf)
                VALUES (%s, %s)
            """, (lar_id, voluntario_cpf))


def popular_voluntarios_evento(cursor):
    """Popula a tabela voluntarios_evento"""
    print("Inserindo voluntários em eventos...")
    
    for evento_id in eventos_ids:
        num_voluntarios = random.randint(1, 5)
        voluntarios_escolhidos = random.sample(voluntarios_cpfs, min(num_voluntarios, len(voluntarios_cpfs)))
        
        for voluntario_cpf in voluntarios_escolhidos:
            cursor.execute("""
                INSERT INTO voluntarios_evento (evento_id, voluntario_cpf)
                VALUES (%s, %s)
            """, (evento_id, voluntario_cpf))


def popular_gatos_evento(cursor):
    """Popula a tabela gatos_evento"""
    print("Inserindo gatos em eventos...")
    
    for evento_id in eventos_ids:
        num_gatos = random.randint(1, 8)
        gatos_escolhidos = random.sample(gatos_ids, min(num_gatos, len(gatos_ids)))
        
        for gato_id in gatos_escolhidos:
            cursor.execute("""
                INSERT INTO gatos_evento (evento_id, gato_id)
                VALUES (%s, %s)
            """, (evento_id, gato_id))


def popular_fotos_gato(cursor):
    """Popula a tabela fotos_gato"""
    print("Inserindo fotos dos gatos...")
    
    for gato_id in gatos_ids:
        num_fotos = random.randint(1, 4)
        
        for i in range(num_fotos):
            foto_url = f"https://example.com/gatos/gato_{gato_id}_foto_{i+1}.jpg"
            
            cursor.execute("""
                INSERT INTO fotos_gato (gato_id, foto_url)
                VALUES (%s, %s)
            """, (gato_id, foto_url))


def popular_hospedagem(cursor):
    """Popula a tabela hospedagem"""
    print("Inserindo hospedagens...")
    
    for gato_id in gatos_ids:
        if random.choice([True, False]):  # 50% dos gatos passaram por lar temporário
            lar_id = random.choice(lares_ids)
            data_entrada = fake.date_between(start_date='-1y', end_date='today')
            data_saida = fake.date_between(start_date=data_entrada, end_date='today') if random.choice([True, False]) else None
            
            cursor.execute("""
                INSERT INTO hospedagem (lar_temporario_id, gato_id, data_entrada, data_saida)
                VALUES (%s, %s, %s, %s)
            """, (lar_id, gato_id, data_entrada, data_saida))


def popular_gastos(cursor, quantidade=150):
    """Popula a tabela gasto"""
    print(f"Inserindo {quantidade} gastos...")
    
    tipos = ['ALIMENTACAO', 'VETERINARIO', 'MEDICAMENTO', 'TRANSPORTE', 'HIGIENE', 'MANUTENCAO']
    
    for _ in range(quantidade):
        data = fake.date_between(start_date='-1y', end_date='today')
        valor = Decimal(str(random.uniform(10.0, 300.0))).quantize(Decimal('0.01'))
        descricao = fake.text(max_nb_chars=100)
        tipo = random.choice(tipos)
        
        # 70% dos gastos são relacionados a gatos, 30% a lares
        if random.random() < 0.7:
            gato_id = random.choice(gatos_ids)
            lar_id = None
        else:
            gato_id = None
            lar_id = random.choice(lares_ids)
        
        cursor.execute("""
            INSERT INTO gasto (data, valor, descricao, tipo, lar_id, gato_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data, valor, descricao, tipo, lar_id, gato_id))


def popular_procedimentos(cursor, quantidade=100):
    """Popula a tabela procedimento"""
    print(f"Inserindo {quantidade} procedimentos veterinários...")
    
    tipos = ['CONSULTA', 'VACINACAO', 'CASTRACAO', 'CIRURGIA', 'EXAME', 'TRATAMENTO']
    
    for _ in range(quantidade):
        gato_id = random.choice(gatos_ids)
        veterinario_cpf = random.choice(veterinarios_cpfs)
        data_hora = fake.date_time_between(start_date='-1y', end_date='now')
        tipo = random.choice(tipos)
        custo = Decimal(str(random.uniform(50.0, 800.0))).quantize(Decimal('0.01'))
        descricao = fake.text(max_nb_chars=200)
        
        cursor.execute("""
            INSERT INTO procedimento (gato_id, veterinario_cpf, data_hora, tipo, custo, descricao)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (gato_id, veterinario_cpf, data_hora, tipo, custo, descricao))


def popular_preferencias(cursor):
    """Popula a tabela preferencia"""
    print("Inserindo preferências dos adotantes...")
    
    idades_pref = ['Filhote', 'Adulto', 'Idoso', 'Qualquer']
    cores_pref = ['Preto', 'Branco', 'Cinza', 'Laranja', 'Qualquer']
    racas_pref = ['SRD', 'Persa', 'Siamês', 'Qualquer']
    
    for adotante_cpf in adotantes_cpfs:
        if random.choice([True, False]):  # 50% dos adotantes têm preferências registradas
            idade_preferida = random.choice(idades_pref)
            cor_preferida = random.choice(cores_pref)
            raca_preferida = random.choice(racas_pref)
            
            cursor.execute("""
                INSERT INTO preferencia (adotante_cpf, idade_preferida, cor_preferida, raca_preferida)
                VALUES (%s, %s, %s, %s)
            """, (adotante_cpf, idade_preferida, cor_preferida, raca_preferida))


def popular_triagens(cursor):
    """Popula a tabela triagem"""
    print("Inserindo triagens dos adotantes...")
    
    resultados = ['APROVADO', 'REPROVADO', 'PENDENTE']
    
    for adotante_cpf in adotantes_cpfs:
        if random.choice([True, False, False]):  # 33% dos adotantes passaram por triagem
            data = fake.date_between(start_date='-6m', end_date='today')
            responsavel_cpf = random.choice(voluntarios_cpfs)
            resultado = random.choice(resultados)
            
            cursor.execute("""
                INSERT INTO triagem (adotante_cpf, data, responsavel_cpf, resultado)
                VALUES (%s, %s, %s, %s)
            """, (adotante_cpf, data, responsavel_cpf, resultado))


def popular_fotos_triagem(cursor):
    """Popula a tabela fotos_triagem"""
    print("Inserindo fotos das triagens...")
    
    # Busca triagens existentes
    cursor.execute("SELECT adotante_cpf, data FROM triagem")
    triagens = cursor.fetchall()
    
    for adotante_cpf, data_triagem in triagens:
        num_fotos = random.randint(1, 3)
        
        for i in range(num_fotos):
            foto_url = f"https://example.com/triagens/{adotante_cpf}_{data_triagem}_foto_{i+1}.jpg"
            
            cursor.execute("""
                INSERT INTO fotos_triagem (adotante_cpf, triagem_data, foto_url)
                VALUES (%s, %s, %s)
            """, (adotante_cpf, data_triagem, foto_url))


def popular_adocoes(cursor, quantidade=20):
    """Popula a tabela adocao"""
    print(f"Inserindo {quantidade} adoções...")
    
    motivos = ['Amor por animais', 'Companhia', 'Ajudar animal necessitado', 'Pedido da família']
    
    gatos_disponiveis = gatos_ids.copy()
    random.shuffle(gatos_disponiveis)
    
    for i in range(min(quantidade, len(gatos_disponiveis), len(adotantes_cpfs))):
        gato_id = gatos_disponiveis[i]
        adotante_cpf = random.choice(adotantes_cpfs)
        data = fake.date_between(start_date='-6m', end_date='today')
        motivo = random.choice(motivos)
        
        cursor.execute("""
            INSERT INTO adocao (gato_id, adotante_cpf, data, motivo)
            VALUES (%s, %s, %s, %s)
        """, (gato_id, adotante_cpf, data, motivo))


def popular_devolucoes(cursor, quantidade=3):
    """Popula a tabela devolucao"""
    print(f"Inserindo {quantidade} devoluções...")
    
    motivos = ['Problemas de saúde do animal', 'Mudança de residência', 'Alergia', 'Problemas comportamentais']
    
    # Busca algumas adoções para criar devoluções
    cursor.execute("SELECT gato_id, adotante_cpf, data FROM adocao LIMIT %s", (quantidade,))
    adocoes = cursor.fetchall()
    
    for gato_id, adotante_cpf, data_adocao in adocoes:
        data_devolucao = fake.date_between(start_date=data_adocao, end_date='today')
        motivo = random.choice(motivos)
        
        cursor.execute("""
            INSERT INTO devolucao (gato_id, adotante_cpf, data, motivo)
            VALUES (%s, %s, %s, %s)
        """, (gato_id, adotante_cpf, data_devolucao, motivo))


def atualizar_responsaveis_lares(cursor):
    """Atualiza os responsáveis dos lares temporários"""
    print("Atualizando responsáveis dos lares temporários...")
    
    for lar_id in lares_ids:
        # Busca voluntários que cuidam deste lar
        cursor.execute("SELECT voluntario_cpf FROM cuida_lar WHERE lar_id = %s LIMIT 1", (lar_id,))
        result = cursor.fetchone()
        
        if result:
            responsavel_cpf = result[0]
            cursor.execute("""
                UPDATE lar_temporario 
                SET responsavel_cpf = %s 
                WHERE id = %s
            """, (responsavel_cpf, lar_id))


def main():
    """Função principal que executa a população do banco de dados"""
    print("Iniciando população do banco de dados...")
    print("=" * 50)
    
    conn = conectar_bd()
    cursor = conn.cursor()
    
    try:
        # Limpa dados existentes
        limpar_banco(cursor)
        
        # 1. Popula tabelas base sem foreign keys
        popular_enderecos(cursor, 200)
        popular_pessoas(cursor, 100)
        popular_gatos(cursor, 50)
        popular_campanhas(cursor, 10)
        popular_eventos(cursor, 20)
        
        # 2. Popula especializações de Pessoa (dependem de Pessoa)
        popular_voluntarios(cursor, 30)
        popular_adotantes(cursor, 40)
        popular_veterinarios(cursor, 8)
        
        # 3. Popula lares temporários (agora que voluntários existem)
        popular_lares_temporarios(cursor, 15)
        
        # Popula tabelas de relacionamento e transacionais
        popular_funcoes(cursor)
        popular_doacoes(cursor, 80)
        popular_participantes(cursor)
        popular_contatos(cursor, 100)
        popular_cuida_lar(cursor)
        popular_voluntarios_evento(cursor)
        popular_gatos_evento(cursor)
        popular_fotos_gato(cursor)
        popular_hospedagem(cursor)
        popular_gastos(cursor, 150)
        popular_procedimentos(cursor, 100)
        popular_preferencias(cursor)
        popular_triagens(cursor)
        popular_fotos_triagem(cursor)
        popular_adocoes(cursor, 20)
        popular_devolucoes(cursor, 3)
        
        # Atualiza campos que dependem de outros dados
        atualizar_responsaveis_lares(cursor)
        
        # Commit das transações
        conn.commit()
        
        print("=" * 50)
        print("População do banco de dados concluída com sucesso!")
        print(f"Total de endereços inseridos: {len(enderecos_ids)}")
        print(f"Total de pessoas inseridas: {len(pessoas_cpfs)}")
        print(f"Total de voluntários: {len(voluntarios_cpfs)}")
        print(f"Total de adotantes: {len(adotantes_cpfs)}")
        print(f"Total de veterinários: {len(veterinarios_cpfs)}")
        print(f"Total de gatos: {len(gatos_ids)}")
        print(f"Total de campanhas: {len(campanhas_ids)}")
        print(f"Total de eventos: {len(eventos_ids)}")
        print(f"Total de lares temporários: {len(lares_ids)}")
        
    except Exception as e:
        print(f"Erro durante a população do banco: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()