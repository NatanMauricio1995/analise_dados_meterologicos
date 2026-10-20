# Nimbus — Interface gráfica

Frontend do Nimbus em Python com Tkinter. O projeto separa as telas e os serviços para facilitar a leitura e a manutenção.

## Executar

Na raiz do repositório:

```bash
python3 -m interface.app
```

## Funcionalidades

- Dashboard com indicadores e histórico de temperatura.
- Cadastro, consulta, edição e exclusão de pontos, fontes e registros.
- Máscara brasileira de data e hora: `DD-MM-AAAA HH:MM`.
- Importação CSV com criação ou reutilização automática de pontos e fontes.
- Relatório de linhas importadas e rejeitadas.
- Filtros por ponto e período, estatísticas e comparações.
- Envio de CSV do computador para o Codespaces pela porta 8765.

## Dados durante o desenvolvimento

Enquanto a API não estiver integrada, os dados são salvos em arquivos JSON dentro de `interface/dados/`. O frontend não acessa o MySQL diretamente. O arquivo `services/api.py` contém o cliente HTTP para a futura integração.

## Formato CSV aceito

O Nimbus aceita somente o formato autossuficiente abaixo:

```csv
ponto_nome;latitude;longitude;cidade;estado;fonte_nome;fonte_tipo;fonte_descricao;data_hora;temperatura;umidade;precipitacao
```

Cada linha contém os dados do ponto, da fonte e da observação. O sistema reutiliza pontos com o mesmo nome, coordenadas, cidade e estado; fontes com o mesmo nome e tipo; e cria cadastros quando ainda não existem e há uma observação válida.

O arquivo deve usar UTF-8, separador `;`, ponto decimal e data/hora `AAAA-MM-DD HH:MM:SS`. A descrição da fonte é opcional. O formato antigo baseado em IDs não é aceito.

## Testes

Na raiz do repositório:

```bash
python3 -m unittest discover -s interface/tests -v
```

## Enviar CSV do computador no Codespaces

1. Inicie a aplicação.
2. Abra a porta 8765 na aba Ports e mantenha a visibilidade como Private.
3. Na página aberta, escolha e envie o CSV do computador.
4. Na tela Importação CSV, atualize a lista de arquivos recebidos, selecione o arquivo e importe.

O servidor aceita arquivos CSV em UTF-8 de até 15 MB. Os arquivos recebidos ficam em `interface/dados/importacoes/`, pasta ignorada pelo Git.
