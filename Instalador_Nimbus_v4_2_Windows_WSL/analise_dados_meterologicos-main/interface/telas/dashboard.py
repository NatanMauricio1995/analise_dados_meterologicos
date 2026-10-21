import tkinter as tk
from tkinter import ttk

from ..config import BG, WHITE, BLACK, GRAY, BORDER
from ..services.statistics import summarize
from .base import page_header, make_card, build_table


class DashboardPage(tk.Frame):
    def __init__(self, parent, store, navigate):
        super().__init__(parent, bg=BG)
        self.store = store
        self.navigate = navigate
        self._build()

    def _build(self):
        page_header(self, "Visão geral", "Resumo das observações meteorológicas cadastradas no Nimbus.")
        records = self.store.list("registros")
        stats = summarize(records)

        if stats:
            values = [
                ("Temperatura média", f'{stats["temperatura_media"]:.1f} °C', f'Mín. {stats["temperatura_minima"]:.1f} °C · Máx. {stats["temperatura_maxima"]:.1f} °C'),
                ("Umidade média", f'{stats["umidade_media"]:.1f} %', f'Mín. {stats["umidade_minima"]:.1f}% · Máx. {stats["umidade_maxima"]:.1f}%'),
                ("Precipitação total", f'{stats["precipitacao_total"]:.1f} mm' if stats["precipitacao_total"] is not None else "-- mm", "Selecione ponto e fonte nas análises" if stats["precipitacao_total"] is None else f'Maior observação {stats["precipitacao_maxima"]:.1f} mm'),
                ("Observações", str(stats["quantidade"]), "Registros armazenados"),
            ]
        else:
            values = [
                ("Temperatura média", "-- °C", "Sem observações"),
                ("Umidade média", "-- %", "Sem observações"),
                ("Precipitação total", "-- mm", "Sem observações"),
                ("Observações", "0", "Registros armazenados"),
            ]

        cards = tk.Frame(self, bg=BG)
        cards.pack(fill="x", padx=20)
        for index, (title, value, subtitle) in enumerate(values):
            card, _ = make_card(cards, title, value, subtitle)
            card.grid(row=0, column=index, padx=6, sticky="nsew")
            cards.columnconfigure(index, weight=1)

        row = tk.Frame(self, bg=BG)
        row.pack(fill="both", expand=True, padx=27, pady=18)

        chart_panel = tk.Frame(row, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        chart_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(chart_panel, text="Histórico de temperatura", bg=WHITE, fg=BLACK, font=("Arial", 13, "bold")).pack(anchor="w", padx=16, pady=(15, 2))
        tk.Label(chart_panel, text="Últimas observações cadastradas", bg=WHITE, fg=GRAY, font=("Arial", 9)).pack(anchor="w", padx=16)
        self.chart = tk.Canvas(chart_panel, bg=WHITE, highlightthickness=0, height=245)
        self.chart.pack(fill="both", expand=True, padx=12, pady=10)
        self.chart.bind("<Configure>", self.draw_chart)

        quick = tk.Frame(row, bg=WHITE, width=230, highlightbackground=BORDER, highlightthickness=1)
        quick.pack(side="right", fill="y")
        quick.pack_propagate(False)
        tk.Label(quick, text="Acesso rápido", bg=WHITE, fg=BLACK, font=("Arial", 13, "bold")).pack(anchor="w", padx=16, pady=(17, 14))
        for label, destination in [
            ("Cadastrar ponto", "Pontos de observação"),
            ("Cadastrar fonte", "Fontes de dados"),
            ("Novo registro", "Registros meteorológicos"),
            ("Importar JSON", "Importação JSON"),
            ("Análises e filtros", "Análises"),
        ]:
            tk.Button(quick, text=label, command=lambda name=destination: self.navigate(name), bg="#F3F4F6", fg=BLACK, activebackground="#E5E7EB", relief="flat", anchor="w", padx=12, pady=10).pack(fill="x", padx=12, pady=4)

        recent = tk.Frame(self, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        recent.pack(fill="x", padx=27, pady=(0, 16))
        tk.Label(recent, text="Últimas observações", bg=WHITE, fg=BLACK, font=("Arial", 12, "bold")).pack(anchor="w", padx=14, pady=(10, 4))
        points = {int(p["id"]): p["nome"] for p in self.store.list("pontos")}
        sources = {int(s["id"]): s["nome"] for s in self.store.list("fontes")}
        table = build_table(
            recent,
            ("data", "ponto", "fonte", "temperatura", "umidade", "precipitacao"),
            {"data": "Data/hora", "ponto": "Ponto", "fonte": "Fonte", "temperatura": "Temperatura °C", "umidade": "Umidade %", "precipitacao": "Precipitação mm"},
            {"data": 135, "ponto": 150, "fonte": 130, "temperatura": 110, "umidade": 100, "precipitacao": 115},
            height=4,
        )
        for record in sorted(records, key=lambda x: x["data_hora"], reverse=True)[:5]:
            table.insert("", "end", values=(
                record["data_hora"],
                points.get(int(record["ponto_observacao_id"]), "--"),
                sources.get(int(record["fonte_dados_id"]), "--"),
                record["temperatura"], record["umidade"], record["precipitacao"],
            ))

    def draw_chart(self, event=None):
        canvas = self.chart
        canvas.delete("all")
        width = max(canvas.winfo_width(), 300)
        height = max(canvas.winfo_height(), 180)
        left, right, top, bottom = 48, width - 20, 18, height - 35
        records = sorted(self.store.list("registros"), key=lambda x: x["data_hora"])[-12:]
        for step in range(5):
            y = top + (bottom - top) * step / 4
            canvas.create_line(left, y, right, y, fill="#E9EDF2", dash=(3, 3))
        if not records:
            canvas.create_text(width / 2, height / 2, text="Cadastre registros para visualizar o gráfico.", fill=GRAY, font=("Arial", 10))
            return
        values = [float(row["temperatura"]) for row in records]
        low = min(values)
        high = max(values)
        if high == low:
            high += 1
            low -= 1
        canvas.create_text(8, top, text=f"{high:.1f}°", anchor="w", fill=GRAY, font=("Arial", 8))
        canvas.create_text(8, bottom, text=f"{low:.1f}°", anchor="w", fill=GRAY, font=("Arial", 8))
        points = []
        for index, value in enumerate(values):
            x = left + (right - left) * (index / max(len(values) - 1, 1))
            y = bottom - (value - low) / (high - low) * (bottom - top)
            points.extend([x, y])
        if len(values) > 1:
            canvas.create_line(*points, fill="#475569", width=2, smooth=True)
        for index in range(len(values)):
            x, y = points[index * 2], points[index * 2 + 1]
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#171717", outline=WHITE, width=1)
