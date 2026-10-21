# Nimbus

**Sistema de Análise de Dados Meteorológicos** desenvolvido em Python para a disciplina de Programação Aplicada (PAV).

**Integrantes:** Natan Mauricio Santos e Arthur Maia Rangel.

> **Status:** o frontend possui telas de gerenciamento, importação CSV e análises estatísticas, com armazenamento local em JSON para desenvolvimento e testes. A integração definitiva com a API REST e o MySQL deve ser concluída em conjunto com o backend.

## 1. Objetivo

O Nimbus organiza observações meteorológicas coletadas em diferentes momentos e pontos geográficos. O sistema permite cadastrar pontos de observação e fontes de dados, armazenar temperatura, umidade e precipitação, consultar históricos e calcular estatísticas e comparações por período e ponto.

Além das operações de cadastro, consulta, edição e exclusão, o sistema oferece importação validada de arquivos CSV e recursos de análise dos dados meteorológicos.

## 2. Funcionalidades

- Cadastro, consulta, edição e exclusão de pontos de observação.
- Cadastro, consulta, edição e exclusão de fontes de dados.
- Cadastro, consulta, edição e exclusão de registros meteorológicos.
- Importação de observações por CSV, com criação automática ou reutilização de pontos e fontes.
- Relatório de linhas importadas e rejeitadas, com o motivo de cada rejeição.
- Filtros por período e ponto de observação.
- Cálculo de média, mínimo e máximo de temperatura e umidade.
- Cálculo de precipitação acumulada e máxima.
- Comparação entre pontos de observação e entre períodos.
- Validação dos dados e identificação de registros duplicados.

## 3. Modelo de dados

O modelo possui três entidades relacionadas.

### `ponto_observacao`

Representa um **ponto geográfico específico**, como uma estação meteorológica ou um local definido por coordenadas. Não representa automaticamente uma cidade inteira.

| Campo | Descrição |
|---|---|
| `id` | Chave primária. |
| `nome` | Nome do ponto ou estação. |
| `latitude` | Latitude em graus decimais. |
| `longitude` | Longitude em graus decimais. |
| `cidade` | Município onde o ponto está localizado. |
| `estado` | Sigla do estado. |

### `fonte_dados`

| Campo | Descrição |
|---|---|
| `id` | Chave primária. |
| `nome` | Nome da fonte. |
| `tipo` | Categoria da fonte, como API, sensor ou registro manual. |
| `descricao` | Descrição opcional. |

### `registro_meteorologico`

| Campo | Descrição |
|---|---|
| `id` | Chave primária. |
| `ponto_observacao_id` | Chave estrangeira para `ponto_observacao`. |
| `fonte_dados_id` | Chave estrangeira para `fonte_dados`. |
| `data_hora` | Momento da observação. |
| `temperatura` | Temperatura em graus Celsius (°C). |
| `umidade` | Umidade relativa (%). |
| `precipitacao` | Precipitação em milímetros (mm). |

**Relacionamentos:** um ponto de observação pode ter muitos registros; uma fonte pode estar associada a muitos registros. Cada registro referencia um ponto e uma fonte existentes.

A combinação `fonte_dados_id + ponto_observacao_id + data_hora` identifica uma observação e não pode se repetir.

### Modelagem do banco de dados

O diagrama abaixo apresenta as entidades e os relacionamentos do banco de dados do Nimbus.

![Diagrama Entidade-Relacionamento](docs/modelo_entidade_relacionamento.png)

O arquivo editável está disponível em `docs/modelo_entidade_relacionamento.drawio`.

## 4. Regras de negócio principais

1. Cada registro deve estar associado a um ponto de observação cadastrado.
2. Temperatura, umidade, precipitação, data/hora, ponto e fonte são obrigatórios.
3. Umidade deve estar entre 0% e 100%.
4. Precipitação não pode ser negativa e é armazenada em mm.
5. Temperatura deve estar entre −90 °C e 60 °C, inclusive.
6. Datas e horas devem ser válidas e não podem estar no futuro.
7. A fonte de dados deve existir.
8. Não é permitido excluir ponto ou fonte que possua registros associados.
9. A data inicial de uma consulta deve ser anterior ou igual à data final.
10. Estatísticas devem respeitar os filtros; sem resultados, o sistema deve informar que não há dados.
11. Não pode haver dois registros com a mesma fonte, ponto e data/hora.
12. Linhas inválidas ou duplicadas no CSV devem ser identificadas no relatório de importação.
13. Latitude deve estar entre −90 e 90 graus.
14. Longitude deve estar entre −180 e 180 graus.
15. Nome, latitude, longitude, cidade e estado são obrigatórios no cadastro do ponto e no CSV autossuficiente.
16. Nome e tipo da fonte são obrigatórios; a descrição é opcional.
17. Na importação CSV, pontos e fontes equivalentes devem ser reutilizados; cadastros novos só devem ser criados quando houver uma observação válida associada.

## 5. Formato de importação CSV

O formato atual é **autossuficiente**: cada linha contém os dados do ponto de observação, da fonte de dados e da observação meteorológica. Dessa forma, o usuário não precisa cadastrar previamente cada ponto e cada fonte antes da importação.

O arquivo deve utilizar:

- Codificação UTF-8 (com ou sem BOM).
- Ponto e vírgula (`;`) como separador de colunas.
- Ponto (`.`) como separador decimal.
- Data e hora no formato `AAAA-MM-DD HH:MM:SS`.
- Uma linha para cada observação meteorológica.

### Cabeçalho obrigatório

```csv
ponto_nome;latitude;longitude;cidade;estado;fonte_nome;fonte_tipo;fonte_descricao;data_hora;temperatura;umidade;precipitacao
```

### Exemplo

```csv
ponto_nome;latitude;longitude;cidade;estado;fonte_nome;fonte_tipo;fonte_descricao;data_hora;temperatura;umidade;precipitacao
ESTACAO CENTRAL;-22.903500;-43.209600;RIO DE JANEIRO;RJ;INMET;API;INSTITUTO NACIONAL DE METEOROLOGIA;2026-10-18 08:00:00;23.5;72;0.0
ESTACAO CENTRAL;-22.903500;-43.209600;RIO DE JANEIRO;RJ;INMET;API;INSTITUTO NACIONAL DE METEOROLOGIA;2026-10-18 14:00:00;29.8;61;0.0
ESTACAO SERRANA;-22.461000;-42.653000;TERESOPOLIS;RJ;OPEN-METEO;API;SERVICO METEOROLOGICO;2026-10-18 08:00:00;18.6;86;2.4
```

### Como funciona a criação automática

Para cada linha, o importador valida os dados do ponto, da fonte e da observação. Em seguida:

1. Procura um ponto com o mesmo nome, latitude, longitude, cidade e estado. Se encontrar, reutiliza o cadastro; caso contrário, prepara um novo ponto.
2. Procura uma fonte com o mesmo nome e tipo. Se encontrar, reutiliza o cadastro; caso contrário, prepara uma nova fonte.
3. Valida data/hora, temperatura, umidade, precipitação e duplicidade da observação.
4. Grava os registros válidos e os pontos/fontes novos que tenham pelo menos uma observação válida associada.
5. Apresenta um relatório por linha, identificando importações e rejeições e seus motivos.

A descrição da fonte é opcional e não participa da identificação usada para reutilizar uma fonte. Cidade e estado são atributos de `ponto_observacao`; o modelo não possui uma tabela de localidade separada.

### Data e hora na interface

Nos formulários do Nimbus, a data é digitada no padrão brasileiro `DD-MM-AAAA HH:MM`. A interface aplica a máscara enquanto o usuário digita. No CSV, utiliza-se o padrão `AAAA-MM-DD HH:MM:SS`, que é convertido para o formato interno do sistema.

## 6. Tecnologias

| Componente | Tecnologia |
|---|---|
| Linguagem | Python |
| API REST | Flask-RESTful (backend) |
| ORM | SQLAlchemy (backend) |
| Banco de dados | MySQL |
| Interface gráfica | Tkinter |
| Comunicação HTTP | `urllib.request` (cliente preparado para a API) |
| Leitura de CSV | Biblioteca padrão `csv` |
| Armazenamento temporário do frontend | Arquivos JSON |
| Ambiente de desenvolvimento | GitHub Codespaces |
| Interface gráfica remota | Desktop Lite / noVNC |
| Containers | Docker e Docker Compose |
| Versionamento | Git |

O armazenamento JSON é utilizado apenas durante o desenvolvimento do frontend. Na versão integrada, a interface deverá enviar e consultar os dados pela API REST, e o backend será responsável pela persistência no MySQL. A interface não acessará o banco diretamente. SQLite não será utilizado.

## 7. Arquitetura do projeto

```text
Nimbus/
├── projeto_API/
│   ├── entities/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── routes/
│   ├── config/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── interface/
│   ├── telas/
│   │   ├── base.py
│   │   ├── dashboard.py
│   │   ├── pontos.py
│   │   ├── fontes.py
│   │   ├── registros.py
│   │   ├── importacao_csv.py
│   │   └── analises.py
│   ├── services/
│   │   ├── storage.py
│   │   ├── validators.py
│   │   ├── csv_service.py
│   │   ├── statistics.py
│   │   ├── upload_server.py
│   │   └── api.py
│   ├── recursos/
│   │   ├── nimbus_logo.png
│   │   └── upload.html
│   ├── exemplos/
│   ├── dados/
│   ├── tests/
│   ├── config.py
│   ├── app.py
│   └── requirements.txt
├── database/
│   └── init.sql
├── .devcontainer/
│   └── devcontainer.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

- `entities`: modelos SQLAlchemy e relacionamentos do backend.
- `repositories`: acesso ao banco de dados.
- `services`: regras de negócio, importação, armazenamento local de desenvolvimento e estatísticas.
- `controllers`: coordenação de requisições e respostas.
- `routes`: endpoints HTTP.
- `config`: configurações da aplicação.
- `interface/telas`: páginas e formulários da interface gráfica.
- `interface/services`: validações, importação CSV, estatísticas, armazenamento temporário e comunicação HTTP.
- `interface/tests`: testes automatizados dos serviços do frontend.

Fluxo previsto para a versão integrada: **interface → API → services/repositories → MySQL**.

## 8. Divisão de responsabilidades

- **Natan Maurício Santos:** banco de dados, script SQL, modelos SQLAlchemy, backend, API REST, regras de negócio e importação CSV no backend.
- **Arthur Maia Rangel:** frontend em Tkinter, telas, formulários, seleção e envio de CSV, comunicação HTTP com a API e apresentação dos resultados e erros.
- **Em conjunto:** testes integrados, Docker, revisão de código, documentação e apresentação. Ambos devem compreender a arquitetura geral e as partes que apresentarem.

## 9. Execução e testes

### Requisitos do ambiente

- Python 3.10 ou superior.
- Tkinter instalado no ambiente.
- No GitHub Codespaces, utilizar a configuração em `.devcontainer/devcontainer.json`, que prepara o ambiente gráfico Desktop Lite.

O frontend utiliza a biblioteca padrão do Python e não exige instalação de pacotes externos por `pip`.

### Executar a interface

Na raiz do repositório:

```bash
python3 -m interface.app
```

No Codespaces, a janela Tkinter é exibida pelo Desktop Lite/noVNC. Abra a porta **6080** na aba **Ports** e acesse o endereço encaminhado pelo Codespaces.

### Executar os testes automatizados

Na raiz do repositório:

```bash
python3 -m unittest discover -s interface/tests -v
```

### Selecionar um CSV do computador no Codespaces

Quando o Nimbus roda no Codespaces, o seletor nativo do Tkinter acessa os arquivos do ambiente remoto, e não diretamente o disco do computador local. Para enviar um arquivo do computador:

1. Inicie o Nimbus com `python3 -m interface.app`.
2. Abra a aba **Ports** do VS Code no Codespaces.
3. Localize a porta **8765 — Nimbus - Enviar CSV do computador** e abra o endereço no navegador. Mantenha a porta como **Private**.
4. Na página aberta, clique em **Escolher arquivo**, selecione o CSV no computador e envie.
5. Volte à tela **Importação CSV** e atualize a lista de arquivos recebidos.
6. Selecione o arquivo enviado e clique em **Validar e importar CSV**.

O servidor de recebimento aceita arquivos `.csv` em UTF-8 e limita o tamanho a 15 MB. Os arquivos recebidos são armazenados em `interface/dados/importacoes/`, pasta ignorada pelo Git. Quando o Nimbus é executado diretamente no computador, o botão de seleção utiliza o seletor de arquivos local.

## 10. Situação do desenvolvimento

- [x] Interface modularizada em telas e serviços.
- [x] CRUD de pontos, fontes e registros no modo local.
- [x] Validação dos dados e das regras de negócio na interface.
- [x] Importação CSV autossuficiente com criação/reutilização de pontos e fontes.
- [x] Aceitação exclusiva do novo formato CSV, sem suporte ao modelo antigo por IDs.
- [x] Relatório por linha de registros importados e rejeitados.
- [x] Filtros, estatísticas e comparações no frontend.
- [x] Testes automatizados dos serviços do frontend.
- [ ] Integração das telas com os endpoints definitivos da API.
- [ ] Persistência integrada no MySQL por meio do backend.
- [ ] Testes integrados de ponta a ponta.
- [ ] Conclusão da configuração Docker da solução completa.
- [ ] Documentação e apresentação final.

## 11. Referências

- Enunciado do trabalho PAV.
- Documento inicial `REGRA DE NEGÓCIOS.pdf`.

Este README descreve o modelo e o estado de desenvolvimento do projeto. A presença de funcionalidades no frontend não significa que a integração com a API e o MySQL já esteja concluída.
