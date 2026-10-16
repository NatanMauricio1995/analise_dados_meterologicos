# Nimbus — Etapa 1: Especificação e Planejamento

**Disciplina:** Programação Aplicada (PAV)  
**Integrantes:** Natan Maurício Santos e Arthur Maia Rangel  
**Tema:** Análise de dados meteorológicos  
**Status:** Especificação inicial revisada para representar pontos específicos de observação.

---

## 1. Identificação do sistema

**Nome:** Nimbus — Sistema de Análise de Dados Meteorológicos.

### 1.1 Problema
Dados meteorológicos coletados em diferentes momentos e pontos geográficos precisam ser organizados para permitir consultas históricas, análise estatística e comparação entre variáveis meteorológicas.

### 1.2 Solução proposta
Desenvolver uma aplicação que armazene observações meteorológicas associadas a pontos específicos de observação, identificados por nome e coordenadas geográficas. O sistema permitirá consultar, filtrar, resumir e comparar registros por período e ponto de observação. Os dados poderão ser inseridos manualmente ou importados de arquivos CSV.

### 1.3 Objetivo geral
Desenvolver um sistema em Python que integre banco de dados relacional, API REST e interface gráfica para armazenamento e análise de dados meteorológicos.

### 1.4 Objetivos específicos
- Cadastrar pontos específicos de observação com nome, latitude, longitude e dados administrativos.
- Cadastrar fontes de dados.
- Registrar temperatura, umidade relativa e precipitação associadas a data/hora, ponto de observação e fonte.
- Permitir entrada manual e importação de registros por CSV.
- Consultar registros por período, ponto de observação ou combinação dos filtros.
- Calcular média, mínimo e máximo das variáveis meteorológicas.
- Comparar dados de períodos ou pontos de observação diferentes.
- Validar dados e apresentar mensagens compreensíveis para operações inválidas.
- Demonstrar persistência, comunicação entre camadas e orientação a objetos.

### 1.5 Limites do escopo
A versão inicial trabalhará com dados meteorológicos já registrados. Não haverá previsão do tempo por inteligência artificial, coleta automática de sensores nem integração obrigatória com serviços meteorológicos externos. A importação CSV será uma forma de entrada de dados, não uma integração com serviço externo.

Cada registro de localidade representará **um ponto específico de observação**, como uma estação meteorológica ou um local definido por coordenadas. Não representará automaticamente uma cidade inteira.

---

## 2. Requisitos funcionais

| Código | Requisito |
|---|---|
| RF01 | Cadastrar, consultar, editar e excluir pontos de observação. |
| RF02 | Cadastrar, consultar, editar e excluir fontes de dados. |
| RF03 | Cadastrar, consultar, editar e excluir registros meteorológicos. |
| RF04 | Vincular cada registro a um ponto de observação e a uma fonte existentes. |
| RF05 | Filtrar registros por data inicial e final. |
| RF06 | Filtrar registros por ponto de observação. |
| RF07 | Combinar filtros de período e ponto de observação. |
| RF08 | Calcular média, mínimo e máximo das variáveis selecionadas. |
| RF09 | Comparar resultados de dois períodos ou de dois pontos de observação. |
| RF10 | Informar quando uma consulta não encontrar registros. |
| RF11 | Fazer a interface se comunicar com a API REST, sem acesso direto ao banco. |
| RF12 | Disponibilizar POST, GET, PUT e DELETE para cada entidade. |
| RF13 | Permitir importar registros meteorológicos a partir de arquivos CSV. |
| RF14 | Validar os dados de cada linha do CSV antes de persistir os registros e informar linhas rejeitadas e respectivos motivos. |
| RF15 | Evitar duplicidades tanto no cadastro manual quanto na importação CSV. |

---

## 3. Requisitos não funcionais

| Código | Requisito |
|---|---|
| RNF01 | Desenvolver o sistema em Python. |
| RNF02 | Utilizar um SGBD relacional permitido pelo enunciado; a escolha é MySQL. SQLite não será utilizado. |
| RNF03 | Utilizar SQLAlchemy para os modelos. |
| RNF04 | Organizar a API em camadas com responsabilidades separadas. |
| RNF05 | Utilizar Tkinter na interface gráfica. |
| RNF06 | Executar a interface fora dos containers Docker. |
| RNF07 | Executar API e banco em containers separados. |
| RNF08 | Fornecer Dockerfile, docker-compose.yml e script SQL de inicialização. |
| RNF09 | Apresentar mensagens claras para validação, registros inexistentes e falhas de comunicação. |
| RNF10 | Documentar instalação, execução e demonstração. |
| RNF11 | A importação CSV deve informar o resultado do processamento, incluindo registros importados, rejeitados e motivos de rejeição. |

---

## 4. Regras de negócio

As regras abaixo são a versão de trabalho do Nimbus, baseadas no tema e nas regras iniciais do grupo. Elas devem ser implementadas e testadas na API.

| Código | Regra de negócio | Como testar |
|---|---|---|
| RN01 | Todo registro meteorológico deve estar associado a um ponto de observação cadastrado. | Tentar criar registro com ponto inexistente. |
| RN02 | Temperatura, umidade, precipitação, data/hora, ponto de observação e fonte são obrigatórias. | Enviar cadastro sem um campo obrigatório. |
| RN03 | A umidade relativa deve estar entre 0% e 100%, inclusive. | Testar valores abaixo de 0 e acima de 100. |
| RN04 | A precipitação não pode ser negativa e será armazenada em milímetros (mm). | Testar valor negativo e conferir unidade. |
| RN05 | A temperatura será armazenada em graus Celsius (°C) e deve estar entre −90 °C e 60 °C, inclusive. | Testar −90, 60 e valores abaixo/acima desses limites. |
| RN06 | A data e a hora de cada observação devem ser válidas e não podem estar no futuro, considerando a data/hora de referência do sistema. | Enviar data inválida e uma data/hora futura. |
| RN07 | Todo registro deve estar associado a uma fonte de dados cadastrada. | Criar registro com fonte inexistente. |
| RN08 | A exclusão de um ponto de observação ou fonte que possua registros associados deve ser bloqueada, preservando a integridade dos dados. | Tentar excluir entidade em uso. |
| RN09 | Em consultas por período, a data inicial deve ser anterior ou igual à data final. | Consultar com início posterior ao fim. |
| RN10 | Estatísticas devem considerar apenas registros correspondentes aos filtros; sem resultados, o sistema informa que não há dados para calcular. | Conferir cálculo com conjunto conhecido e testar consulta vazia. |
| RN11 | Não pode existir mais de um registro com a mesma combinação de fonte, ponto de observação e data/hora da observação. | Tentar cadastrar a mesma combinação duas vezes. |
| RN12 | Arquivos CSV devem ser validados antes de seus dados serem persistidos; linhas inválidas ou duplicadas devem ser identificadas no relatório de importação. | Importar arquivo com linhas válidas, inválidas e repetidas. |
| RN13 | A latitude deve estar entre −90 e 90 graus, inclusive. | Testar coordenadas fora do intervalo. |
| RN14 | A longitude deve estar entre −180 e 180 graus, inclusive. | Testar coordenadas fora do intervalo. |
| RN15 | Nome, latitude e longitude são obrigatórios para cadastrar um ponto de observação. | Tentar cadastrar ponto sem esses campos. |

### 4.1 Decisões de validação

- **Ponto de observação:** representa uma estação ou local específico, identificado por nome e coordenadas. Cidade e estado são dados administrativos complementares.
- **Latitude:** faixa válida de −90 a 90 graus.
- **Longitude:** faixa válida de −180 a 180 graus.
- **Temperatura:** faixa inclusiva de −90 °C a 60 °C.
- **Datas futuras:** proibidas. A aplicação deverá padronizar o tratamento de fuso horário.
- **Duplicidade:** bloqueada para a combinação `fonte_dados_id + ponto_observacao_id + data_hora`.
- **Entrada de dados:** cadastro manual e importação de CSV.
- **Unidades:** temperatura em °C, umidade em porcentagem (%) e precipitação em mm.
- **Exclusão:** bloquear a exclusão de pontos e fontes que possuam registros associados.
- **CSV inválido:** informar número da linha e motivo. Proposta: importar linhas válidas e relatar as rejeitadas, após validar o arquivo.

---

## 5. Modelo de dados

O projeto utilizará três tabelas relacionadas, dentro do limite de três a cinco tabelas exigido no enunciado.

### 5.1 Tabela `ponto_observacao`

| Campo | Finalidade |
|---|---|
| `id` | Chave primária. |
| `nome` | Nome do ponto, estação ou local de observação. |
| `latitude` | Latitude em graus decimais. |
| `longitude` | Longitude em graus decimais. |
| `cidade` | Município, como informação complementar. |
| `estado` | Estado, como informação complementar. |

### 5.2 Tabela `fonte_dados`

| Campo | Finalidade |
|---|---|
| `id` | Chave primária. |
| `nome` | Nome da fonte de dados. |
| `tipo` | Categoria da fonte, a definir conforme a origem dos dados. |
| `descricao` | Descrição opcional. |

A fonte deve representar a procedência dos dados. O mecanismo de entrada (manual ou CSV) não precisa ser confundido com a origem real dos dados. A equipe definirá como registrar essa informação na implementação.

### 5.3 Tabela `registro_meteorologico`

| Campo | Finalidade |
|---|---|
| `id` | Chave primária. |
| `ponto_observacao_id` | Chave estrangeira para `ponto_observacao`. |
| `fonte_dados_id` | Chave estrangeira para `fonte_dados`. |
| `data_hora` | Momento da observação. |
| `temperatura` | Temperatura em °C. |
| `umidade` | Umidade relativa em %. |
| `precipitacao` | Precipitação em mm. |

### 5.4 Relacionamentos e restrições

- Um ponto de observação pode ter muitos registros meteorológicos.
- Uma fonte pode estar associada a muitos registros.
- Cada registro pertence a um ponto de observação e a uma fonte existentes.
- A combinação (`fonte_dados_id`, `ponto_observacao_id`, `data_hora`) deve possuir restrição de unicidade.
- As chaves estrangeiras devem impedir referências a entidades inexistentes.
- A exclusão de pontos e fontes em uso deve ser bloqueada.
- Latitude e longitude devem ser armazenadas em tipos numéricos adequados para preservar casas decimais.

A validação crítica deve ocorrer na API e, quando possível, também ser reforçada por restrições no banco.

---

## 6. Formato CSV proposto

O formato padrão proposto usa UTF-8, ponto e vírgula como separador, ponto como separador decimal e data/hora no padrão `AAAA-MM-DD HH:MM:SS`.

```csv
ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao
1;1;2026-10-10 14:00:00;23.5;72;0.0
1;1;2026-10-10 15:00:00;24.1;68;0.2
2;1;2026-10-10 14:00:00;21.8;80;1.4
```

Os IDs devem corresponder a pontos de observação e fontes previamente cadastrados. A importação validará cabeçalhos, tipos, campos obrigatórios, intervalos, datas futuras e duplicidades.

A API deverá retornar um resumo da importação com quantidades importadas e rejeitadas e o motivo de rejeição por linha. O formato definitivo deve ser testado com o frontend antes da conclusão.

---

## 7. Tecnologias propostas

| Componente | Tecnologia |
|---|---|
| Linguagem | Python |
| API REST | Flask-RESTful |
| ORM | SQLAlchemy |
| Banco de dados | MySQL |
| Interface gráfica | Tkinter |
| Cliente HTTP | `requests` |
| Importação CSV | Biblioteca padrão `csv` do Python |
| Containers | Docker e Docker Compose |
| Controle de versão | Git |

Essas escolhas atendem às alternativas previstas no enunciado. A interface executará fora dos containers; API e banco serão containers separados.

---

## 8. Arquitetura planejada

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
│   ├── services/
│   ├── app.py
│   └── requirements.txt
├── database/
│   └── init.sql
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

### Responsabilidades das camadas
- **Entities:** modelos SQLAlchemy e relacionamentos.
- **Repositories:** acesso e consultas ao banco.
- **Services:** regras de negócio, importação e cálculos estatísticos.
- **Controllers:** coordenação das requisições e respostas.
- **Routes:** endpoints HTTP.
- **Config:** configuração da aplicação e conexão.
- **Interface:** telas e chamadas HTTP à API.

Fluxo: interface → API → services/repositories → banco de dados. A interface não acessa o banco diretamente.

---

## 9. Divisão de responsabilidades

- **Natan Maurício Santos:** banco de dados, script SQL, modelos SQLAlchemy, backend, API REST, regras de negócio e importação CSV no backend.
- **Arthur Maia Rangel:** frontend em Tkinter, telas de cadastro e consulta, formulários, seleção de CSV, comunicação HTTP com a API e apresentação de resultados/erros.
- **Trabalho conjunto:** testes integrados, Docker, revisão de código, documentação e apresentação. Ambos devem compreender a arquitetura geral e as partes que apresentarem.

---

## 10. Fases de desenvolvimento

1. **Etapa 1 — Especificação e planejamento:** confirmar escopo, requisitos, regras, modelo e tecnologias.
2. **Etapa 2 — Banco e modelos:** criar script SQL, configurar SQLAlchemy e testar relacionamentos.
3. **Etapa 3 — API REST:** implementar CRUD para as três entidades e tratar erros.
4. **Etapa 4 — Análises e importação:** implementar filtros, estatísticas, comparações e importação CSV.
5. **Etapa 5 — Interface gráfica:** construir telas e integrar com a API.
6. **Etapa 6 — Dockerização:** configurar containers separados para API e MySQL.
7. **Etapa 7 — Testes integrados:** testar regras, erros, persistência, importação e comunicação.
8. **Etapa 8 — Documentação e apresentação:** finalizar README, slides e roteiro de demonstração.

---

## 11. Critérios de aceite da Etapa 1

- [x] Nome e objetivo definidos.
- [x] Faixa de temperatura definida.
- [x] Política para datas futuras definida.
- [x] Regra de duplicidade definida.
- [x] Cadastro manual e importação CSV definidos.
- [x] Modelo inicial com três tabelas documentado.
- [x] Ponto de observação definido como local geográfico específico.
- [x] Latitude e longitude incluídas no modelo.
- [x] Divisão inicial de responsabilidades registrada.
- [ ] Revisão final e aprovação pelos dois integrantes.

---

## 12. Referências

- Enunciado do trabalho PAV: contexto, requisitos, banco, API, interface, Docker e apresentação.
- `REGRA DE NEGÓCIOS.pdf`: tema de análise de dados meteorológicos e regras iniciais do grupo.

Este documento é uma especificação de planejamento; não afirma que as funcionalidades já foram implementadas.
