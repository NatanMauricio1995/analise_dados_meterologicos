import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ..config import BG, WHITE, BLACK, GRAY, BORDER, RED, GREEN
from ..services.csv_service import CSVImportService
from .base import page_header, build_table


class CSVPage(tk.Frame):
    def __init__(self, parent, store, on_change=None):
        super().__init__(parent, bg=BG)
        self.store = store
        self.on_change = on_change
        self.selected_file = None
        self._build()

    def _build(self):
        page_header(self, "Importação CSV", "Importe observações meteorológicas e receba um relatório das linhas processadas.")
        panel = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True, padx=27, pady=(0, 20))

        tk.Label(panel, text="Arquivo de observações", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(
            panel,
            text="Formato: UTF-8, separador ponto e vírgula (;), decimal com ponto e data AAAA-MM-DD HH:MM:SS.",
            bg=WHITE, fg=GRAY, font=("Arial", 9), wraplength=850, justify="left"
        ).pack(anchor="w", padx=18, pady=(0, 12))

        expected = "ponto_observacao_id;fonte_dados_id;data_hora;temperatura;umidade;precipitacao"
        tk.Label(panel, text="Cabeçalho obrigatório:", bg=WHITE, fg=BLACK, font=("Arial", 9, "bold")).pack(anchor="w", padx=18)
        tk.Label(panel, text=expected, bg="#F3F4F6", fg=GRAY, font=("Consolas", 8), anchor="w", padx=8, pady=8).pack(fill="x", padx=18, pady=(4, 12))

        row = tk.Frame(panel, bg=WHITE)
        row.pack(fill="x", padx=18, pady=5)
        self.path_label = tk.Label(row, text="Nenhum arquivo selecionado.", bg=WHITE, fg=GRAY, anchor="w")
        self.path_label.pack(side="left", fill="x", expand=True)
        tk.Button(row, text="Selecionar CSV", command=self.choose_file, bg="#E5E7EB", fg=BLACK, relief="flat", padx=14, pady=8).pack(side="right", padx=5)
        tk.Button(row, text="Validar e importar", command=self.import_file, bg=BLACK, fg=WHITE, relief="flat", padx=14, pady=8).pack(side="right", padx=5)

        self.summary = tk.Label(panel, text="Selecione um arquivo para iniciar a importação.", bg=WHITE, fg=GRAY, font=("Arial", 10, "bold"), anchor="w")
        self.summary.pack(fill="x", padx=18, pady=14)

        tk.Label(panel, text="Relatório por linha", bg=WHITE, fg=BLACK, font=("Arial", 12, "bold")).pack(anchor="w", padx=18, pady=(8, 4))
        self.report = build_table(
            panel,
            ("linha", "status", "motivo"),
            {"linha": "Linha CSV", "status": "Resultado", "motivo": "Detalhe"},
            {"linha": 90, "status": 110, "motivo": 650},
            height=10,
        )

    def choose_file(self):
        path = filedialog.askopenfilename(
            parent=self,
            title="Selecionar arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if path:
            self.selected_file = path
            self.path_label.configure(text=Path(path).name, fg=BLACK)
            self.summary.configure(text="Arquivo selecionado. Clique em Validar e importar.", fg=GRAY)
            self.report.delete(*self.report.get_children())

    def import_file(self):
        if not self.selected_file:
            messagebox.showwarning("Arquivo não selecionado", "Selecione um arquivo CSV antes de importar.", parent=self)
            return
        try:
            result = CSVImportService(self.store).import_file(self.selected_file)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Falha na importação", str(exc), parent=self)
            return

        self.report.delete(*self.report.get_children())
        for line in result["linhas"]:
            self.report.insert("", "end", values=(line["linha"], line["status"], line["motivo"]))

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
