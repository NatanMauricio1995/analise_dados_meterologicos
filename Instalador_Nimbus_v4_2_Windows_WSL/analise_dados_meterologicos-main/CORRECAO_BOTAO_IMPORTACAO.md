# Nimbus v4.2 — correção do botão de importação JSON

## Erro corrigido

No Windows (Tkinter com Python 3.14), ao clicar em **Validar e importar JSON**, o programa mostrava:

```
AttributeError: 'NoneType' object has no attribute 'configure'
```

**Causa:** `self.import_button = tk.Button(...).pack(...)` atribuía o retorno de `pack()` (`None`) em vez de guardar o botão.

**Solução:** criar o `tk.Button`, atribuir à variável `self.import_button` e chamar `self.import_button.pack(...)` separadamente. A correção foi feita em `interface/telas/importacao_json.py`.

## Execução no PowerShell do Windows

```powershell
$env:NIMBUS_STORAGE = "local"
python -m interface.app
```

Entre em **Importação JSON**, escolha o arquivo, clique em **Validar e importar JSON**. Não é necessário Docker para o modo local.

## Testes

```powershell
python -m unittest discover -s interface/tests -v
```

Os testes de interface com Tkinter são executados quando há display disponível e cobrem importação, duplicação e JSON inválido. Os demais testes continuam verificando a lógica dos serviços.
