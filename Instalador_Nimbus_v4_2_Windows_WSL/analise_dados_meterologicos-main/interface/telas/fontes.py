import tkinter as tk
from tkinter import messagebox

from ..config import BG, WHITE, BLACK, GRAY, RED, BORDER
from ..services.validators import validate_source, ValidationError
from .base import page_header, field, status_label, build_table, show_error, show_success


class FontesPage(tk.Frame):
    def __init__(self, parent, store, on_change=None):
        super().__init__(parent, bg=BG)
        self.store = store
        self.on_change = on_change
        self.editing_id = None
        self.fields = {}
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "Fontes de dados", "Cadastre e gerencie as origens das observações meteorológicas.")
        area = tk.Frame(self, bg=BG)
        area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        area.columnconfigure(0, weight=0, minsize=300)
        area.columnconfigure(1, weight=1)
        area.rowconfigure(0, weight=1)

        form = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tk.Label(form, text="Dados da fonte", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(18, 8))
        self.fields["nome"] = field(form, "Nome da fonte *")
        self.fields["tipo"] = field(form, "Tipo da fonte *")
        self.fields["descricao"] = field(form, "Descrição (opcional)")
        buttons = tk.Frame(form, bg=WHITE)
        buttons.pack(fill="x", padx=16, pady=14)
        self.save_button = tk.Button(buttons, text="Cadastrar fonte", command=self.save, bg=BLACK, fg=WHITE, relief="flat", pady=9)
        self.save_button.pack(fill="x", pady=(0, 6))
        self.clear_button = tk.Button(buttons, text="Limpar formulário", command=self.clear, bg="#F3F4F6", fg=BLACK, relief="flat", pady=8)
        self.clear_button.pack(fill="x")
        self.status = status_label(form, "Nome e tipo são obrigatórios. A descrição é opcional.")

        panel = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew")
        tk.Label(panel, text="Fontes cadastradas", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        self.table = build_table(panel, ("id", "nome", "tipo", "descricao"),
                                 {"id": "ID", "nome": "Nome", "tipo": "Tipo", "descricao": "Descrição"},
                                 {"id": 45, "nome": 160, "tipo": 120, "descricao": 260})
        self.table.bind("<Double-1>", lambda event: self.prepare_edit())
        actions = tk.Frame(panel, bg=WHITE)
        actions.pack(fill="x", padx=14, pady=10)
        self.counter = tk.Label(actions, text="", bg=WHITE, fg=GRAY, font=("Arial", 9))
        self.counter.pack(side="left")
        tk.Button(actions, text="Editar", command=self.prepare_edit, bg="#E5E7EB", fg=BLACK, relief="flat", padx=12, pady=7).pack(side="right", padx=3)
        tk.Button(actions, text="Excluir", command=self.delete, bg="#FEE2E2", fg=RED, relief="flat", padx=12, pady=7).pack(side="right", padx=3)

    def save(self):
        try:
            values = validate_source({key: entry.get() for key, entry in self.fields.items()})
        except ValidationError as exc:
            show_error(self, self.status, str(exc))
            return
        try:
            if self.editing_id is None:
                self.store.add("fontes", values)
                message = "Fonte cadastrada com sucesso."
            else:
                self.store.update("fontes", self.editing_id, values)
                message = "Fonte atualizada com sucesso."
        except (OSError, KeyError, ValueError, ConnectionError) as exc:
            show_error(self, self.status, f"Não foi possível salvar a fonte: {exc}")
            return
        self.clear()
        self.refresh()
        show_success(self.status, message)
        if self.on_change:
            self.on_change()

    def prepare_edit(self):
        selected = self.table.selection()
        if not selected:
            self.status.configure(text="Selecione uma fonte para editar.", fg=RED)
            return
        item_id = int(selected[0])
        source = next((row for row in self.store.list("fontes") if int(row["id"]) == item_id), None)
        if source is None:
            return
        self.editing_id = item_id
        for key, entry in self.fields.items():
            entry.delete(0, tk.END)
            entry.insert(0, source.get(key) or "")
        self.save_button.configure(text="Salvar alterações")
        self.clear_button.configure(text="Cancelar edição")
        self.status.configure(text=f"Editando a fonte {item_id}.", fg="#B7791F")

    def clear(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.editing_id = None
        self.save_button.configure(text="Cadastrar fonte")
        self.clear_button.configure(text="Limpar formulário")
        self.status.configure(text="Nome e tipo são obrigatórios. A descrição é opcional.", fg=GRAY)

    def delete(self):
        selected = self.table.selection()
        if not selected:
            self.status.configure(text="Selecione uma fonte para excluir.", fg=RED)
            return
        item_id = int(selected[0])
        if any(int(row["fonte_dados_id"]) == item_id for row in self.store.list("registros")):
            show_error(self, self.status, "Esta fonte possui registros meteorológicos associados e não pode ser excluída.")
            return
        if not messagebox.askyesno("Confirmar exclusão", "Deseja realmente excluir a fonte selecionada?", parent=self):
            return
        try:
            self.store.delete("fontes", item_id)
        except (OSError, KeyError, ValueError, ConnectionError) as exc:
            show_error(self, self.status, f"Não foi possível excluir a fonte: {exc}")
            return
        if self.editing_id == item_id:
            self.clear()
        self.refresh()
        show_success(self.status, "Fonte excluída com sucesso.")
        if self.on_change:
            self.on_change()

    def refresh(self):
        self.table.delete(*self.table.get_children())
        for source in self.store.list("fontes"):
            self.table.insert("", "end", iid=str(source["id"]), values=(
                source["id"], source["nome"], source["tipo"], source.get("descricao", "")
            ))
        self.counter.configure(text=f"Total de fontes: {len(self.store.list('fontes'))}")
