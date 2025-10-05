--------------------------- CONTAGEM DE TUPLAS ---------------------------
-- Contagem de tuplas por tabela em uma tabela
SELECT 'endereco'            AS tabela, COUNT(*) AS qtde FROM endereco            UNION ALL
SELECT 'pessoa'                        , COUNT(*)        FROM pessoa              UNION ALL
SELECT 'gato'                          , COUNT(*)        FROM gato                UNION ALL
SELECT 'voluntario'                    , COUNT(*)        FROM voluntario          UNION ALL
SELECT 'adotante'                      , COUNT(*)        FROM adotante            UNION ALL
SELECT 'veterinario'                   , COUNT(*)        FROM veterinario         UNION ALL
SELECT 'funcao'                        , COUNT(*)        FROM funcao              UNION ALL
SELECT 'doacao'                        , COUNT(*)        FROM doacao              UNION ALL
SELECT 'campanha'                      , COUNT(*)        FROM campanha            UNION ALL
SELECT 'participantes'                 , COUNT(*)        FROM participantes       UNION ALL
SELECT 'contato'                       , COUNT(*)        FROM contato             UNION ALL
SELECT 'lar_temporario'                , COUNT(*)        FROM lar_temporario      UNION ALL
SELECT 'cuida_lar'                     , COUNT(*)        FROM cuida_lar           UNION ALL
SELECT 'evento'                        , COUNT(*)        FROM evento              UNION ALL
SELECT 'voluntarios_evento'            , COUNT(*)        FROM voluntarios_evento  UNION ALL
SELECT 'gatos_evento'                  , COUNT(*)        FROM gatos_evento        UNION ALL
SELECT 'fotos_gato'                    , COUNT(*)        FROM fotos_gato          UNION ALL
SELECT 'hospedagem'                    , COUNT(*)        FROM hospedagem          UNION ALL
SELECT 'gasto'                         , COUNT(*)        FROM gasto               UNION ALL
SELECT 'procedimento'                  , COUNT(*)        FROM procedimento        UNION ALL
SELECT 'preferencia'                   , COUNT(*)        FROM preferencia         UNION ALL
SELECT 'triagem'                       , COUNT(*)        FROM triagem             UNION ALL
SELECT 'fotos_triagem'                 , COUNT(*)        FROM fotos_triagem       UNION ALL
SELECT 'adocao'                        , COUNT(*)        FROM adocao              UNION ALL
SELECT 'devolucao'                     , COUNT(*)        FROM devolucao
ORDER BY tabela;

-- Contagem de tuplas por tabela para cada tabela
SELECT 'endereco' AS tabela, COUNT(*) AS qtde FROM endereco;
SELECT 'pessoa'   AS tabela, COUNT(*) AS qtde FROM pessoa;
SELECT 'gato'     AS tabela, COUNT(*) AS qtde FROM gato;
SELECT 'voluntario' AS tabela, COUNT(*) AS qtde FROM voluntario;
SELECT 'adotante'   AS tabela, COUNT(*) AS qtde FROM adotante;
SELECT 'veterinario' AS tabela, COUNT(*) AS qtde FROM veterinario;
SELECT 'funcao'       AS tabela, COUNT(*) AS qtde FROM funcao;
SELECT 'doacao'       AS tabela, COUNT(*) AS qtde FROM doacao;
SELECT 'campanha'     AS tabela, COUNT(*) AS qtde FROM campanha;
SELECT 'participantes' AS tabela, COUNT(*) AS qtde FROM participantes;
SELECT 'contato'       AS tabela, COUNT(*) AS qtde FROM contato;
SELECT 'lar_temporario' AS tabela, COUNT(*) AS qtde FROM lar_temporario;
SELECT 'cuida_lar'       AS tabela, COUNT(*) AS qtde FROM cuida_lar;
SELECT 'evento'          AS tabela, COUNT(*) AS qtde FROM evento;
SELECT 'voluntarios_evento' AS tabela, COUNT(*) AS qtde FROM voluntarios_evento;
SELECT 'gatos_evento'        AS tabela, COUNT(*) AS qtde FROM gatos_evento;
SELECT 'fotos_gato'          AS tabela, COUNT(*) AS qtde FROM fotos_gato;
SELECT 'hospedagem'          AS tabela, COUNT(*) AS qtde FROM hospedagem;
SELECT 'gasto'               AS tabela, COUNT(*) AS qtde FROM gasto;
SELECT 'procedimento'        AS tabela, COUNT(*) AS qtde FROM procedimento;
SELECT 'preferencia'         AS tabela, COUNT(*) AS qtde FROM preferencia;
SELECT 'triagem'             AS tabela, COUNT(*) AS qtde FROM triagem;
SELECT 'fotos_triagem'       AS tabela, COUNT(*) AS qtde FROM fotos_triagem;
SELECT 'adocao'              AS tabela, COUNT(*) AS qtde FROM adocao;
SELECT 'devolucao'           AS tabela, COUNT(*) AS qtde FROM devolucao;
--------------------------------------------------------------------------

--------------------------- CONSULTAS SIMPLES ---------------------------

-- Gatos disponíveis para adoção 
SELECT g.id, g.nome, g.idade, g.cor, g.raca, g.condicao_saude
FROM gato g
WHERE (g.adotado IS NULL OR g.adotado = FALSE)
ORDER BY g.id;

-- Gatos atualmente hospedados e o lar onde estão
SELECT h.gato_id, g.nome AS nome_gato, h.lar_temporario_id, h.data_entrada
FROM hospedagem h
JOIN gato g ON g.id = h.gato_id
WHERE h.data_saida IS NULL
ORDER BY h.data_entrada DESC;

-- Capacidade total de lares e ocupação atual
WITH ocup AS (
  SELECT lar_temporario_id, COUNT(*) AS ocupacao
  FROM hospedagem
  WHERE data_saida IS NULL
  GROUP BY lar_temporario_id
)

-- Gastos por tipo
SELECT tipo, COUNT(*) AS qtd, SUM(valor) AS total
FROM gasto
GROUP BY tipo
ORDER BY total DESC;

-- Gastos por gato
SELECT g.id AS gato_id, g.nome, COUNT(*) AS qtd_gastos, SUM(ga.valor) AS total_gasto
FROM gasto ga
JOIN gato g ON g.id = ga.gato_id
GROUP BY g.id, g.nome
ORDER BY total_gasto DESC NULLS LAST;

-- Procedimentos veterinários por tipo
SELECT tipo, COUNT(*) AS qtd, SUM(COALESCE(custo,0)) AS custo_total
FROM procedimento
GROUP BY tipo
ORDER BY qtd DESC;

-- Adoções por ano
SELECT EXTRACT(YEAR FROM data)::INT AS ano, COUNT(*) AS qtd_adocoes
FROM adocao
GROUP BY 1
ORDER BY ano DESC;

-- Devoluções por ano
SELECT EXTRACT(YEAR FROM data)::INT AS ano, COUNT(*) AS qtd_devolucoes
FROM devolucao
GROUP BY 1
ORDER BY ano DESC;

-- Voluntários por lar temporário
SELECT l.id AS lar_id, pe.nome AS voluntario, v.cpf
FROM cuida_lar cl
JOIN lar_temporario l ON l.id = cl.lar_id
JOIN voluntario v ON v.cpf = cl.voluntario_cpf
JOIN pessoa pe ON pe.cpf = v.cpf
ORDER BY lar_id, voluntario;