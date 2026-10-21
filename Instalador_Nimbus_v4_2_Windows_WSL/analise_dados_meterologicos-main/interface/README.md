# Nimbus — Interface Tkinter

Na raiz do projeto, execute `python -m interface.app`. Para trabalhar com arquivos JSON locais mantenha `NIMBUS_STORAGE=local`; para usar a API, configure `NIMBUS_STORAGE=api` em `.env`, inicie `docker compose up --build -d`, e só então abra a interface.

A tela **Importação JSON** importa arquivos no formato `{"observacoes":[...]}`, com objetos `ponto`, `fonte`, `data_hora`, `temperatura`, `umidade` e `precipitacao`. Baixe o modelo na própria tela ou use `interface/exemplos/observacoes_exemplo.json`. Um relatório indica cada item validado ou rejeitado. O importador pode criar ou reutilizar pontos e fontes automaticamente.

No Codespaces, a porta 8765 fornece um portal de envio de JSON. Mantenha a porta como **Private**. O portal exige token de upload, mas esse token é entregue ao carregar a página e não fornece autenticação de usuários.

Nas análises, filtre ponto e fonte para consultar precipitação acumulada, além de escolher datas. Dados locais ficam em `interface/dados/`, que está ignorada pelo Git. Consulte o `README.md` da raiz para a API REST e os testes.
