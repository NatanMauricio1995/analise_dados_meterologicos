# Nimbus — Solução para importação JSON no Windows (v4.1)

## Execução rápida SEM Docker

1. Extraia **todo** o ZIP e abra o Git Bash na pasta `analise_dados_meterologicos-main`.
2. Se existir `.env`, abra-o e configure `NIMBUS_STORAGE=local`.
3. Rode `python -m interface.app`.
4. Em **Importação JSON**, use **Procurar arquivo JSON...**, escolha
   `interface/exemplos/observacoes_exemplo.json` ou seu JSON de 140 observações,
   e clique em **Validar e importar JSON**.
5. Abra **Registros meteorológicos** e **Análises** para consultar os dados.

O programa também funciona sem instalar `tzdata`, graças ao fallback para o
horário atual UTC-03:00 usado em São Paulo desde a extinção do horário de verão.
A instalação recomendada é `python -m pip install -r interface/requirements.txt`.

**Atenção:** se o JSON já tiver sido importado, os itens aparecem como
**DUPLICADA** em vez de serem contados como rejeitados. Isso evita a interpretação
errada de que o arquivo não funcionou. Não apague os arquivos de `interface/dados/`
sem antes fazer backup: eles guardam os cadastros e as medições locais.

## Se ocorrer erro

A interface apresenta a causa na tela. Para falhas inesperadas, consulte
`interface/dados/erro_importacao_json.log`. Informe a mensagem de erro e diga
se aparece **MODO LOCAL (JSON)** ou **API / MySQL** no rodapé da interface.

## Formato de entrada

O arquivo deve ser JSON UTF-8 contendo um objeto com a chave `observacoes`,
que deve ser uma lista. Cada item exige `ponto`, `fonte`, `data_hora` em ISO 8601
sem offset, `temperatura`, `umidade` e `precipitacao`.
