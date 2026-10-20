import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil

from ..config import BG, WHITE, BLACK, GRAY, BORDER, RED, GREEN
from ..services.csv_service import CSVImportService, HEADERS
from .base import page_header, build_table


class CSVPage(tk.Frame):
    """Importa observações e cadastra/reutiliza ponto e fonte a partir do CSV."""

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
            "Importe observações com os dados do local, do ponto e da fonte incluídos no próprio arquivo.",
        )

        panel = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        top = tk.Frame(panel, bg=WHITE)
        top.pack(fill="x", padx=16, pady=(12, 5))

        tk.Label(
            top,
            text="1. Selecione o arquivo",
            bg=WHITE, fg=BLACK, font=("Arial", 13, "bold")
        ).pack(side="left")

        tk.Label(
            panel,
            text=(
                "Formato: CSV UTF-8, separador ; e decimal com ponto. "
                "Cada linha contém uma observação e também os dados para localizar ou cadastrar "
                "automaticamente o ponto de observação e a fonte."
            ),
            bg=WHITE, fg=GRAY, font=("Arial", 9), wraplength=1000, justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 7))

        picker_row = tk.Frame(panel, bg=WHITE)
        picker_row.pack(fill="x", padx=16, pady=4)

        tk.Button(
            picker_row,
            text="Procurar arquivo CSV...",
            command=self.choose_file,
            bg="#E5E7EB", fg=BLACK, relief="flat",
            padx=14, pady=8, cursor="hand2"
        ).pack(side="left")

        tk.Button(
            picker_row,
            text="Limpar seleção",
            command=self.clear_selection,
            bg="#F3F4F6", fg=BLACK, relief="flat",
            padx=11, pady=8, cursor="hand2"
        ).pack(side="left", padx=7)

        tk.Button(
            picker_row,
            text="Baixar modelo CSV",
            command=self.download_template,
            bg="#F3F4F6", fg=BLACK, relief="flat",
            padx=11, pady=8, cursor="hand2"
        ).pack(side="left")

        self.path_label = tk.Label(
            panel,
            text="Nenhum arquivo selecionado.",
            bg="#F9FAFB", fg=GRAY, anchor="w",
            justify="left", wraplength=1000,
            padx=10, pady=7
        )
        self.path_label.pack(fill="x", padx=16, pady=(4, 7))

        if self.browser_upload_enabled:
            upload_box = tk.Frame(panel, bg="#F8FAFC", highlightbackground=BORDER, highlightthickness=1)
            upload_box.pack(fill="x", padx=16, pady=(0, 7))

            tk.Label(
                upload_box,
                text="Arquivo do seu computador (Codespaces)",
                bg="#F8FAFC", fg=BLACK, font=("Arial", 9, "bold")
            ).pack(anchor="w", padx=10, pady=(7, 2))

            tk.Label(
                upload_box,
                text=(
                    "Abra a porta 8765 na aba Ports, escolha o CSV no navegador e envie. "
                    "Depois selecione-o na lista abaixo."
                ),
                bg="#F8FAFC", fg=GRAY, font=("Arial", 8),
                wraplength=1000, justify="left"
            ).pack(anchor="w", padx=10, pady=(0, 6))

            received_row = tk.Frame(upload_box, bg="#F8FAFC")
            received_row.pack(fill="x", padx=10, pady=(0, 7))

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
                text="Atualizar lista",
                command=self.refresh_uploaded_files,
                bg="#E5E7EB", fg=BLACK, relief="flat",
                padx=10, pady=6, cursor="hand2"
            ).pack(side="left", padx=(7, 0))

        tk.Label(
            panel,
            text="2. Colunas do novo CSV (uma linha por observação)",
            bg=WHITE, fg=BLACK, font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=16, pady=(5, 3))

        headers_text = ";".join(HEADERS)
        tk.Label(
            panel,
            text=headers_text,
            bg="#F3F4F6", fg=GRAY,
            font=("Consolas", 8), anchor="w",
            justify="left", wraplength=1000, padx=8, pady=7
        ).pack(fill="x", padx=16)

        tk.Label(
            panel,
            text=(
                "O sistema reutiliza pontos com os mesmos nome, coordenadas, cidade e estado; "
                "e fontes com o mesmo nome e tipo. Se não encontrar, cria o cadastro automaticamente. "
                "Cidade e estado são campos do ponto de observação no modelo atual do Nimbus."
            ),
            bg=WHITE, fg=GRAY, font=("Arial", 8),
            wraplength=1000, justify="left"
        ).pack(anchor="w", padx=16, pady=(5, 7))

        action_row = tk.Frame(panel, bg=WHITE)
        action_row.pack(fill="x", padx=16, pady=5)

        tk.Button(
            action_row,
            text="Validar e importar CSV",
            command=self.import_file,
            bg=BLACK, fg=WHITE, relief="flat",
            padx=16, pady=8, cursor="hand2"
        ).pack(side="left")

        self.summary = tk.Label(
            action_row,
            text="Selecione um arquivo para iniciar.",
            bg=WHITE, fg=GRAY, font=("Arial", 9, "bold"), anchor="w"
        )
        self.summary.pack(side="left", padx=12)

        tk.Label(
            panel, text="3. Relatório por linha", bg=WHITE,
            fg=BLACK, font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=16, pady=(5, 2))

        self.report = build_table(
            panel,
            ("linha", "status", "motivo"),
            {"linha": "Linha CSV", "status": "Resultado", "motivo": "Detalhe"},
            {"linha": 75, "status": 100, "motivo": 650},
            height=6,
        )

    def download_template(self):
        template = Path(__file__).resolve().parents[1] / "exemplos" / "observacoes_exemplo.csv"
        if not template.is_file():
            messagebox.showerror(
                "Modelo não encontrado",
                "O arquivo de modelo CSV não está disponível na pasta exemplos.",
                parent=self,
            )
            return
        destination = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar modelo CSV do Nimbus",
            initialfile="modelo_importacao_nimbus.csv",
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
        )
        if not destination:
            return
        try:
            shutil.copyfile(template, destination)
        except OSError as exc:
            messagebox.showerror("Falha ao salvar modelo", str(exc), parent=self)
            return
        messagebox.showinfo(
            "Modelo salvo",
            "O modelo CSV foi salvo. Preencha as linhas com os dados dos pontos, fontes e observações.",
            parent=self,
        )

    def choose_file(self):
        """Abre o seletor nativo no ambiente em que o Tkinter está sendo executado."""
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
            messagebox.showwarning("Formato inválido", "Selecione um arquivo com extensão .csv.", parent=self)
            return
        if not candidate.is_file():
            messagebox.showerror("Arquivo não encontrado", "O arquivo selecionado não existe ou não está acessível.", parent=self)
            return
        self.selected_file = candidate
        self.path_label.configure(text=str(candidate), fg=BLACK)
        self.summary.configure(text="Arquivo selecionado. Clique em Validar e importar CSV.", fg=GRAY)
        self.report.delete(*self.report.get_children())

    def clear_selection(self):
        self.selected_file = None
        self.path_label.configure(text="Nenhum arquivo selecionado.", fg=GRAY)
        self.summary.configure(text="Selecione um arquivo para iniciar.", fg=GRAY)
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
                "Selecione um CSV do ambiente ou envie um arquivo do seu computador.",
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
            text=(
                f'Importadas: {result["importadas"]} | Rejeitadas: {result["rejeitadas"]} | '
                f'Pontos criados: {result["pontos_criados"]} | Fontes criadas: {result["fontes_criadas"]}'
            ),
            fg=GREEN if result["rejeitadas"] == 0 else RED,
        )
        messagebox.showinfo(
            "Importação concluída",
            f'Observações importadas: {result["importadas"]}\n'
            f'Linhas rejeitadas: {result["rejeitadas"]}\n'
            f'Pontos criados automaticamente: {result["pontos_criados"]}\n'
            f'Fontes criadas automaticamente: {result["fontes_criadas"]}',
            parent=self,
        )
        if self.on_change and result["importadas"]:
            self.on_change()
