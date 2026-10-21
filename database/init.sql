
-- O MYSQL_DATABASE do Compose seleciona o banco automaticamente.
-- No terminal: mysql -u usuario -p nome_do_banco < database/init.sql

-- TABELA 1: PONTOS DE OBSERVAÇÃO
CREATE TABLE IF NOT EXISTS ponto_observacao (
    ponto_observacao_id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    cidade VARCHAR(100) NULL,
    estado CHAR(2) NULL,

    CONSTRAINT chk_ponto_latitude
        CHECK (latitude BETWEEN -90 AND 90),

    CONSTRAINT chk_ponto_longitude
        CHECK (longitude BETWEEN -180 AND 180)
) ENGINE=InnoDB;


-- TABELA 2: FONTES DE DADOS
CREATE TABLE IF NOT EXISTS fonte_dados (
    fonte_dados_id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descricao VARCHAR(255)
) ENGINE=InnoDB;


-- TABELA 3: REGISTROS METEOROLÓGICOS
CREATE TABLE IF NOT EXISTS registro_meteorologico (
    registro_meteorologico_id INT AUTO_INCREMENT PRIMARY KEY,

    ponto_observacao_id INT NOT NULL,
    fonte_dados_id INT NOT NULL,

    data_hora DATETIME NOT NULL,
    temperatura DECIMAL(5,2) NOT NULL,
    umidade DECIMAL(5,2) NOT NULL,
    precipitacao DECIMAL(8,2) NOT NULL,

    CONSTRAINT fk_registro_ponto
        FOREIGN KEY (ponto_observacao_id)
        REFERENCES ponto_observacao(ponto_observacao_id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_registro_fonte
        FOREIGN KEY (fonte_dados_id)
        REFERENCES fonte_dados(fonte_dados_id)
        ON DELETE RESTRICT,

    CONSTRAINT uq_registro_observacao
        UNIQUE (
            fonte_dados_id,
            ponto_observacao_id,
            data_hora
        ),

    CONSTRAINT chk_registro_temperatura
        CHECK (temperatura BETWEEN -90 AND 60),

    CONSTRAINT chk_registro_umidade
        CHECK (umidade BETWEEN 0 AND 100),

    CONSTRAINT chk_registro_precipitacao
        CHECK (precipitacao >= 0)
) ENGINE=InnoDB;
