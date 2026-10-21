# Etapa 1 — Requisitos atualizados do Nimbus (revisão 2026-10-21)

O documento original está preservado em `docs/Etapa1_original_arquivo_recebido.md`. Esta revisão consolida as decisões implementadas; regras não explicitadas no material da disciplina devem ser confirmadas com o professor.

## Objetivo

Cadastrar pontos de observação, fontes e medições meteorológicas; consultar, filtrar e comparar temperatura, umidade e precipitação em períodos definidos.

## Regras de negócio

- **RN01:** pontos têm nome obrigatório (até 100 caracteres), latitude e longitude obrigatórias (seis casas decimais), cidade e estado opcionais; sigla UF deve pertencer ao Brasil quando informada.
- **RN02:** fontes têm nome (até 100) e tipo (até 50) obrigatórios e descrição opcional (até 255).
- **RN03:** registros têm ponto, fonte, data/hora, temperatura, umidade e precipitação obrigatórios.
- **RN04:** temperatura deve estar entre -90 e 60 °C, umidade entre 0 e 100%, precipitação entre 0 e 999999,99 mm, máximo de duas casas decimais; medição com mais casas decimais deve ser rejeitada, não arredondada.
- **RN05:** duas observações não podem compartilhar a tríade (ponto, fonte, data/hora).
- **RN06:** registro com data/hora futura deve ser rejeitado; adota-se horário civil de America/Sao_Paulo sem offset na entrada, armazenamento em DATETIME local.
- **RN07:** uma fonte ou ponto que tenha registros associados não deve ser excluído.
- **RN08:** entrada de arquivos obrigatoriamente em JSON UTF-8, formato `{"observacoes": [...]}` com ponto e fonte autossuficientes. Não há importação CSV.
- **RN09:** o importador valida cada item, reutiliza pontos/fontes equivalentes, cria apenas os necessários para registros aceitos e retorna quantidades aceitas/rejeitadas e justificativas.
- **RN10:** consultas e análises filtram ponto, fonte e período; não agregam chuva entre múltiplos pontos ou fontes.

## Persistência

Modo local: arquivos JSON em `interface/dados/`. Modo integrado: Tkinter -> Flask -> SQLAlchemy -> MySQL. O diagrama atualizado está em `docs/modelo_entidade_relacionamento_atualizado.svg`, e a versão editável em `docs/modelo_entidade_relacionamento.drawio`; seus nomes e nulabilidade devem refletir o script `database/init.sql` e os modelos ORM.

## Etapas

- Modelagem das três entidades: implementada, com testes locais.
- Interface desktop: implementada.
- JSON de importação: implementado.
- API REST: código implementado, dependente de validação com MySQL/Docker.
- Segurança de publicação e autenticação multiusuário: fora do escopo da versão acadêmica; acesso local recomendado.
