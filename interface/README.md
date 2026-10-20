# Nimbus - Interface gráfica

Frontend do Nimbus desenvolvido em Python com Tkinter. A estrutura separa as telas, os serviços de validação, armazenamento, estatísticas e importação CSV.

## Executar no GitHub Codespaces

Na raiz do repositório, abra o terminal e execute:

```bash
python3 -m interface.app
```

O Codespace deve ter Tkinter instalado (`python3-tk`) e o ambiente gráfico Desktop Lite habilitado pela pasta `.devcontainer`.

## Funcionalidades

- Dashboard com indicadores globais e histórico de temperatura.
- CRUD de pontos de observação.
- CRUD de fontes de dados.
- CRUD de registros meteorológicos.
- Máscara de data/hora brasileira: `DD-MM-AAAA HH:MM`.
- Importação CSV com separador `;`, cabeçalho validado, checagem de relacionamentos, valores, datas futuras e duplicidades; relatório de linhas aceitas e rejeitadas.
- Filtros por ponto e período.
- Estatísticas de média, mínimo, máximo e precipitação acumulada.
- Comparação entre dois pontos e entre dois períodos.

## Armazenamento durante o desenvolvimento

Enquanto a API do backend não estiver integrada, os dados de teste ficam em arquivos JSON na pasta `interface/dados/`. Esses arquivos são ignorados pelo Git. O frontend não acessa o MySQL diretamente.

O módulo `services/api.py` contém um cliente HTTP padrão, preparado para a futura integração. Os endpoints ainda precisam ser combinados com o responsável pelo backend.

## CSV

O cabeçalho deve ser exatamente:

```csv
ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao
```

Exemplo:

```csv
ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao
1;1;2026-10-10 14:00:00;23.5;72;0.0
1;1;2026-10-10 15:00:00;24.1;68;0.2
2;1;2026-10-10 14:00:00;21.8;80;1.4
```

Os IDs do arquivo devem existir previamente em pontos e fontes. O arquivo deve usar UTF-8, `;` como separador, ponto decimal e data/hora no formato `AAAA-MM-DD HH:MM:SS`.

## Testes automatizados

Na raiz do repositório:

```bash
python3 -m unittest discover -s interface/tests -v
```


## Selecionar um CSV do computador no GitHub Codespaces

Quando o Nimbus roda no Codespaces, a janela nativa do Tkinter navega pelos arquivos do ambiente remoto, não diretamente pelo disco do computador local. Para escolher um arquivo salvo no seu PC:

1. Inicie o Nimbus com `python3 -m interface.app`.
2. No VS Code do Codespaces, abra a aba **Ports**.
3. Localize a porta **8765 — Nimbus - Enviar CSV do computador** e abra o endereço no navegador. Mantenha a porta como **Private**.
4. Na página aberta, clique em **Escolher arquivo**. O seletor do navegador mostrará os arquivos do seu computador.
5. Clique em **Enviar CSV para o Nimbus**.
6. Volte à tela Importação CSV e clique em **Atualizar arquivos recebidos**.
7. Selecione o arquivo enviado na lista e clique em **Validar e importar CSV**.

O servidor de recebimento aceita apenas arquivos `.csv` em UTF-8 e limita o tamanho a 15 MB. Os arquivos recebidos ficam em `interface/dados/importacoes/` e são ignorados pelo Git.

Quando o Nimbus for executado diretamente no próprio computador, o botão **Procurar arquivo CSV** abre o seletor nativo daquele computador. No Codespaces, esse seletor nativo acessa o sistema de arquivos remoto; por isso, use o portal da porta 8765 para transferir arquivos do seu PC.
