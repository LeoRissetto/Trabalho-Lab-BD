-- Versão PostgreSQL das tabelas do sistema de adoção de gatos

-- Tabela para armazenar dados de todas as pessoas envolvidas (voluntários, adotantes, etc.).
CREATE TABLE Pessoa (
    CPF VARCHAR(11) NOT NULL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(15),
    email VARCHAR(255) UNIQUE,
    CEP VARCHAR(8),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    rua VARCHAR(255)
);

-- Tabela para armazenar informações sobre os gatos.
CREATE TABLE Gato (
    ID SERIAL PRIMARY KEY,  -- PostgreSQL usa SERIAL ao invés de AUTO_INCREMENT
    nome VARCHAR(100),
    idade INT,
    data_resgate DATE,
    CEP VARCHAR(8),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    rua VARCHAR(255),
    cor VARCHAR(50),
    raca VARCHAR(50),
    cond_saude TEXT,
    flag_adotado BOOLEAN DEFAULT FALSE
);

-- Tabela de especialização para Voluntários.
CREATE TABLE Voluntario (
    CPF VARCHAR(11) NOT NULL PRIMARY KEY,
    FOREIGN KEY (CPF) REFERENCES Pessoa(CPF)
);

-- Tabela de especialização para Adotantes.
CREATE TABLE Adotante (
    CPF VARCHAR(11) NOT NULL PRIMARY KEY,
    flag_procurando_gato BOOLEAN,
    FOREIGN KEY (CPF) REFERENCES Pessoa(CPF)
);

-- Tabela de especialização para Veterinários.
CREATE TABLE Veterinario (
    CPF VARCHAR(11) NOT NULL PRIMARY KEY,
    CRMV VARCHAR(20) NOT NULL UNIQUE,
    especialidade VARCHAR(100),
    clinica VARCHAR(255),
    FOREIGN KEY (CPF) REFERENCES Pessoa(CPF)
);

-- Tabela para as funções de um voluntário.
CREATE TABLE Funcao (
    Voluntario_CPF VARCHAR(11) NOT NULL,
    funcao VARCHAR(100) NOT NULL,
    PRIMARY KEY (Voluntario_CPF, funcao),
    FOREIGN KEY (Voluntario_CPF) REFERENCES Voluntario(CPF)
);

-- Tabela para registrar doações.
CREATE TABLE Doacao (
    ID SERIAL PRIMARY KEY,  -- PostgreSQL usa SERIAL
    data DATE NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    forma_de_pagamento VARCHAR(50),
    Pessoa_CPF VARCHAR(11) NOT NULL,
    FOREIGN KEY (Pessoa_CPF) REFERENCES Pessoa(CPF)
);

-- Tabela para as campanhas.
CREATE TABLE Campanha (
    nome VARCHAR(255) NOT NULL PRIMARY KEY,
    data_ini DATE,
    data_fim DATE,
    premio VARCHAR(255),
    vencedor_CPF VARCHAR(11),
    FOREIGN KEY (vencedor_CPF) REFERENCES Pessoa(CPF)
);

-- Tabela de relacionamento N:M entre Pessoa e Campanha.
CREATE TABLE Participantes (
    Pessoa_CPF VARCHAR(11) NOT NULL,
    Campanha_nome VARCHAR(255) NOT NULL,
    PRIMARY KEY (Pessoa_CPF, Campanha_nome),
    FOREIGN KEY (Pessoa_CPF) REFERENCES Pessoa(CPF),
    FOREIGN KEY (Campanha_nome) REFERENCES Campanha(nome)
);

-- Tabela para registrar contatos feitos.
CREATE TABLE Contato (
    Pessoa_CPF VARCHAR(11) NOT NULL,
    data TIMESTAMP NOT NULL,  -- PostgreSQL usa TIMESTAMP ao invés de DATETIME
    assunto TEXT,
    PRIMARY KEY (Pessoa_CPF, data),
    FOREIGN KEY (Pessoa_CPF) REFERENCES Pessoa(CPF)
);

-- Tabela para os lares temporários.
CREATE TABLE Lar_Temporario (
    ID SERIAL PRIMARY KEY,  -- PostgreSQL usa SERIAL
    nome VARCHAR(255),
    CEP VARCHAR(8),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    rua VARCHAR(255),
    capacidade_max INT,
    Voluntario_responsavel_CPF VARCHAR(11),
    FOREIGN KEY (Voluntario_responsavel_CPF) REFERENCES Voluntario(CPF)
);

-- Tabela de relacionamento N:M entre Voluntario e Lar_Temporario.
CREATE TABLE Cuida_Lar (
    Lar_ID INT NOT NULL,
    Voluntario_CPF VARCHAR(11) NOT NULL,
    PRIMARY KEY (Lar_ID, Voluntario_CPF),
    FOREIGN KEY (Lar_ID) REFERENCES Lar_Temporario(ID),
    FOREIGN KEY (Voluntario_CPF) REFERENCES Voluntario(CPF)
);

-- Tabela de eventos.
CREATE TABLE Evento (
    ID SERIAL PRIMARY KEY,  -- PostgreSQL usa SERIAL
    nome VARCHAR(255) NOT NULL,
    data TIMESTAMP NOT NULL,  -- PostgreSQL usa TIMESTAMP
    CEP VARCHAR(8),
    numero VARCHAR(10),
    bairro VARCHAR(100),
    rua VARCHAR(255)
);

-- Tabela de relacionamento N:M:N para participação em eventos.
CREATE TABLE Participa_Evento (
    Voluntario_CPF VARCHAR(11) NOT NULL,
    Gato_ID INT NOT NULL,
    Evento_ID INT NOT NULL,
    PRIMARY KEY (Voluntario_CPF, Gato_ID, Evento_ID),
    FOREIGN KEY (Voluntario_CPF) REFERENCES Voluntario(CPF),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID),
    FOREIGN KEY (Evento_ID) REFERENCES Evento(ID)
);

-- Tabela para armazenar as fotos dos gatos.
CREATE TABLE Fotos_Gato (
    Gato_ID INT NOT NULL,
    foto_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (Gato_ID, foto_url),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID)
);

-- Tabela de relacionamento N:M entre Gato e Lar_Temporario.
CREATE TABLE Hospedagem (
    Lar_Temporario_ID INT NOT NULL,
    Gato_ID INT NOT NULL,
    data_entrada DATE,
    data_saida DATE,
    PRIMARY KEY (Lar_Temporario_ID, Gato_ID),
    FOREIGN KEY (Lar_Temporario_ID) REFERENCES Lar_Temporario(ID),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID)
);

-- Tabela para registrar gastos relacionados a um gato ou a um lar.
CREATE TABLE Gasto (
    ID SERIAL PRIMARY KEY,  -- PostgreSQL usa SERIAL
    data DATE NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(100),
    Lar_ID INT,
    Gato_ID INT,
    FOREIGN KEY (Lar_ID) REFERENCES Lar_Temporario(ID),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID)
);

-- Tabela para os procedimentos veterinários realizados em um gato.
CREATE TABLE Procedimento (
    Gato_ID INT NOT NULL,
    Veterinario_CPF VARCHAR(11) NOT NULL,
    data_hora TIMESTAMP NOT NULL,  -- PostgreSQL usa TIMESTAMP
    tipo VARCHAR(255),
    custo DECIMAL(10, 2),
    PRIMARY KEY (Gato_ID, Veterinario_CPF, data_hora),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID),
    FOREIGN KEY (Veterinario_CPF) REFERENCES Veterinario(CPF)
);

-- Tabela para registrar as preferências de um potencial adotante.
CREATE TABLE Preferencia (
    Adotante_CPF VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    idade_pref VARCHAR(50),
    cor_pref VARCHAR(50),
    raca_pref VARCHAR(50),
    PRIMARY KEY (Adotante_CPF, data),
    FOREIGN KEY (Adotante_CPF) REFERENCES Adotante(CPF)
);

-- Tabela de triagem de um potencial adotante.
CREATE TABLE Triagem (
    Adotante_CPF VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    responsavel_CPF VARCHAR(11) NOT NULL,
    resultado VARCHAR(50), -- Ex: Aprovado, Reprovado
    PRIMARY KEY (Adotante_CPF, data),
    FOREIGN KEY (Adotante_CPF) REFERENCES Adotante(CPF),
    FOREIGN KEY (responsavel_CPF) REFERENCES Voluntario(CPF)
);

-- Tabela para armazenar fotos da triagem (ex: fotos da casa).
CREATE TABLE Fotos_Triagem (
    Adotante_CPF VARCHAR(11) NOT NULL,
    Triagem_data DATE NOT NULL,
    foto_url VARCHAR(255) NOT NULL,
    PRIMARY KEY (Adotante_CPF, Triagem_data, foto_url),
    FOREIGN KEY (Adotante_CPF, Triagem_data) REFERENCES Triagem(Adotante_CPF, data)
);

-- Tabela para formalizar a adoção.
CREATE TABLE Adocao (
    Gato_ID INT NOT NULL,
    Adotante_CPF VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    motivo TEXT,
    PRIMARY KEY (Gato_ID, Adotante_CPF, data),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID),
    FOREIGN KEY (Adotante_CPF) REFERENCES Adotante(CPF)
);

-- Tabela para registrar devoluções.
CREATE TABLE Devolucao (
    Gato_ID INT NOT NULL,
    Adotante_CPF VARCHAR(11) NOT NULL,
    data DATE NOT NULL,
    motivo TEXT,
    PRIMARY KEY (Gato_ID, Adotante_CPF, data),
    FOREIGN KEY (Gato_ID) REFERENCES Gato(ID),
    FOREIGN KEY (Adotante_CPF) REFERENCES Adotante(CPF)
);