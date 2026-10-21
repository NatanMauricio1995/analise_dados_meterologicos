## Correção v4.1 — importação JSON no Windows

Consulte [CORRECAO_IMPORTACAO_JSON.md](CORRECAO_IMPORTACAO_JSON.md). Inclui correção da validação de fuso horário no Windows, mensagens de erro e identificação de observações duplicadas.

# Nimbus — Sistema de Análise de Dados Meteorológicos

Projeto acadêmico em Python: aplicação desktop Tkinter, API REST Flask, persistência MySQL e, opcionalmente, arquivos JSON locais. Os dados de entrada são **JSON**, não CSV.

**Autores originais:** Natan Mauricio Santos e Arthur Maia Rangel.

## Situação atual

- Telas Tkinter: pontos, fontes, registros, dashboard, importação JSON, análises e comparações.
- Modo `local`: utiliza três arquivos JSON, permitindo usar o desktop sem MySQL.
- Modo `api`: usa a API Flask e MySQL como armazenamento principal, sem duplicar dados em JSON locais.
- Regras de validação compartilhadas (`shared/`) e serviços CRUD no backend.
- Importação JSON com criação/reutilização de pontos/fontes, prevenção de duplicatas e relatório item a item.
- Filtros por **ponto, fonte e período**. Somente se calcula precipitação total quando há um único ponto e uma única fonte; caso contrário o total não é mostrado.

### Requisitos

- Python 3.13 ou versão compatível; Tkinter instalado (`python3-tk` no Ubuntu).
- Para a API: Docker Compose e Docker, ou MySQL 8 + pacotes Python listados em `projeto_API/requirements.txt`.
- Não exponha o servidor Flask ou o portal de upload diretamente à internet: não há autenticação de usuários.

## Início rápido: modo local (sem Docker)

Na raiz do projeto:

```bash
python -m interface.app
```

A aplicação usa `interface/dados/` e salva pontos, fontes e registros em JSON. Escolha **Importação JSON → Baixar modelo JSON** ou utilize `interface/exemplos/observacoes_exemplo.json`.

## Modo MySQL/API

1. Copie `.env.example` para `.env`, defina duas senhas fortes e ajuste `NIMBUS_STORAGE=api`.
2. Suba os serviços:

```bash
docker compose up --build -d
docker compose ps
```

3. Verifique `http://127.0.0.1:5000/health` e, em outro terminal, execute:

```bash
python -m interface.app
```

A API lê as variáveis `DB_*`, e o Docker Compose sobrescreve `DB_HOST` para `banco` **apenas dentro do contêiner**. Nunca inclua `.env` nos ZIPs ou no controle de versão.

> Se o banco já foi criado a partir de um projeto anterior, `init.sql` não altera as tabelas existentes: faça backup e aplique `database/migrate_v2.sql` somente na base correspondente. Não execute `docker compose down -v` em bancos com dados importantes.

## Entrada JSON

Formato de arquivo: objeto com propriedade `observacoes`, contendo uma lista de objetos. Exemplo:

```json
{
  "observacoes": [
    {
      "ponto": {"nome": "Estação Centro", "latitude": -22.90, "longitude": -43.20, "cidade": "Rio de Janeiro", "estado": "RJ"},
      "fonte": {"nome": "INMET", "tipo": "API", "descricao": "Fonte oficial"},
      "data_hora": "2026-10-18T14:00:00",
      "temperatura": 23.50,
      "umidade": 72.00,
      "precipitacao": 0.50
    }
  ]
}
```

Campos obrigatórios de `ponto`: `nome`, `latitude`, `longitude`; `cidade` e `estado` são opcionais. Campos obrigatórios de `fonte`: `nome`, `tipo`; `descricao` é opcional. Cada observação requer data/hora, temperatura, umidade e precipitação. Valores numéricos podem ser enviados como números ou strings decimais com até duas casas para medições e seis para coordenadas. Valores fora do intervalo ou com precisão excessiva são rejeitados, **não arredondados**.

`data_hora` segue ISO 8601 no **horário civil de America/Sao_Paulo sem offset**, por exemplo `2026-10-18T14:00:00`. A interface permite digitar `DD-MM-AAAA HH:MM` nos formulários. O sistema proíbe observações futuras.

O JSON pode conter múltiplas observações. Registros inválidos são rejeitados com indicação do item e do motivo; os válidos são importados em lote. Não são criados pontos nem fontes quando o registro é rejeitado. Duplicatas têm mesma fonte, mesmo ponto e mesmo instante. Limite de arquivo: 15 MB; máximo de 50 mil observações.

### Endpoints HTTP

| Método | Endpoint | Uso |
|---|---|---|
| GET, POST | `/api/pontos-observacao` | Listar e criar pontos |
| GET, PUT, DELETE | `/api/pontos-observacao/<id>` | Consultar, editar e excluir ponto |
| GET, POST | `/api/fontes-dados` | Listar e criar fontes |
| GET, PUT, DELETE | `/api/fontes-dados/<id>` | Consultar, editar e excluir fonte |
| GET, POST | `/api/registros` | Listar e criar registros; GET aceita filtros |
| GET, PUT, DELETE | `/api/registros/<id>` | Consultar, editar e excluir registro |
| POST | `/api/importacoes/json` | Importar um documento JSON no formato acima |
| GET | `/api/analises` | Estatísticas filtradas |
| GET | `/health` | Saúde da API e conexão com banco |

Filtros para registros e análises: `ponto_observacao_id`, `fonte_dados_id`, `inicio`, `fim`. Datas de filtros HTTP são `YYYY-MM-DD`.

## Validação e testes

```bash
python -m pytest -q interface/tests
python -m compileall -q interface projeto_API shared
```

Os testes de serviços locais usam arquivos JSON temporários, os testes de backend usam SQLAlchemy e SQLite em memória, e os testes HTTP da API requerem Flask. Para validação final ainda é necessário testar o ciclo completo com MySQL/Docker em máquina com esses serviços instalados.

## Interpretação meteorológica

A precipitação deve ser informada como *acumulação no intervalo de observação definido pela fonte*. O sistema não consegue inferir esse intervalo automaticamente, nem eliminar sobreposição entre estações ou fontes. É responsabilidade do usuário confirmar que os intervalos de observação são comparáveis antes de interpretar os totais. Filtrar ponto e fonte evita a duplicação mais comum.

## Modelo entidade-relacionamento

Consulte `docs/modelo_entidade_relacionamento_atualizado.svg` (ou `.png`). O arquivo `.drawio` também está disponível para edição.

## Segurança

O `.env` está excluído do projeto distribuível e do Git (`.gitignore`). O portal de upload do Codespaces usa token na página, portanto deve ser mantido **Private**, já que esse token não equivale à autenticação robusta. Portas do banco e da API no Compose estão limitadas à interface de loopback do hospedeiro. Para uso público seria necessária autenticação, TLS, limites de taxa e controle de acesso.
