import tkinter as tk
from tkinter import ttk, messagebox

from ..config import BG, WHITE, BLACK, GRAY, BORDER, RED, GREEN
from ..services.statistics import filter_records, parse_date_range, summarize
from .base import page_header, DateEntry, make_card, build_table


class AnalisesPage(tk.Frame):
    def __init__(self, parent, store):
        super().__init__(parent, bg=BG)
        self.store = store
        self.filtered = []
        self._build()
        self.apply_filters()

    def _point_options(self, include_all=False):
        options = {}
        if include_all:
            options["Todos os pontos"] = None
        for point in self.store.list("pontos"):
            options[f'{point["id"]} - {point["nome"]}'] = int(point["id"])
        return options

    def _build(self):
        page_header(self, "Análises meteorológicas", "Filtre observações, consulte estatísticas e compare pontos ou períodos.")

        filters = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        filters.pack(fill="x", padx=22, pady=(0, 12))
        tk.Label(filters, text="Ponto de observação", bg=WHITE, fg=BLACK, font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))
        self.point_options = self._point_options(include_all=True)
        self.point_filter = ttk.Combobox(filters, state="readonly", values=list(self.point_options), width=29)
        self.point_filter.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        self.point_filter.set("Todos os pontos")

        tk.Label(filters, text="Data inicial (DD-MM-AAAA)", bg=WHITE, fg=BLACK, font=("Arial", 9, "bold")).grid(row=0, column=1, sticky="w", padx=12, pady=(10, 4))
        self.start_filter = DateEntry(filters, width=15)
        self.start_filter.grid(row=1, column=1, padx=12, pady=(0, 10), sticky="ew", ipady=5)

        tk.Label(filters, text="Data final (DD-MM-AAAA)", bg=WHITE, fg=BLACK, font=("Arial", 9, "bold")).grid(row=0, column=2, sticky="w", padx=12, pady=(10, 4))
        self.end_filter = DateEntry(filters, width=15)
        self.end_filter.grid(row=1, column=2, padx=12, pady=(0, 10), sticky="ew", ipady=5)

        tk.Button(filters, text="Aplicar filtros", command=self.apply_filters, bg=BLACK, fg=WHITE, relief="flat", padx=15, pady=8).grid(row=1, column=3, padx=12, pady=(0, 10))
        tk.Button(filters, text="Limpar", command=self.clear_filters, bg="#F3F4F6", fg=BLACK, relief="flat", padx=12, pady=8).grid(row=1, column=4, padx=(0, 12), pady=(0, 10))

        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=16, pady=(0, 10))
        card_specs = [
            ("Registros", "--"), ("Temperatura média", "-- °C"),
            ("Temperatura mínima", "-- °C"), ("Temperatura máxima", "-- °C"),
            ("Umidade média", "-- %"), ("Precipitação total", "-- mm"),
        ]
        self.card_values = []
        for index, (title, value) in enumerate(card_specs):
            card, value_label = make_card(cards, title, value)
            card.grid(row=0, column=index, padx=5, sticky="nsew")
            cards.columnconfigure(index, weight=1)
            self.card_values.append(value_label)

        tk.Label(self, text="Observações encontradas", bg=BG, fg=BLACK, font=("Arial", 12, "bold")).pack(anchor="w", padx=25, pady=(4, 2))
        self.filter_status = tk.Label(self, text="", bg=BG, fg=GRAY, font=("Arial", 9), anchor="w")
        self.filter_status.pack(fill="x", padx=25, pady=(0, 3))
        self.records_table = build_table(
            self,
            ("data", "ponto", "temperatura", "umidade", "precipitacao"),
            {"data": "Data/hora", "ponto": "Ponto de observação", "temperatura": "Temperatura °C", "umidade": "Umidade %", "precipitacao": "Precipitação mm"},
            {"data": 145, "ponto": 230, "temperatura": 130, "umidade": 120, "precipitacao": 140},
            height=5,
        )

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=22, pady=(8, 15))
        self.point_tab = tk.Frame(notebook, bg=WHITE)
        self.period_tab = tk.Frame(notebook, bg=WHITE)
        notebook.add(self.point_tab, text="Comparar pontos")
        notebook.add(self.period_tab, text="Comparar períodos")
        self._build_point_comparison()
        self._build_period_comparison()

    def clear_filters(self):
        self.point_filter.set("Todos os pontos")
        self.start_filter.delete(0, tk.END)
        self.end_filter.delete(0, tk.END)
        self.apply_filters()

    def apply_filters(self):
        try:
            start, end = parse_date_range(self.start_filter.get(), self.end_filter.get())
        except ValueError as exc:
            messagebox.showerror("Período inválido", str(exc), parent=self)
            return
        point_id = self.point_options.get(self.point_filter.get())
        self.filtered = filter_records(self.store.list("registros"), point_id, start, end)
        stats = summarize(self.filtered)
        values = ["0", "-- °C", "-- °C", "-- °C", "-- %", "-- mm"]
        if stats:
            values = [
                str(stats["quantidade"]),
                f'{stats["temperatura_media"]:.2f} °C',
                f'{stats["temperatura_minima"]:.2f} °C',
                f'{stats["temperatura_maxima"]:.2f} °C',
                f'{stats["umidade_media"]:.2f} %',
                f'{stats["precipitacao_total"]:.2f} mm',
            ]
        for label, value in zip(self.card_values, values):
            label.configure(text=value)

        if not self.filtered:
            self.filter_status.configure(text="Nenhum dado encontrado para os filtros selecionados.", fg=RED)
        else:
            self.filter_status.configure(text=f"Exibindo {len(self.filtered)} registro(s) para os filtros selecionados.", fg=GREEN)
        point_names = {int(p["id"]): p["nome"] for p in self.store.list("pontos")}
        self.records_table.delete(*self.records_table.get_children())
        for row in self.filtered:
            self.records_table.insert("", "end", values=(
                row["data_hora"], point_names.get(int(row["ponto_observacao_id"]), "--"),
                row["temperatura"], row["umidade"], row["precipitacao"],
            ))
        self.refresh_comparison_options()

    def refresh_comparison_options(self):
        self.point_options = self._point_options(include_all=True)
        options = list(self.point_options)
        for combo in (self.compare_point_a, self.compare_point_b, self.period_point):
            current = combo.get()
            combo["values"] = options
            if current in options:
                combo.set(current)
            elif options:
                combo.set(options[0])

    def _build_point_comparison(self):
        tk.Label(self.point_tab, text="Compare indicadores de dois pontos no intervalo aplicado acima.", bg=WHITE, fg=GRAY, font=("Arial", 9)).pack(anchor="w", padx=14, pady=(12, 8))
        row = tk.Frame(self.point_tab, bg=WHITE)
        row.pack(fill="x", padx=12)
        options = list(self.point_options)
        tk.Label(row, text="Ponto A", bg=WHITE, fg=BLACK).pack(side="left", padx=(0, 5))
        self.compare_point_a = ttk.Combobox(row, state="readonly", values=options, width=27)
        self.compare_point_a.pack(side="left", padx=(0, 15))
        tk.Label(row, text="Ponto B", bg=WHITE, fg=BLACK).pack(side="left", padx=(0, 5))
        self.compare_point_b = ttk.Combobox(row, state="readonly", values=options, width=27)
        self.compare_point_b.pack(side="left", padx=(0, 15))
        if options:
            self.compare_point_a.set(options[0])
            self.compare_point_b.set(options[-1])
        tk.Button(row, text="Comparar", command=self.compare_points, bg=BLACK, fg=WHITE, relief="flat", padx=14, pady=7).pack(side="left")
        self.point_comparison = tk.Label(self.point_tab, text="Selecione dois pontos para comparar.", bg=WHITE, fg=GRAY, font=("Arial", 10), justify="left", anchor="w")
        self.point_comparison.pack(fill="x", padx=14, pady=14)

    def compare_points(self):
        label_a = self.compare_point_a.get()
        label_b = self.compare_point_b.get()
        if not label_a or not label_b:
            messagebox.showwarning("Seleção necessária", "Cadastre e selecione dois pontos de observação.", parent=self)
            return
        id_a = self.point_options.get(label_a)
        id_b = self.point_options.get(label_b)
        if id_a is None or id_b is None or id_a == id_b:
            messagebox.showwarning("Pontos inválidos", "Selecione dois pontos diferentes.", parent=self)
            return
        try:
            start, end = parse_date_range(self.start_filter.get(), self.end_filter.get())
        except ValueError as exc:
            messagebox.showerror("Período inválido", str(exc), parent=self)
            return
        records = self.store.list("registros")
        stats_a = summarize(filter_records(records, id_a, start, end))
        stats_b = summarize(filter_records(records, id_b, start, end))
        point_names = {int(p["id"]): p["nome"] for p in self.store.list("pontos")}

        def line(title, stats):
            if not stats:
                return f"{title}: sem registros no período."
            return (
                f'{title}: {stats["quantidade"]} registros | '
                f'Temperatura média {stats["temperatura_media"]:.2f} °C '
                f'(mín. {stats["temperatura_minima"]:.2f} °C / máx. {stats["temperatura_maxima"]:.2f} °C) | '
                f'Umidade média {stats["umidade_media"]:.2f}% | '
                f'Precipitação total {stats["precipitacao_total"]:.2f} mm'
            )
        self.point_comparison.configure(
            text=line(point_names.get(id_a, label_a), stats_a) + "\n\n" + line(point_names.get(id_b, label_b), stats_b),
            fg=BLACK,
        )

    def _build_period_comparison(self):
        tk.Label(self.period_tab, text="Compare dois intervalos de datas para um ponto ou para todos.", bg=WHITE, fg=GRAY, font=("Arial", 9)).grid(row=0, column=0, columnspan=4, sticky="w", padx=12, pady=(12, 8))
        tk.Label(self.period_tab, text="Ponto", bg=WHITE, fg=BLACK).grid(row=1, column=0, sticky="w", padx=12)
        self.period_point = ttk.Combobox(self.period_tab, state="readonly", values=list(self.point_options), width=27)
        self.period_point.grid(row=2, column=0, sticky="w", padx=12, pady=(3, 10))
        if self.point_options:
            self.period_point.set(list(self.point_options)[0])

        date_fields = [
            ("Período A - início", 1), ("Período A - fim", 2),
            ("Período B - início", 3), ("Período B - fim", 4),
        ]
        self.period_dates = {}
        for title, column in date_fields:
            tk.Label(self.period_tab, text=title, bg=WHITE, fg=BLACK).grid(row=1, column=column, sticky="w", padx=8)
            entry = DateEntry(self.period_tab, width=14)
            entry.grid(row=2, column=column, sticky="w", padx=8, pady=(3, 10), ipady=4)
            self.period_dates[column] = entry
        tk.Button(self.period_tab, text="Comparar períodos", command=self.compare_periods, bg=BLACK, fg=WHITE, relief="flat", padx=12, pady=7).grid(row=2, column=5, padx=8)

        table_holder = tk.Frame(self.period_tab, bg=WHITE)
        table_holder.grid(row=3, column=0, columnspan=6, sticky="nsew", padx=4, pady=4)
        self.period_result = build_table(
            table_holder,
            ("periodo", "quantidade", "media", "minima", "maxima", "umidade", "precipitacao"),
            {"periodo": "Período", "quantidade": "Registros", "media": "Temp. média", "minima": "Temp. mínima", "maxima": "Temp. máxima", "umidade": "Umidade média", "precipitacao": "Precipitação total"},
            {"periodo": 100, "quantidade": 75, "media": 100, "minima": 100, "maxima": 100, "umidade": 110, "precipitacao": 130},
            height=3,
        )
        self.period_tab.columnconfigure(0, weight=1)
        self.period_tab.rowconfigure(3, weight=1)

    def compare_periods(self):
        point_id = self.point_options.get(self.period_point.get())
        periods = [
            ("Período A", self.period_dates[1].get(), self.period_dates[2].get()),
            ("Período B", self.period_dates[3].get(), self.period_dates[4].get()),
        ]
        self.period_result.delete(*self.period_result.get_children())
        for name, start_text, end_text in periods:
            if not start_text.strip() or not end_text.strip():
                messagebox.showwarning(
                    "Período incompleto",
                    f"Informe a data inicial e final de {name}.",
                    parent=self,
                )
                return
            try:
                start, end = parse_date_range(start_text, end_text)
            except ValueError as exc:
                messagebox.showerror("Período inválido", f"{name}: {exc}", parent=self)
                return
            stats = summarize(filter_records(self.store.list("registros"), point_id, start, end))
            if not stats:
                values = (name, 0, "--", "--", "--", "--", "--")
            else:
                values = (
                    name, stats["quantidade"],
                    f'{stats["temperatura_media"]:.2f} °C',
                    f'{stats["temperatura_minima"]:.2f} °C',
                    f'{stats["temperatura_maxima"]:.2f} °C',
                    f'{stats["umidade_media"]:.2f} %',
                    f'{stats["precipitacao_total"]:.2f} mm',
                )
            self.period_result.insert("", "end", values=values)
