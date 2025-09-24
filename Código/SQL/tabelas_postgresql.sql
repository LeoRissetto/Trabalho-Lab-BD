-- Versão PostgreSQL das tabelas do sistema de adoção de gatos

-- Tabela centralizada para endereços (normalização)
CREATE TABLE endereco (
    id SERIAL PRIMARY KEY,
    cep VARCHAR(8) NOT NULL,
    rua VARCHAR(255),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    complemento VARCHAR(100),
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    CONSTRAINT chk_endereco_cep CHECK (LENGTH(cep) = 8 AND cep ~ '^[0-9]+$'),
    CONSTRAINT chk_endereco_estado CHECK (LENGTH(estado) = 2 AND estado ~ '^[A-Z]{2}$')
);

CREATE UNIQUE INDEX uq_endereco_unico
ON endereco (cep, rua, numero, bairro, cidade, estado, COALESCE(complemento, ''));

-- Tabela para armazenar dados de todas as pessoas envolvidas (voluntários, adotantes, etc.).
CREATE TABLE pessoa (
    cpf VARCHAR(11) NOT NULL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(15),
    email VARCHAR(255) UNIQUE,
    endereco_id INT,
    FOREIGN KEY (endereco_id) REFERENCES endereco(id) ON DELETE SET NULL,
    CONSTRAINT chk_cpf_valido CHECK (LENGTH(cpf) = 11 AND cpf ~ '^[0-9]+$'),
    CONSTRAINT chk_email_valido CHECK (email IS NULL OR email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_telefone_valido CHECK (telefone IS NULL OR LENGTH(telefone) >= 10)
);

-- Tabela para armazenar informações sobre os gatos.
CREATE TABLE gato (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    idade INT,
    data_resgate DATE,
    endereco_resgate_id INT,
    cor VARCHAR(50),
    raca VARCHAR(50),
    condicao_saude TEXT,
    adotado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (endereco_resgate_id) REFERENCES endereco(id) ON DELETE SET NULL,
    CONSTRAINT chk_gato_idade CHECK (idade IS NULL OR (idade >= 0 AND idade <= 30)),
    CONSTRAINT chk_gato_data_resgate CHECK (data_resgate <= CURRENT_DATE)
);

-- Tabela de especialização para Voluntários.
CREATE TABLE voluntario (
    cpf VARCHAR(11) NOT NULL PRIMARY KEY,
    FOREIGN KEY (cpf) REFERENCES pessoa(cpf) ON DELETE CASCADE
);

-- Tabela de especialização para Adotantes.
CREATE TABLE adotante (
    cpf VARCHAR(11) NOT NULL PRIMARY KEY,
    procurando_gato BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (cpf) REFERENCES pessoa(cpf) ON DELETE CASCADE
);

-- Tabela de especialização para Veterinários.
CREATE TABLE veterinario (
    cpf VARCHAR(11) NOT NULL PRIMARY KEY,
    crmv VARCHAR(20) NOT NULL UNIQUE,
    especialidade VARCHAR(100),
    clinica VARCHAR(255),
    FOREIGN KEY (cpf) REFERENCES pessoa(cpf) ON DELETE CASCADE,
    CONSTRAINT chk_crmv_formato CHECK (crmv ~ '^[0-9]+-[A-Z]{2}$')
);

-- Tabela para as funções de um voluntário.
CREATE TABLE funcao (
    voluntario_cpf VARCHAR(11) NOT NULL,
    funcao VARCHAR(100) NOT NULL,
    PRIMARY KEY (voluntario_cpf, funcao),
    FOREIGN KEY (voluntario_cpf) REFERENCES voluntario(cpf) ON DELETE CASCADE
);

-- Tabela para registrar doações.
CREATE TABLE doacao (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    forma_pagamento VARCHAR(50),
    pessoa_cpf VARCHAR(11),
    FOREIGN KEY (pessoa_cpf) REFERENCES pessoa(cpf) ON DELETE RESTRICT,
    CONSTRAINT chk_valor_positivo CHECK (valor > 0),
    CONSTRAINT chk_data_doacao CHECK (data <= CURRENT_DATE),
    CONSTRAINT chk_forma_pagamento CHECK (forma_pagamento IS NULL OR forma_pagamento IN ('DINHEIRO', 'PIX', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'TRANSFERENCIA', 'OUTROS'))
);

-- Tabela para as campanhas.
CREATE TABLE campanha (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    data_inicio DATE,
    data_fim DATE,
    premio VARCHAR(255),
    vencedor_cpf VARCHAR(11),
    FOREIGN KEY (vencedor_cpf) REFERENCES pessoa(cpf) ON DELETE SET NULL,
    CONSTRAINT uq_campanha_nome_data UNIQUE (nome, data_inicio),
    CONSTRAINT chk_datas_campanha CHECK (
        (data_inicio IS NOT NULL AND data_fim IS NULL) OR
        (data_inicio IS NOT NULL AND data_fim IS NOT NULL AND data_fim >= data_inicio) OR
        (data_inicio IS NULL AND data_fim IS NULL)
    )
);

-- Tabela de relacionamento N:M entre Pessoa e Campanha.
CREATE TABLE participantes (
    pessoa_cpf VARCHAR(11) NOT NULL,
    campanha_id INT NOT NULL,
    PRIMARY KEY (pessoa_cpf, campanha_id),
    FOREIGN KEY (pessoa_cpf) REFERENCES pessoa(cpf) ON DELETE CASCADE,
    FOREIGN KEY (campanha_id) REFERENCES campanha(id) ON DELETE CASCADE
);

-- Tabela para registrar contatos feitos.
CREATE TABLE contato (
    pessoa_cpf VARCHAR(11) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    assunto TEXT,
    PRIMARY KEY (pessoa_cpf, data_hora),
    FOREIGN KEY (pessoa_cpf) REFERENCES pessoa(cpf) ON DELETE CASCADE
);

-- Tabela para os lares temporários.
CREATE TABLE lar_temporario (
    id SERIAL PRIMARY KEY,
    endereco_id INT NOT NULL UNIQUE,
    capacidade_maxima INT,
    responsavel_cpf VARCHAR(11),
    FOREIGN KEY (endereco_id) REFERENCES endereco(id) ON DELETE CASCADE,
    FOREIGN KEY (responsavel_cpf) REFERENCES voluntario(cpf) ON DELETE SET NULL,
    CONSTRAINT chk_capacidade_positiva CHECK (capacidade_maxima IS NULL OR capacidade_maxima > 0)
);

-- Tabela de relacionamento N:M entre Voluntario e Lar_Temporario.
CREATE TABLE cuida_lar (
    lar_id INT NOT NULL,
    voluntario_cpf VARCHAR(11) NOT NULL,
    PRIMARY KEY (lar_id, voluntario_cpf),
    FOREIGN KEY (lar_id) REFERENCES lar_temporario(id) ON DELETE CASCADE,
    FOREIGN KEY (voluntario_cpf) REFERENCES voluntario(cpf) ON DELETE CASCADE
);

-- Tabela de eventos.
CREATE TABLE evento (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    data_inicio DATE,
    data_fim DATE,
    endereco_id INT,
    FOREIGN KEY (endereco_id) REFERENCES endereco(id) ON DELETE SET NULL,
    CONSTRAINT uq_evento_nome_data UNIQUE (nome, data_inicio),
    CONSTRAINT chk_datas_evento CHECK (
        (data_inicio IS NOT NULL AND data_fim IS NULL) OR
        (data_inicio IS NOT NULL AND data_fim IS NOT NULL AND data_fim >= data_inicio) OR
        (data_inicio IS NULL AND data_fim IS NULL)
    )
);

-- Voluntários que organizam/participam do evento
CREATE TABLE voluntarios_evento (
    evento_id INT NOT NULL,
    voluntario_cpf VARCHAR(11) NOT NULL,
    PRIMARY KEY (evento_id, voluntario_cpf),
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    FOREIGN KEY (voluntario_cpf) REFERENCES voluntario(cpf) ON DELETE CASCADE
);

-- Gatos que participam do evento  
CREATE TABLE gatos_evento (
    evento_id INT NOT NULL,
    gato_id INT NOT NULL,
    PRIMARY KEY (evento_id, gato_id),
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE CASCADE
);

-- Tabela para armazenar as fotos dos gatos.
CREATE TABLE fotos_gato (
    gato_id INT NOT NULL,
    foto_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (gato_id, foto_url),
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE CASCADE
);

-- Tabela de relacionamento N:M entre Gato e Lar_Temporario.
CREATE TABLE hospedagem (
    lar_temporario_id INT NOT NULL,
    gato_id INT NOT NULL,
    data_entrada DATE NOT NULL,
    data_saida DATE,
    PRIMARY KEY (lar_temporario_id, gato_id, data_entrada),
    FOREIGN KEY (lar_temporario_id) REFERENCES lar_temporario(id) ON DELETE CASCADE,
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE CASCADE,
    CONSTRAINT chk_hospedagem_datas CHECK (
        (data_saida IS NULL OR data_saida >= data_entrada)
    )
);

-- Tabela para registrar gastos relacionados a um gato ou a um lar.
CREATE TABLE gasto (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    lar_id INT,
    gato_id INT,
    FOREIGN KEY (lar_id) REFERENCES lar_temporario(id) ON DELETE SET NULL,
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE SET NULL,
    CONSTRAINT chk_gasto_valor CHECK (valor >= 0),
    CONSTRAINT chk_gasto_data CHECK (data <= CURRENT_DATE),
    CONSTRAINT chk_gasto_referencia CHECK ((lar_id IS NOT NULL AND gato_id IS NULL) OR (lar_id IS NULL AND gato_id IS NOT NULL)),
    CONSTRAINT chk_gasto_tipo CHECK (tipo IN ('ALIMENTACAO', 'VETERINARIO', 'MEDICAMENTO', 'HIGIENE', 'TRANSPORTE', 'MANUTENCAO', 'OUTROS'))
);

-- Tabela para os procedimentos veterinários realizados em um gato.
CREATE TABLE procedimento (
    gato_id INT NOT NULL,
    veterinario_cpf VARCHAR(11) NOT NULL,
    data_hora TIMESTAMP NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    custo DECIMAL(10, 2),
    descricao TEXT,
    PRIMARY KEY (gato_id, veterinario_cpf, data_hora),
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE CASCADE,
    FOREIGN KEY (veterinario_cpf) REFERENCES veterinario(cpf) ON DELETE RESTRICT,
    CONSTRAINT chk_procedimento_custo CHECK (custo IS NULL OR custo >= 0),
    CONSTRAINT chk_procedimento_data CHECK (data_hora <= CURRENT_TIMESTAMP),
    CONSTRAINT chk_procedimento_tipo CHECK (tipo IN ('CONSULTA', 'VACINACAO', 'CASTRACAO', 'CIRURGIA', 'EXAME', 'EMERGENCIA', 'TRATAMENTO', 'OUTROS'))
);

-- Tabela para registrar as preferências de um potencial adotante.
CREATE TABLE preferencia (
    adotante_cpf VARCHAR(11) NOT NULL PRIMARY KEY,
    idade_preferida VARCHAR(50),
    cor_preferida VARCHAR(50),
    raca_preferida VARCHAR(50),
    FOREIGN KEY (adotante_cpf) REFERENCES adotante(cpf) ON DELETE CASCADE
);

-- Tabela de triagem de um potencial adotante.
CREATE TABLE triagem (
    adotante_cpf VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    responsavel_cpf VARCHAR(11) NOT NULL,
    resultado VARCHAR(50),
    PRIMARY KEY (adotante_cpf, data),
    FOREIGN KEY (adotante_cpf) REFERENCES adotante(cpf) ON DELETE CASCADE,
    FOREIGN KEY (responsavel_cpf) REFERENCES voluntario(cpf) ON DELETE RESTRICT,
    CONSTRAINT chk_triagem_resultado CHECK (resultado IS NULL OR resultado IN ('APROVADO', 'REPROVADO', 'PENDENTE')),
    CONSTRAINT chk_triagem_data CHECK (data <= CURRENT_DATE)
);

-- Tabela para armazenar fotos da triagem (ex: fotos da casa).
CREATE TABLE fotos_triagem (
    adotante_cpf VARCHAR(11) NOT NULL,
    triagem_data DATE NOT NULL,
    foto_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (adotante_cpf, triagem_data, foto_url),
    FOREIGN KEY (adotante_cpf, triagem_data) REFERENCES triagem(adotante_cpf, data) ON DELETE CASCADE
);

-- Tabela para formalizar a adoção.
CREATE TABLE adocao (
    gato_id INT NOT NULL,
    adotante_cpf VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    motivo TEXT,
    PRIMARY KEY (gato_id, adotante_cpf, data),
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE RESTRICT,
    FOREIGN KEY (adotante_cpf) REFERENCES adotante(cpf) ON DELETE RESTRICT,
    CONSTRAINT chk_adocao_data CHECK (data <= CURRENT_DATE)
);

-- Tabela para registrar devoluções.
CREATE TABLE devolucao (
    gato_id INT NOT NULL,
    adotante_cpf VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    motivo TEXT,
    PRIMARY KEY (gato_id, adotante_cpf, data),
    FOREIGN KEY (gato_id) REFERENCES gato(id) ON DELETE RESTRICT,
    FOREIGN KEY (adotante_cpf) REFERENCES adotante(cpf) ON DELETE RESTRICT,
    CONSTRAINT chk_devolucao_data CHECK (data <= CURRENT_DATE)
);