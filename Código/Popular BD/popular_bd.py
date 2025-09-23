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
campanhas_nomes = []
eventos_ids = []
lares_ids = []


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


def popular_pessoas(cursor, quantidade=100):
    """Popula a tabela Pessoa"""
    print(f"Inserindo {quantidade} pessoas...")
    
    for _ in range(quantidade):
        cpf = gerar_cpf_valido()
        while cpf in pessoas_cpfs:  # Evita CPFs duplicados
            cpf = gerar_cpf_valido()
        
        pessoas_cpfs.append(cpf)
        
        nome = fake.name()
        telefone = fake.phone_number()[:15]
        email = fake.unique.email()
        cep = fake.postcode().replace('-', '')
        numero = str(random.randint(1, 9999))
        bairro = fake.neighborhood()
        rua = fake.street_name()
        
        cursor.execute("""
            INSERT INTO Pessoa (CPF, nome, telefone, email, CEP, numero, bairro, rua)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (cpf, nome, telefone, email, cep, numero, bairro, rua))


def popular_gatos(cursor, quantidade=50):
    """Popula a tabela Gato"""
    print(f"Inserindo {quantidade} gatos...")
    
    cores = ['Preto', 'Branco', 'Cinza', 'Laranja', 'Malhado', 'Siamês', 'Rajado']
    racas = ['SRD', 'Persa', 'Siamês', 'Maine Coon', 'British Shorthair', 'Ragdoll']
    
    for _ in range(quantidade):
        nome = fake.first_name()
        idade = random.randint(0, 15)
        data_resgate = fake.date_between(start_date='-2y', end_date='today')
        cep = fake.postcode().replace('-', '')
        numero = str(random.randint(1, 9999))
        bairro = fake.neighborhood()
        rua = fake.street_name()
        cor = random.choice(cores)
        raca = random.choice(racas)
        cond_saude = fake.text(max_nb_chars=200)
        flag_adotado = random.choice([True, False])
        
        cursor.execute("""
            INSERT INTO Gato (nome, idade, data_resgate, CEP, numero, bairro, rua, cor, raca, cond_saude, flag_adotado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID
        """, (nome, idade, data_resgate, cep, numero, bairro, rua, cor, raca, cond_saude, flag_adotado))
        
        gato_id = cursor.fetchone()[0]
        gatos_ids.append(gato_id)


def popular_campanhas(cursor, quantidade=10):
    """Popula a tabela Campanha"""
    print(f"Inserindo {quantidade} campanhas...")
    
    for i in range(quantidade):
        nome = f"Campanha {fake.catch_phrase()} {i+1}"
        while nome in campanhas_nomes:  # Evita nomes duplicados
            nome = f"Campanha {fake.catch_phrase()} {i+1}"
        
        campanhas_nomes.append(nome)
        
        data_ini = fake.date_between(start_date='-1y', end_date='today')
        data_fim = fake.date_between(start_date=data_ini, end_date='+6m')
        premio = fake.text(max_nb_chars=100)
        vencedor_cpf = random.choice(pessoas_cpfs) if random.choice([True, False]) else None
        
        cursor.execute("""
            INSERT INTO Campanha (nome, data_ini, data_fim, premio, vencedor_CPF)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, data_ini, data_fim, premio, vencedor_cpf))


def popular_eventos(cursor, quantidade=20):
    """Popula a tabela Evento"""
    print(f"Inserindo {quantidade} eventos...")
    
    for _ in range(quantidade):
        nome = f"Evento {fake.catch_phrase()}"
        data = fake.date_time_between(start_date='-6m', end_date='+6m')
        cep = fake.postcode().replace('-', '')
        numero = str(random.randint(1, 9999))
        bairro = fake.neighborhood()
        rua = fake.street_name()
        
        cursor.execute("""
            INSERT INTO Evento (nome, data, CEP, numero, bairro, rua)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING ID
        """, (nome, data, cep, numero, bairro, rua))
        
        evento_id = cursor.fetchone()[0]
        eventos_ids.append(evento_id)


def popular_lares_temporarios(cursor, quantidade=15):
    """Popula a tabela Lar_Temporario"""
    print(f"Inserindo {quantidade} lares temporários...")
    
    for _ in range(quantidade):
        nome = f"Lar {fake.company()}"
        cep = fake.postcode().replace('-', '')
        numero = str(random.randint(1, 9999))
        bairro = fake.neighborhood()
        rua = fake.street_name()
        capacidade_max = random.randint(5, 30)
        
        # Inserir sem responsável inicialmente (será atualizado depois)
        cursor.execute("""
            INSERT INTO Lar_Temporario (nome, CEP, numero, bairro, rua, capacidade_max, Voluntario_responsavel_CPF)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING ID
        """, (nome, cep, numero, bairro, rua, capacidade_max, None))
        
        lar_id = cursor.fetchone()[0]
        lares_ids.append(lar_id)


def popular_voluntarios(cursor, quantidade=30):
    """Popula a tabela Voluntario"""
    print(f"Inserindo {quantidade} voluntários...")
    
    cpfs_disponiveis = [cpf for cpf in pessoas_cpfs if cpf not in voluntarios_cpfs]
    quantidade = min(quantidade, len(cpfs_disponiveis))
    
    for i in range(quantidade):
        cpf = cpfs_disponiveis[i]
        voluntarios_cpfs.append(cpf)
        
        cursor.execute("""
            INSERT INTO Voluntario (CPF)
            VALUES (%s)
        """, (cpf,))


def popular_adotantes(cursor, quantidade=40):
    """Popula a tabela Adotante"""
    print(f"Inserindo {quantidade} adotantes...")
    
    cpfs_disponiveis = [cpf for cpf in pessoas_cpfs if cpf not in voluntarios_cpfs and cpf not in adotantes_cpfs]
    quantidade = min(quantidade, len(cpfs_disponiveis))
    
    for i in range(quantidade):
        cpf = cpfs_disponiveis[i]
        adotantes_cpfs.append(cpf)
        
        flag_procurando_gato = random.choice([True, False])
        
        cursor.execute("""
            INSERT INTO Adotante (CPF, flag_procurando_gato)
            VALUES (%s, %s)
        """, (cpf, flag_procurando_gato))


def popular_veterinarios(cursor, quantidade=8):
    """Popula a tabela Veterinario"""
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
        
        crmv = f"CRMV{random.randint(1000, 9999)}"
        especialidade = random.choice(especialidades)
        clinica = f"Clínica {fake.company()}"
        
        cursor.execute("""
            INSERT INTO Veterinario (CPF, CRMV, especialidade, clinica)
            VALUES (%s, %s, %s, %s)
        """, (cpf, crmv, especialidade, clinica))


def popular_funcoes(cursor):
    """Popula a tabela Funcao"""
    print("Inserindo funções dos voluntários...")
    
    funcoes = ['Resgate', 'Cuidador', 'Transporte', 'Triagem', 'Administração', 'Captação de Recursos']
    
    for voluntario_cpf in voluntarios_cpfs:
        num_funcoes = random.randint(1, 3)
        funcoes_escolhidas = random.sample(funcoes, num_funcoes)
        
        for funcao in funcoes_escolhidas:
            cursor.execute("""
                INSERT INTO Funcao (Voluntario_CPF, funcao)
                VALUES (%s, %s)
            """, (voluntario_cpf, funcao))


def popular_doacoes(cursor, quantidade=80):
    """Popula a tabela Doacao"""
    print(f"Inserindo {quantidade} doações...")
    
    formas_pagamento = ['PIX', 'Cartão de Crédito', 'Transferência', 'Dinheiro', 'Boleto']
    
    for _ in range(quantidade):
        data = fake.date_between(start_date='-1y', end_date='today')
        valor = Decimal(str(random.uniform(10.0, 500.0))).quantize(Decimal('0.01'))
        forma_pagamento = random.choice(formas_pagamento)
        pessoa_cpf = random.choice(pessoas_cpfs)
        
        cursor.execute("""
            INSERT INTO Doacao (data, valor, forma_de_pagamento, Pessoa_CPF)
            VALUES (%s, %s, %s, %s)
        """, (data, valor, forma_pagamento, pessoa_cpf))


def popular_participantes(cursor):
    """Popula a tabela Participantes"""
    print("Inserindo participantes das campanhas...")
    
    for campanha_nome in campanhas_nomes:
        num_participantes = random.randint(5, 20)
        participantes = random.sample(pessoas_cpfs, min(num_participantes, len(pessoas_cpfs)))
        
        for pessoa_cpf in participantes:
            cursor.execute("""
                INSERT INTO Participantes (Pessoa_CPF, Campanha_nome)
                VALUES (%s, %s)
            """, (pessoa_cpf, campanha_nome))


def popular_contatos(cursor, quantidade=100):
    """Popula a tabela Contato"""
    print(f"Inserindo {quantidade} contatos...")
    
    assuntos = [
        'Interesse em adoção', 'Dúvidas sobre voluntariado', 'Relato de animal abandonado',
        'Solicitação de castração', 'Doação de ração', 'Informações sobre evento'
    ]
    
    for _ in range(quantidade):
        pessoa_cpf = random.choice(pessoas_cpfs)
        data = fake.date_time_between(start_date='-1y', end_date='now')
        assunto = random.choice(assuntos)
        
        cursor.execute("""
            INSERT INTO Contato (Pessoa_CPF, data, assunto)
            VALUES (%s, %s, %s)
        """, (pessoa_cpf, data, assunto))


def popular_cuida_lar(cursor):
    """Popula a tabela Cuida_Lar"""
    print("Inserindo cuidadores de lares temporários...")
    
    for lar_id in lares_ids:
        num_cuidadores = random.randint(1, 3)
        cuidadores = random.sample(voluntarios_cpfs, min(num_cuidadores, len(voluntarios_cpfs)))
        
        for voluntario_cpf in cuidadores:
            cursor.execute("""
                INSERT INTO Cuida_Lar (Lar_ID, Voluntario_CPF)
                VALUES (%s, %s)
            """, (lar_id, voluntario_cpf))


def popular_participa_evento(cursor):
    """Popula a tabela Participa_Evento"""
    print("Inserindo participações em eventos...")
    
    for evento_id in eventos_ids:
        num_participacoes = random.randint(1, 5)
        
        for _ in range(num_participacoes):
            voluntario_cpf = random.choice(voluntarios_cpfs)
            gato_id = random.choice(gatos_ids)
            
            # Verifica se já existe essa combinação
            cursor.execute("""
                SELECT 1 FROM Participa_Evento 
                WHERE Voluntario_CPF = %s AND Gato_ID = %s AND Evento_ID = %s
            """, (voluntario_cpf, gato_id, evento_id))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Participa_Evento (Voluntario_CPF, Gato_ID, Evento_ID)
                    VALUES (%s, %s, %s)
                """, (voluntario_cpf, gato_id, evento_id))


def popular_fotos_gato(cursor):
    """Popula a tabela Fotos_Gato"""
    print("Inserindo fotos dos gatos...")
    
    for gato_id in gatos_ids:
        num_fotos = random.randint(1, 4)
        
        for i in range(num_fotos):
            foto_url = f"https://example.com/gatos/gato_{gato_id}_foto_{i+1}.jpg"
            
            cursor.execute("""
                INSERT INTO Fotos_Gato (Gato_ID, foto_url)
                VALUES (%s, %s)
            """, (gato_id, foto_url))


def popular_hospedagem(cursor):
    """Popula a tabela Hospedagem"""
    print("Inserindo hospedagens...")
    
    for gato_id in gatos_ids:
        if random.choice([True, False]):  # 50% dos gatos passaram por lar temporário
            lar_id = random.choice(lares_ids)
            data_entrada = fake.date_between(start_date='-1y', end_date='today')
            data_saida = fake.date_between(start_date=data_entrada, end_date='today') if random.choice([True, False]) else None
            
            cursor.execute("""
                INSERT INTO Hospedagem (Lar_Temporario_ID, Gato_ID, data_entrada, data_saida)
                VALUES (%s, %s, %s, %s)
            """, (lar_id, gato_id, data_entrada, data_saida))


def popular_gastos(cursor, quantidade=150):
    """Popula a tabela Gasto"""
    print(f"Inserindo {quantidade} gastos...")
    
    tipos = ['Veterinário', 'Ração', 'Medicamento', 'Transporte', 'Material de Limpeza', 'Brinquedos']
    
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
            INSERT INTO Gasto (data, valor, descricao, tipo, Lar_ID, Gato_ID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data, valor, descricao, tipo, lar_id, gato_id))


def popular_procedimentos(cursor, quantidade=100):
    """Popula a tabela Procedimento"""
    print(f"Inserindo {quantidade} procedimentos veterinários...")
    
    tipos = ['Consulta', 'Vacinação', 'Castração', 'Cirurgia', 'Exame', 'Tratamento']
    
    for _ in range(quantidade):
        gato_id = random.choice(gatos_ids)
        veterinario_cpf = random.choice(veterinarios_cpfs)
        data_hora = fake.date_time_between(start_date='-1y', end_date='now')
        tipo = random.choice(tipos)
        custo = Decimal(str(random.uniform(50.0, 800.0))).quantize(Decimal('0.01'))
        
        cursor.execute("""
            INSERT INTO Procedimento (Gato_ID, Veterinario_CPF, data_hora, tipo, custo)
            VALUES (%s, %s, %s, %s, %s)
        """, (gato_id, veterinario_cpf, data_hora, tipo, custo))


def popular_preferencias(cursor):
    """Popula a tabela Preferencia"""
    print("Inserindo preferências dos adotantes...")
    
    idades_pref = ['Filhote', 'Adulto', 'Idoso', 'Qualquer']
    cores_pref = ['Preto', 'Branco', 'Cinza', 'Laranja', 'Qualquer']
    racas_pref = ['SRD', 'Persa', 'Siamês', 'Qualquer']
    
    for adotante_cpf in adotantes_cpfs:
        if random.choice([True, False]):  # 50% dos adotantes têm preferências registradas
            data = fake.date_between(start_date='-6m', end_date='today')
            idade_pref = random.choice(idades_pref)
            cor_pref = random.choice(cores_pref)
            raca_pref = random.choice(racas_pref)
            
            cursor.execute("""
                INSERT INTO Preferencia (Adotante_CPF, data, idade_pref, cor_pref, raca_pref)
                VALUES (%s, %s, %s, %s, %s)
            """, (adotante_cpf, data, idade_pref, cor_pref, raca_pref))


def popular_triagens(cursor):
    """Popula a tabela Triagem"""
    print("Inserindo triagens dos adotantes...")
    
    resultados = ['Aprovado', 'Reprovado', 'Pendente']
    
    for adotante_cpf in adotantes_cpfs:
        if random.choice([True, False, False]):  # 33% dos adotantes passaram por triagem
            data = fake.date_between(start_date='-6m', end_date='today')
            responsavel_cpf = random.choice(voluntarios_cpfs)
            resultado = random.choice(resultados)
            
            cursor.execute("""
                INSERT INTO Triagem (Adotante_CPF, data, responsavel_CPF, resultado)
                VALUES (%s, %s, %s, %s)
            """, (adotante_cpf, data, responsavel_cpf, resultado))


def popular_fotos_triagem(cursor):
    """Popula a tabela Fotos_Triagem"""
    print("Inserindo fotos das triagens...")
    
    # Busca triagens existentes
    cursor.execute("SELECT Adotante_CPF, data FROM Triagem")
    triagens = cursor.fetchall()
    
    for adotante_cpf, data_triagem in triagens:
        num_fotos = random.randint(1, 3)
        
        for i in range(num_fotos):
            foto_url = f"https://example.com/triagens/{adotante_cpf}_{data_triagem}_foto_{i+1}.jpg"
            
            cursor.execute("""
                INSERT INTO Fotos_Triagem (Adotante_CPF, Triagem_data, foto_url)
                VALUES (%s, %s, %s)
            """, (adotante_cpf, data_triagem, foto_url))


def popular_adocoes(cursor, quantidade=20):
    """Popula a tabela Adocao"""
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
            INSERT INTO Adocao (Gato_ID, Adotante_CPF, data, motivo)
            VALUES (%s, %s, %s, %s)
        """, (gato_id, adotante_cpf, data, motivo))


def popular_devolucoes(cursor, quantidade=3):
    """Popula a tabela Devolucao"""
    print(f"Inserindo {quantidade} devoluções...")
    
    motivos = ['Problemas de saúde do animal', 'Mudança de residência', 'Alergia', 'Problemas comportamentais']
    
    # Busca algumas adoções para criar devoluções
    cursor.execute("SELECT Gato_ID, Adotante_CPF, data FROM Adocao LIMIT %s", (quantidade,))
    adocoes = cursor.fetchall()
    
    for gato_id, adotante_cpf, data_adocao in adocoes:
        data_devolucao = fake.date_between(start_date=data_adocao, end_date='today')
        motivo = random.choice(motivos)
        
        cursor.execute("""
            INSERT INTO Devolucao (Gato_ID, Adotante_CPF, data, motivo)
            VALUES (%s, %s, %s, %s)
        """, (gato_id, adotante_cpf, data_devolucao, motivo))


def atualizar_responsaveis_lares(cursor):
    """Atualiza os responsáveis dos lares temporários"""
    print("Atualizando responsáveis dos lares temporários...")
    
    for lar_id in lares_ids:
        # Busca voluntários que cuidam deste lar
        cursor.execute("SELECT Voluntario_CPF FROM Cuida_Lar WHERE Lar_ID = %s LIMIT 1", (lar_id,))
        result = cursor.fetchone()
        
        if result:
            responsavel_cpf = result[0]
            cursor.execute("""
                UPDATE Lar_Temporario 
                SET Voluntario_responsavel_CPF = %s 
                WHERE ID = %s
            """, (responsavel_cpf, lar_id))


def main():
    """Função principal que executa a população do banco de dados"""
    print("Iniciando população do banco de dados...")
    print("=" * 50)
    
    conn = conectar_bd()
    cursor = conn.cursor()
    
    try:
        # Desabilita temporariamente as foreign key constraints (PostgreSQL)
        # Não é necessário desabilitar se seguirmos a ordem correta de inserção
        
        # 1. Popula tabelas base sem foreign keys
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
        popular_participa_evento(cursor)
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
        
        # Foreign keys permanecem habilitadas (ordem correta de inserção)
        
        # Commit das transações
        conn.commit()
        
        print("=" * 50)
        print("População do banco de dados concluída com sucesso!")
        print(f"Total de pessoas inseridas: {len(pessoas_cpfs)}")
        print(f"Total de voluntários: {len(voluntarios_cpfs)}")
        print(f"Total de adotantes: {len(adotantes_cpfs)}")
        print(f"Total de veterinários: {len(veterinarios_cpfs)}")
        print(f"Total de gatos: {len(gatos_ids)}")
        print(f"Total de campanhas: {len(campanhas_nomes)}")
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