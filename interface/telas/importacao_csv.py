import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ..config import BG, WHITE, BLACK, GRAY, BORDER, RED, GREEN
from ..services.csv_service import CSVImportService
from .base import page_header, build_table


class CSVPage(tk.Frame):
    """Tela de importação CSV com seletor nativo e recebimento pelo navegador."""

    def __init__(self, parent, store, on_change=None, browser_upload_enabled=False):
        super().__init__(parent, bg=BG)
        self.store = store
        self.on_change = on_change
        self.browser_upload_enabled = browser_upload_enabled
        self.upload_dir = self.store.data_dir / "importacoes"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.selected_file = None
        self.uploaded_files = {}
        self._build()
        self.refresh_uploaded_files()

    def _build(self):
        page_header(
            self,
            "Importação CSV",
            "Escolha um arquivo CSV, confira o resultado da validação e importe as observações.",
        )

        panel = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True, padx=27, pady=(0, 20))

        tk.Label(
            panel,
            text="1. Escolher arquivo",
            bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=18, pady=(18, 5))

        tk.Label(
            panel,
            text=(
                "O arquivo deve estar no formato CSV, codificado em UTF-8, com separador ponto e vírgula (;). "
                "Use ponto como separador decimal."
            ),
            bg=WHITE, fg=GRAY, font=("Arial", 9), wraplength=900, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 10))

        picker_row = tk.Frame(panel, bg=WHITE)
        picker_row.pack(fill="x", padx=18, pady=5)

        tk.Button(
            picker_row,
            text="Procurar arquivo CSV...",
            command=self.choose_file,
            bg="#E5E7EB", fg=BLACK, relief="flat",
            padx=16, pady=10, cursor="hand2"
        ).pack(side="left")

        tk.Button(
            picker_row,
            text="Limpar seleção",
            command=self.clear_selection,
            bg="#F3F4F6", fg=BLACK, relief="flat",
            padx=12, pady=10, cursor="hand2"
        ).pack(side="left", padx=8)

        self.path_label = tk.Label(
            panel,
            text="Nenhum arquivo selecionado.",
            bg="#F9FAFB", fg=GRAY, anchor="w",
            justify="left", wraplength=900,
            padx=12, pady=9
        )
        self.path_label.pack(fill="x", padx=18, pady=(6, 12))

        if self.browser_upload_enabled:
            upload_box = tk.Frame(panel, bg="#F8FAFC", highlightbackground=BORDER, highlightthickness=1)
            upload_box.pack(fill="x", padx=18, pady=(0, 12))

            tk.Label(
                upload_box,
                text="Selecionar um arquivo que está no seu computador (Codespaces)",
                bg="#F8FAFC", fg=BLACK, font=("Arial", 10, "bold")
            ).pack(anchor="w", padx=12, pady=(10, 3))

            tk.Label(
                upload_box,
                text=(
                    "Como o Nimbus está rodando na nuvem, o botão Procurar abre os arquivos do ambiente remoto. "
                    "Para enviar um arquivo do seu PC: abra a aba Ports do VS Code, abra a porta 8765, "
                    "selecione o CSV na página do navegador e envie. Depois atualize a lista abaixo."
                ),
                bg="#F8FAFC", fg=GRAY, font=("Arial", 9),
                wraplength=900, justify="left"
            ).pack(anchor="w", padx=12, pady=(0, 9))

            received_row = tk.Frame(upload_box, bg="#F8FAFC")
            received_row.pack(fill="x", padx=12, pady=(0, 10))

            self.uploaded_var = tk.StringVar(value="")
            self.uploaded_combo = ttk.Combobox(
                received_row,
                textvariable=self.uploaded_var,
                state="readonly",
                font=("Arial", 9),
            )
            self.uploaded_combo.pack(side="left", fill="x", expand=True)
            self.uploaded_combo.bind("<<ComboboxSelected>>", self.select_uploaded_file)

            tk.Button(
                received_row,
                text="Atualizar arquivos recebidos",
                command=self.refresh_uploaded_files,
                bg="#E5E7EB", fg=BLACK, relief="flat",
                padx=12, pady=7, cursor="hand2"
            ).pack(side="left", padx=(8, 0))

        expected = "ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao"
        tk.Label(
            panel, text="2. Cabeçalho obrigatório do CSV", bg=WHITE,
            fg=BLACK, font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=18, pady=(4, 4))
        tk.Label(
            panel, text=expected, bg="#F3F4F6", fg=GRAY,
            font=("Consolas", 8), anchor="w", padx=8, pady=8
        ).pack(fill="x", padx=18)

        action_row = tk.Frame(panel, bg=WHITE)
        action_row.pack(fill="x", padx=18, pady=12)
        tk.Button(
            action_row,
            text="Validar e importar CSV",
            command=self.import_file,
            bg=BLACK, fg=WHITE, relief="flat",
            padx=18, pady=10, cursor="hand2"
        ).pack(side="left")

        self.summary = tk.Label(
            panel,
            text="3. Selecione um arquivo para iniciar a importação.",
            bg=WHITE, fg=GRAY, font=("Arial", 10, "bold"), anchor="w"
        )
        self.summary.pack(fill="x", padx=18, pady=(0, 12))

        tk.Label(
            panel, text="Relatório por linha", bg=WHITE,
            fg=BLACK, font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=18, pady=(4, 4))

        self.report = build_table(
            panel,
            ("linha", "status", "motivo"),
            {"linha": "Linha CSV", "status": "Resultado", "motivo": "Detalhe"},
            {"linha": 90, "status": 110, "motivo": 650},
            height=8,
        )

    def choose_file(self):
        """Abre o seletor nativo de arquivos do sistema que está executando o Tkinter."""
        initial_dir = self.upload_dir if self.upload_dir.exists() else Path.home()
        path = filedialog.askopenfilename(
            parent=self,
            title="Escolha o arquivo CSV",
            initialdir=str(initial_dir),
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.set_selected_file(path)

    def set_selected_file(self, path):
        candidate = Path(path)
        if candidate.suffix.lower() != ".csv":
            messagebox.showwarning(
                "Formato inválido", "Selecione um arquivo com extensão .csv.", parent=self
            )
            return
        if not candidate.is_file():
            messagebox.showerror(
                "Arquivo não encontrado", "O arquivo selecionado não existe ou não está acessível.", parent=self
            )
            return
        self.selected_file = candidate
        self.path_label.configure(text=str(candidate), fg=BLACK)
        self.summary.configure(text="Arquivo selecionado. Clique em Validar e importar CSV.", fg=GRAY)
        self.report.delete(*self.report.get_children())

    def clear_selection(self):
        self.selected_file = None
        self.path_label.configure(text="Nenhum arquivo selecionado.", fg=GRAY)
        self.summary.configure(text="Selecione um arquivo para iniciar a importação.", fg=GRAY)
        self.report.delete(*self.report.get_children())

    def refresh_uploaded_files(self):
        if not hasattr(self, "uploaded_combo"):
            return
        files = sorted(
            self.upload_dir.glob("*.csv"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
        self.uploaded_files = {path.name: path for path in files}
        names = list(self.uploaded_files)
        self.uploaded_combo["values"] = names
        if names and not self.uploaded_var.get():
            self.uploaded_var.set(names[0])
            self.set_selected_file(self.uploaded_files[names[0]])
        elif not names:
            self.uploaded_var.set("")

    def select_uploaded_file(self, _event=None):
        name = self.uploaded_var.get()
        path = self.uploaded_files.get(name)
        if path:
            self.set_selected_file(path)

    def import_file(self):
        if not self.selected_file:
            messagebox.showwarning(
                "Arquivo não selecionado",
                "Clique em Procurar arquivo CSV ou selecione um arquivo recebido do seu computador.",
                parent=self,
            )
            return
        try:
            result = CSVImportService(self.store).import_file(self.selected_file)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Falha na importação", str(exc), parent=self)
            return

        self.report.delete(*self.report.get_children())
        for line in result["linhas"]:
            self.report.insert(
                "", "end",
                values=(line["linha"], line["status"], line["motivo"]),
            )

        self.summary.configure(
            text=f'Importadas: {result["importadas"]}    |    Rejeitadas: {result["rejeitadas"]}',
            fg=GREEN if result["rejeitadas"] == 0 else RED,
        )
        messagebox.showinfo(
            "Importação concluída",
            f'Linhas importadas: {result["importadas"]}\nLinhas rejeitadas: {result["rejeitadas"]}',
            parent=self,
        )
        if self.on_change and result["importadas"]:
            self.on_change()
