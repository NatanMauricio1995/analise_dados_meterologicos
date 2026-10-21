-- Para bases antigas: faça backup antes de executar.
-- Execute UMA VEZ no banco de dados configurado (mysql -u USUARIO -p BANCO).
ALTER TABLE ponto_observacao
    MODIFY COLUMN cidade VARCHAR(100) NULL,
    MODIFY COLUMN estado CHAR(2) NULL;
