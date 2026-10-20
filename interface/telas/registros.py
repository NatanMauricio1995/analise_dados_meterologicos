import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from ..config import BG, WHITE, BLACK, GRAY, RED
from ..services.validators import validate_record, ValidationError
from .base import page_header, field, status_label, build_table, DateTimeEntry, show_error, show_success


class RegistrosPage(tk.Frame):
    def __init__(self, parent, store, on_change=None):
        super().__init__(parent, bg=BG)
        self.store = store
        self.on_change = on_change
        self.editing_id = None
        self.fields = {}
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "Registros meteorológicos", "Registre temperatura, umidade e precipitação por ponto e fonte.")
        area = tk.Frame(self, bg=BG)
        area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        area.columnconfigure(0, weight=0, minsize=325)
        area.columnconfigure(1, weight=1)
        area.rowconfigure(0, weight=1)

        form = tk.Frame(area, bg=WHITE, highlightbackground="#E5E7EB", highlightthickness=1)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        tk.Label(form, text="Novo registro", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(15, 8))

        tk.Label(form, text="Ponto de observação *", bg=WHITE, fg="#374151", font=("Arial", 9, "bold")).pack(anchor="w", padx=16, pady=(6, 3))
        self.point_combo = ttk.Combobox(form, state="readonly", font=("Arial", 9))
        self.point_combo.pack(fill="x", padx=16, ipady=4)

        tk.Label(form, text="Fonte de dados *", bg=WHITE, fg="#374151", font=("Arial", 9, "bold")).pack(anchor="w", padx=16, pady=(8, 3))
        self.source_combo = ttk.Combobox(form, state="readonly", font=("Arial", 9))
        self.source_combo.pack(fill="x", padx=16, ipady=4)

        tk.Label(form, text="Data e hora * (DD-MM-AAAA HH:MM)", bg=WHITE, fg="#374151", font=("Arial", 9, "bold")).pack(anchor="w", padx=16, pady=(8, 3))
        date_entry = DateTimeEntry(form, font=("Arial", 10), bg="#F9FAFB", fg=BLACK, relief="solid", bd=1)
        date_entry.pack(fill="x", padx=16, ipady=6)
        self.fields["data_hora"] = date_entry
        for label, key in [
            ("Temperatura (°C) *", "temperatura"),
            ("Umidade (%) *", "umidade"),
            ("Precipitação (mm) *", "precipitacao"),
        ]:
            self.fields[key] = field(form, label)

        actions = tk.Frame(form, bg=WHITE)
        actions.pack(fill="x", padx=16, pady=12)
        self.save_button = tk.Button(actions, text="Cadastrar registro", command=self.save, bg=BLACK, fg=WHITE, relief="flat", font=("Arial", 9, "bold"), pady=9)
        self.save_button.pack(fill="x", pady=(0, 6))
        self.clear_button = tk.Button(actions, text="Limpar formulário", command=self.clear, bg="#F3F4F6", fg=BLACK, relief="flat", font=("Arial", 9), pady=8)
        self.clear_button.pack(fill="x")
        self.status = status_label(form, "Data no formato DD-MM-AAAA HH:MM. Não são aceitas datas futuras.")

        panel = tk.Frame(area, bg=WHITE, highlightbackground="#E5E7EB", highlightthickness=1)
        panel.grid(row=0, column=1, sticky="nsew")
        tk.Label(panel, text="Registros cadastrados", bg=WHITE, fg=BLACK, font=("Arial", 15, "bold")).pack(anchor="w", padx=16, pady=(18, 4))
        self.table = build_table(
            panel,
            ("id", "data", "ponto", "fonte", "temperatura", "umidade", "precipitacao"),
            {"id": "ID", "data": "Data e hora", "ponto": "Ponto", "fonte": "Fonte", "temperatura": "Temp. °C", "umidade": "Umidade %", "precipitacao": "Chuva mm"},
            {"id": 38, "data": 145, "ponto": 135, "fonte": 115, "temperatura": 80, "umidade": 80, "precipitacao": 85},
        )
        self.table.bind("<Double-1>", lambda event: self.prepare_edit())
        actions = tk.Frame(panel, bg=WHITE)
        actions.pack(fill="x", padx=14, pady=10)
        self.counter = tk.Label(actions, text="", bg=WHITE, fg=GRAY, font=("Arial", 9))
        self.counter.pack(side="left")
        tk.Button(actions, text="Editar", command=self.prepare_edit, bg="#E5E7EB", fg=BLACK, relief="flat", padx=12, pady=7).pack(side="right", padx=3)
        tk.Button(actions, text="Excluir", command=self.delete, bg="#FEE2E2", fg=RED, relief="flat", padx=12, pady=7).pack(side="right", padx=3)

    def refresh_options(self):
        self.point_map = {f'{p["id"]} - {p["nome"]}': int(p["id"]) for p in self.store.list("pontos")}
        self.source_map = {f'{s["id"]} - {s["nome"]}': int(s["id"]) for s in self.store.list("fontes")}
        self.point_combo["values"] = list(self.point_map)
        self.source_combo["values"] = list(self.source_map)

    def current_values(self):
        point_label = self.point_combo.get().strip()
        source_label = self.source_combo.get().strip()
        raw = {key: entry.get().strip() for key, entry in self.fields.items()}
        raw["ponto_observacao_id"] = self.point_map.get(point_label, "")
        raw["fonte_dados_id"] = self.source_map.get(source_label, "")
        try:
            point_ids = {int(p["id"]) for p in self.store.list("pontos")}
            source_ids = {int(s["id"]) for s in self.store.list("fontes")}
            normalized = validate_record(raw, point_ids, source_ids)
        except ValidationError as exc:
            show_error(self, self.status, str(exc))
            return None
        duplicate = any(
            int(row["ponto_observacao_id"]) == normalized["ponto_observacao_id"]
            and int(row["fonte_dados_id"]) == normalized["fonte_dados_id"]
            and row["data_hora"] == normalized["data_hora"]
            and int(row["id"]) != (self.editing_id or -1)
            for row in self.store.list("registros")
        )
        if duplicate:
            show_error(self, self.status, "Já existe um registro dessa fonte para este ponto e horário.")
            return None
        return normalized

    def save(self):
        values = self.current_values()
        if values is None:
            return
        try:
            if self.editing_id is None:
                self.store.add("registros", values)
                message = "Registro meteorológico cadastrado com sucesso."
            else:
                self.store.update("registros", self.editing_id, values)
                message = "Registro meteorológico atualizado com sucesso."
        except (OSError, KeyError) as exc:
            show_error(self, self.status, f"Não foi possível salvar o registro: {exc}")
            return
        self.clear()
        self.refresh()
        show_success(self.status, message)
        if self.on_change:
            self.on_change()

    def prepare_edit(self):
        selected = self.table.selection()
        if not selected:
            self.status.configure(text="Selecione um registro para editar.", fg=RED)
            return
        item_id = int(selected[0])
        record = next((r for r in self.store.list("registros") if int(r["id"]) == item_id), None)
        if record is None:
            return
        self.editing_id = item_id
        self.point_combo.set(next((label for label, value in self.point_map.items() if value == int(record["ponto_observacao_id"])), ""))
        self.source_combo.set(next((label for label, value in self.source_map.items() if value == int(record["fonte_dados_id"])), ""))
        for key, entry in self.fields.items():
            entry.delete(0, tk.END)
            value = record[key]
            if key == "data_hora":
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
            entry.insert(0, value)
        self.save_button.configure(text="Salvar alterações")
        self.clear_button.configure(text="Cancelar edição")
        self.status.configure(text=f"Editando o registro {item_id}.", fg="#B7791F")

    def clear(self):
        self.point_combo.set("")
        self.source_combo.set("")
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.editing_id = None
        self.save_button.configure(text="Cadastrar registro")
        self.clear_button.configure(text="Limpar formulário")
        self.status.configure(text="Todos os campos são obrigatórios. A data não pode estar no futuro.", fg=GRAY)

    def delete(self):
        selected = self.table.selection()
        if not selected:
            self.status.configure(text="Selecione um registro para excluir.", fg=RED)
            return
        item_id = int(selected[0])
        if not messagebox.askyesno("Confirmar exclusão", "Deseja realmente excluir o registro selecionado?", parent=self):
            return
        try:
            self.store.delete("registros", item_id)
        except (OSError, KeyError) as exc:
            show_error(self, self.status, f"Não foi possível excluir o registro: {exc}")
            return
        if self.editing_id == item_id:
            self.clear()
        self.refresh()
        show_success(self.status, "Registro excluído com sucesso.")
        if self.on_change:
            self.on_change()

    def refresh(self):
        self.refresh_options()
        self.table.delete(*self.table.get_children())
        points = {int(p["id"]): p["nome"] for p in self.store.list("pontos")}
        sources = {int(s["id"]): s["nome"] for s in self.store.list("fontes")}
        for row in self.store.list("registros"):
            try:
                display_date = datetime.strptime(row["data_hora"], "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y %H:%M")
            except ValueError:
                display_date = row["data_hora"]
            self.table.insert("", "end", iid=str(row["id"]), values=(
                row["id"], display_date,
                points.get(int(row["ponto_observacao_id"]), "PONTO REMOVIDO"),
                sources.get(int(row["fonte_dados_id"]), "FONTE REMOVIDA"),
                row["temperatura"], row["umidade"], row["precipitacao"]
            ))
        self.counter.configure(text=f"Total de registros: {len(self.store.list('registros'))}")
