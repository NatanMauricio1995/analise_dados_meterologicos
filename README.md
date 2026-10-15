# Nimbus
Sistema de análise de dados meteorológicos desenvolvido em Python para a disciplina de 	Programação em Ambiente Visual (PAV).

O Nimbus tem como objetivo armazenar observações meteorológicas, consultar dados históricos e gerar análises estatísticas por período e localidade. O projeto será desenvolvido em dupla por **Arthur Maia Rangel** e **Natan Mauricio Santos**.

>**Status:** Planejamento inicial. As tecnologias e regras propostas neste *README* devem ser confirmadas pela equipe antes da implementação.

## 1. Objetivos
- Cadastrar e manter localidades, fontes de dados e registros meteorológicos.
- Consultar observações por localidade, período ou combinação dos dois filtros.
- Calcular estatísticas como média, valor máximo e valor mínimo.
- Comparar dados entre períodos ou localidades.
- Validar os dados antes de armazená-los.
- Disponibilizar os dados por uma API REST e uma interface gráfica.
- Empacotar a API e o banco de dados em containers Docker.

*O projeto deve ir além de operações **CRUD***: o processamento e a análise dos dados meteorológicos são funcionalidades centrais.

## 2. Tecnologias propostas

| Componente | Tecnologia |
| :---: | :---: |
| *Linguagem* | Python |
| *API REST* | Flask-RESTful |
| *ORM / modelos* | SQLAlchemy |
| *Banco de dados* | MySQL |
| *Interface gráfica* | Tkinter |
| *Comunicação da interface com a API* | HTTP/JSON usando requests |
| *Containerização* | Docker e Docker Compose |
| *Controle de versão* | Git e GitHub |

As tecnologias são uma proposta inicial compatível com as opções do enunciado. A equipe pode confirmar ou ajustar as escolhas antes de iniciar a implementação.

## 3. Escopo funcional inicial

### Cadastros
- Localidades.
- Fontes de dados meteorológicos.
- Registros meteorológicos.
  
### Consultas e análises
- Consultar registros por período.
- Consultar registros por localidade.
- Combinar filtros de período e localidade.
- Calcular média, máximo e mínimo para as variáveis selecionadas.
- Comparar períodos ou localidades.
- Informar claramente quando uma consulta não encontrar registros.
  
### Validações propostas
As regras abaixo são decisões de projeto que deverão ser implementadas e testadas. Os limites específicos ainda precisam ser documentados.
1. Todo registro deve estar associado a uma localidade existente.
2. Os campos obrigatórios do registro devem ser informados.
3. A umidade relativa deve estar entre 0% e 100%.
4. A precipitação não pode ser negativa e será armazenada em milímetros (mm).
5. A temperatura deve respeitar uma faixa válida definida e documentada pelo projeto.
6. As datas devem ser válidas; a política para datas futuras será definida antes da implementação.
7. Todo registro deve estar associado a uma fonte de dados cadastrada.
8. A exclusão de localidade ou fonte com registros associados deve preservar a integridade dos dados.
9. A data inicial de uma consulta deve ser anterior ou igual à data final.
10. Estatísticas devem considerar apenas os registros válidos que correspondam aos filtros selecionados.
As regras originais do grupo estão no documento REGRA DE NEGÓCIOS.pdf. Antes da entrega da especificação, comparar esta lista com o documento e registrar formalmente as decisões finais.

## 4. Modelo de dados inicial
O projeto prevê três tabelas, dentro do limite de 3 a 5 tabelas solicitado no enunciado.

**`localidade`**
- `id` — chave primária.
- `nome` — nome da estação ou localidade.
- `cidade` — município.
- `estado` — estado.

**`fonte_dados`**
- id — chave primária.
- nome — nome da fonte.
- tipo — tipo de fonte (por exemplo, estação, arquivo ou serviço externo).
- descricao — descrição opcional.

**`registro_meteorologico`**
- id — chave primária.
- localidade_id — chave estrangeira para localidade.
- fonte_id — chave estrangeira para fonte_dados.
- data_hora — data e hora da observação.
- temperatura — temperatura em graus Celsius (°C).
- umidade — umidade relativa em porcentagem (%).
- precipitacao — precipitação em milímetros (mm).
  
**Relacionamentos:** uma localidade pode possuir vários registros; uma fonte pode ser utilizada por vários registros. Cada registro aponta para uma localidade e uma fonte existentes.
O modelo é preliminar. Tipos SQL, precisão decimal, restrições de unicidade, política de exclusão e tratamento de fuso horário serão definidos durante a fase de modelagem.

## 5. Estrutura planejada do projeto
```
Nimbus/
  ├── projeto_API/
  │   ├── entities/          # Modelos SQLAlchemy e relacionamentos
  │   ├── controllers/       # Coordenação das requisições
  │   ├── services/          # Regras de negócio e análises
  │   ├── repositories/      # Acesso e consultas ao banco
  │   ├── routes/            # Endpoints da API
  │   ├── config/            # Configurações
  │   ├── app.py             # Inicialização da API
  │   ├── requirements.txt   # Dependências da API
  │   └── Dockerfile
  ├── interface/
  │   ├── telas/             # Janelas e formulários Tkinter
  │   ├── services/          # Cliente HTTP para a API
  │   ├── app.py             # Inicialização da interface
  │   └── requirements.txt   # Dependências da interface
  ├── database/
  │   └── init.sql           # Script inicial do banco
  ├── docker-compose.yml
  ├── .env.example           # Exemplo de variáveis de ambiente
  ├── .gitignore
  └── README.md
```
A estrutura pode evoluir conforme a implementação. A interface gráfica deverá permanecer fora dos containers, enquanto a API e o banco de dados serão executados em containers separados.

## 6. Fases de desenvolvimento
### Fase 1 — Especificação e planejamento
- [ ] Confirmar as tecnologias.
- [ ] Revisar as regras de negócio originais.
- [ ] Definir os requisitos funcionais e não funcionais.
- [ ] Definir unidades, faixas válidas e política de datas.
- [ ] Desenhar o modelo entidade-relacionamento.
- [ ] Dividir as responsabilidades entre os integrantes.
Entrega: especificação aprovada e modelo de dados inicial.

### Fase 2 — Banco de dados e modelos
- [ ] Criar o banco MySQL e o script database/init.sql.
- [ ] Configurar a conexão com SQLAlchemy.
- [ ] Implementar as classes Localidade, FonteDados e RegistroMeteorologico.
- [ ] Definir chaves primárias, chaves estrangeiras e restrições.
- [ ] Testar os relacionamentos e a persistência.
Entrega: banco inicializado e modelos funcionando.

### Fase 3 — API REST e arquitetura em camadas
- [ ] Implementar repositories, services, controllers e routes.
- [ ] Criar operações POST, GET, PUT e DELETE para cada entidade.
- [ ] Padronizar respostas JSON e códigos HTTP.
- [ ] Tratar entradas inválidas, registros inexistentes e erros de banco.
- [ ] Demonstrar orientação a objetos e programação estruturada no código.
- [ ] Testar os endpoints.
Entrega: API funcional e documentada.

### Fase 4 — Análises meteorológicas
- [ ] Implementar filtros por período e localidade.
- [ ] Implementar média, máximo e mínimo.
- [ ] Implementar comparação entre períodos ou localidades.
- [ ] Tratar consultas sem resultados e evitar divisões por zero.
- [ ] Criar testes com dados conhecidos para conferir os cálculos.
Entrega: funcionalidades de ciência de dados além do CRUD.

### Fase 5 — Interface gráfica
- [ ] Criar telas de cadastro, consulta, edição e exclusão para as três entidades.
- [ ] Criar tela de filtros e análises.
- [ ] Consumir a API com requests.
- [ ] Exibir mensagens claras para erros de validação, comunicação e operações proibidas.
- [ ] Testar a interface com a API em execução.
Entrega: interface funcional executada fora dos containers.

### Fase 6 — Dockerização
- [ ] Criar o Dockerfile da API.
- [ ] Configurar o serviço MySQL no docker-compose.yml.
- [ ] Configurar variáveis de ambiente e dependências entre serviços.
- [ ] Garantir que o banco seja inicializado pelo script SQL.
- [ ] Testar a inicialização em ambiente limpo.
- [ ] Documentar como executar e encerrar o ambiente.
Entrega: API e banco executando em containers separados.

### Fase 7 — Testes integrados e revisão
- [ ] Testar o CRUD de todas as entidades.
- [ ] Testar as dez regras de negócio.
- [ ] Demonstrar pelo menos três regras durante a apresentação.
- [ ] Demonstrar pelo menos dois casos de erro.
- [ ] Verificar comunicação interface–API e persistência no banco.
- [ ] Revisar nomes, mensagens, documentação e tratamento de exceções.
Entrega: versão candidata à apresentação.

### Fase 8 — Documentação e apresentação
- [ ] Finalizar este README com instruções reais de instalação e execução.
- [ ] Preparar slides com contexto, problema, requisitos, banco, arquitetura, classes, endpoints, interface e dificuldades.
- [ ] Preparar roteiro de demonstração.
- [ ] Dividir a apresentação entre Arthur e Natan.
- [ ] Garantir que ambos compreendam as principais partes do código.
Entrega: código da API, código da interface e slides, conforme o enunciado.

## 7. Como executar
As instruções definitivas serão adicionadas quando a configuração estiver pronta. O objetivo é que, ao final, o ambiente possa ser iniciado a partir da raiz do projeto com Docker Compose e que a interface seja executada separadamente.
Exemplo previsto para a versão final:
```
# Iniciar API e banco de dados
docker compose up --build

# Em outro terminal, iniciar a interface
# (os comandos definitivos serão documentados após a configuração do ambiente)
```
Não execute esses comandos esperando que o projeto funcione antes da criação dos arquivos correspondentes.
## 8. Critérios de conclusão
O projeto estará pronto quando:
- [ ] Houver de 3 a 5 tabelas relacionais com modelos SQLAlchemy.
- [ ] Todas as entidades tiverem operações POST, GET, PUT e DELETE na API.
- [ ] A API aplicar as regras de negócio.
- [ ] A interface realizar as operações por meio da API.
- [ ] Existirem consultas, estatísticas e comparações de dados.
- [ ] A API e o banco forem executados em containers separados.
- [ ] O script SQL e o docker-compose.yml forem entregues.
- [ ] Os testes e a demonstração atenderem aos requisitos do professor.
- [ ] A documentação e os slides estiverem finalizados.
## 9. Equipe
- Arthur Maia Rangel
- Natan Maurício Santos
A divisão das tarefas será definida na Fase 1, buscando participação dos dois integrantes na implementação e compreensão do sistema.
## 10. Referência do trabalho
Projeto desenvolvido com base no enunciado da disciplina PAV e no documento de regras de negócio do grupo. Este README representa o planejamento inicial; decisões e comandos deverão ser atualizados para refletir o código efetivamente implementado.
