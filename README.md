# Nimbus - Interface grafica

Frontend do Nimbus em Python/Tkinter.

## Executar no GitHub Codespaces

1. Abra o Codespace do repositorio.
2. No terminal execute:

   ```bash
   python3 interface/app.py
   ```

3. Na aba Ports, abra a porta 6080 (Nimbus Desktop / noVNC).
4. Clique em Connect. A senha padrao e `vscode`.

## Dependencias

O frontend utiliza bibliotecas da biblioteca padrao do Python. O Tkinter e instalado pelo dev container.

## Armazenamento durante o desenvolvimento

Os registros de teste sao gravados em arquivos JSON nesta pasta. Esses arquivos estao no `.gitignore` e nao serao enviados ao Git. Na versao integrada, o frontend devera comunicar-se com a API REST, que persistira os dados no MySQL.

## Data e hora

A interface aceita data/hora em formato brasileiro `DD-MM-AAAA HH:MM`, com mascara automatica ao digitar os 12 numeros `DDMMAAAAHHMM`. Internamente, o valor e armazenado como `AAAA-MM-DD HH:MM:SS`.
