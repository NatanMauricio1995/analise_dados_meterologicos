import tkinter as tk
from tkinter import messagebox

from ..config import BG, WHITE, BLACK, GRAY, RED, GREEN, BORDER
from ..services.validators import validate_point, ValidationError
from .base import page_header, field, status_label, build_table, show_error, show_success


class PontosPage(tk.Frame):
    def __init__(self, parent, store, on_change=None):
        super().__init__(parent, bg=BG)
        self.store = store
        self.on_change = on_change
        self.editing_id = None
        self.fields = {}
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "Pontos de observação", "Cadastre, consulte, edite e exclua locais de monitoramento meteorológico.")
        area = tk.Frame(self, bg=BG)
        area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        area.columnconfigure(0, weight=0, minsize=300)
        area.columnconfigure(1, weight=1)
        area.rowconfigure(0, weight=1)

        form = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tk.Label(form, text="Dados do ponto", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(18, 8))
        for label, key in [
            ("Nome do ponto *", "nome"), ("Latitude *", "latitude"),
            ("Longitude *", "longitude"), ("Cidade (opcional)", "cidade"),
            ("Estado (UF opcional)", "estado")
        ]:
            self.fields[key] = field(form, label)
        buttons = tk.Frame(form, bg=WHITE)
        buttons.pack(fill="x", padx=16, pady=14)
        self.save_button = tk.Button(buttons, text="Cadastrar ponto", command=self.save, bg=BLACK, fg=WHITE, relief="flat", pady=9)
        self.save_button.pack(fill="x", pady=(0, 6))
        self.clear_button = tk.Button(buttons, text="Limpar formulário", command=self.clear, bg="#F3F4F6", fg=BLACK, relief="flat", pady=8)
        self.clear_button.pack(fill="x")
        self.status = status_label(form, "Nome e coordenadas são obrigatórios. Cidade e UF são opcionais.")

        panel = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew")
        tk.Label(panel, text="Pontos cadastrados", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        self.table = build_table(panel, ("id", "nome", "latitude", "longitude", "cidade", "estado"),
                                 {"id": "ID", "nome": "Ponto", "latitude": "Latitude", "longitude": "Longitude", "cidade": "Cidade", "estado": "UF"},
                                 {"id": 42, "nome": 160, "latitude": 90, "longitude": 90, "cidade": 130, "estado": 45})
        self.table.bind("<Double-1>", lambda event: self.prepare_edit())
        actions = tk.Frame(panel, bg=WHITE)
        actions.pack(fill="x", padx=14, pady=10)
        self.counter = tk.Label(actions, text="", bg=WHITE, fg=GRAY, font=("Arial", 9))
        self.counter.pack(side="left")
        tk.Button(actions, text="Editar", command=self.prepare_edit, bg="#E5E7EB", fg=BLACK, relief="flat", padx=12, pady=7).pack(side="right", padx=3)
        tk.Button(actions, text="Excluir", command=self.delete, bg="#FEE2E2", fg=RED, relief="flat", padx=12, pady=7).pack(side="right", padx=3)

    def values(self):
        raw = {key: entry.get() for key, entry in self.fields.items()}
        try:
            return validate_point(raw)
        except ValidationError as exc:
            show_error(self, self.status, str(exc))
            return None

    def save(self):
        values = self.values()
        if values is None:
            return
        try:
            if self.editing_id is None:
                self.store.add("pontos", values)
                message = "Ponto cadastrado com sucesso."
            else:
                self.store.update("pontos", self.editing_id, values)
                message = "Ponto atualizado com sucesso."
        except (OSError, KeyError, ValueError, ConnectionError) as exc:
            show_error(self, self.status, f"Não foi possível salvar o ponto: {exc}")
            return
        self.clear()
        self.refresh()
        show_success(self.status, message)
        if self.on_change:
            self.on_change()

    def prepare_edit(self):
        selected = self.table.selection()
        if not selected:
            self.status.configure(text="Selecione um ponto para editar.", fg=RED)
            return
        item_id = int(selected[0])
        point = next((row for row in self.store.list("pontos") if int(row["id"]) == item_id), None)
        if point is None:
            return
        self.editing_id = item_id
        for key, entry in self.fields.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(point.get(key) or ""))
        self.save_button.configure(text="Salvar alterações")
        self.clear_button.configure(text="Cancelar edição")
        self.status.configure(text=f"Editando o ponto {item_id}.", fg="#B7791F")

    def clear(self):
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.editing_id = None
        self.save_button.configure(text="Cadastrar ponto")
        self.clear_button.configure(text="Limpar formulário")
        self.status.configure(text="Nome e coordenadas são obrigatórios. Cidade e UF são opcionais.", fg=GRAY)

    def delete(self):
        selected = self.table.selection()
        if not selected:
            self.status.configure(text="Selecione um ponto para excluir.", fg=RED)
            return
        item_id = int(selected[0])
        if any(int(row["ponto_observacao_id"]) == item_id for row in self.store.list("registros")):
            show_error(self, self.status, "Este ponto possui registros meteorológicos associados e não pode ser excluído.")
            return
        if not messagebox.askyesno("Confirmar exclusão", "Deseja realmente excluir o ponto selecionado?", parent=self):
            return
        try:
            self.store.delete("pontos", item_id)
        except (OSError, KeyError, ValueError, ConnectionError) as exc:
            show_error(self, self.status, f"Não foi possível excluir o ponto: {exc}")
            return
        if self.editing_id == item_id:
            self.clear()
        self.refresh()
        show_success(self.status, "Ponto excluído com sucesso.")
        if self.on_change:
            self.on_change()

    def refresh(self):
        self.table.delete(*self.table.get_children())
        for point in self.store.list("pontos"):
            self.table.insert("", "end", iid=str(point["id"]), values=(
                point["id"], point["nome"], point["latitude"],
                point["longitude"], point["cidade"], point["estado"]
            ))
        self.counter.configure(text=f"Total de pontos: {len(self.store.list('pontos'))}")
