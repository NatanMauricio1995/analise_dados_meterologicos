"""Componentes reutilizáveis das telas Tkinter."""

import tkinter as tk
from tkinter import ttk

from ..config import BG, WHITE, BLACK, GRAY, BORDER


def page_header(parent, title, subtitle):
    tk.Label(
        parent, text=title, bg=BG, fg=BLACK,
        font=("Arial", 23, "bold")
    ).pack(anchor="w", padx=25, pady=(22, 4))
    tk.Label(
        parent, text=subtitle, bg=BG, fg=GRAY,
        font=("Arial", 10)
    ).pack(anchor="w", padx=26, pady=(0, 18))


def field(parent, label, width=None):
    tk.Label(
        parent, text=label, bg=WHITE, fg="#374151",
        font=("Arial", 9, "bold")
    ).pack(anchor="w", padx=16, pady=(7, 3))
    widget = tk.Entry(
        parent, width=width,
        font=("Arial", 10), bg="#F9FAFB", fg=BLACK,
        relief="solid", bd=1
    )
    widget.pack(fill="x", padx=16, ipady=6)
    return widget


def status_label(parent, text=""):
    label = tk.Label(
        parent, text=text, bg=WHITE, fg=GRAY,
        font=("Arial", 8), wraplength=280, justify="left"
    )
    label.pack(anchor="w", padx=16, pady=(0, 10))
    return label


def show_error(parent, status, message):
    from tkinter import messagebox
    status.configure(text=message, fg="#DC2626")
    messagebox.showerror("Dados inválidos", message, parent=parent.winfo_toplevel())


def show_success(status, message):
    status.configure(text=message, fg="#15803D")


def build_table(parent, columns, headings, widths, height=12):
    wrapper = tk.Frame(parent, bg=WHITE)
    wrapper.pack(fill="both", expand=True, padx=12, pady=5)

    table = ttk.Treeview(
        wrapper, columns=columns, show="headings", height=height
    )
    for column in columns:
        table.heading(column, text=headings.get(column, column))
        table.column(
            column, width=widths.get(column, 100),
            anchor="center", stretch=True
        )

    vertical = ttk.Scrollbar(
        wrapper, orient="vertical", command=table.yview
    )
    horizontal = ttk.Scrollbar(
        wrapper, orient="horizontal", command=table.xview
    )
    table.configure(
        yscrollcommand=vertical.set,
        xscrollcommand=horizontal.set
    )
    table.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")
    wrapper.rowconfigure(0, weight=1)
    wrapper.columnconfigure(0, weight=1)
    return table


def create_table_styles(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "Treeview", background=WHITE, fieldbackground=WHITE,
        foreground=BLACK, rowheight=29, font=("Arial", 9)
    )
    style.configure(
        "Treeview.Heading", background="#F3F4F6",
        foreground=BLACK, font=("Arial", 9, "bold")
    )
    style.map("Treeview", background=[("selected", "#DCE4EE")], foreground=[("selected", BLACK)])


class DateTimeEntry(tk.Entry):
    """Entrada que formata 12 dígitos como DD-MM-AAAA HH:MM."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<KeyRelease>", self._format)

    def _format(self, event=None):
        if event and event.keysym in {
            "Left", "Right", "Home", "End", "Tab", "Shift_L",
            "Shift_R", "Control_L", "Control_R", "Escape"
        }:
            return
        raw = "".join(ch for ch in self.get() if ch.isdigit())[:12]
        parts = []
        if len(raw) > 0:
            parts.append(raw[:2])
        if len(raw) > 2:
            parts.append(raw[2:4])
        if len(raw) > 4:
            parts.append(raw[4:8])
        if len(raw) > 8:
            parts.append(raw[8:10])
        formatted = ""
        if len(parts) >= 1:
            formatted = parts[0]
        if len(parts) >= 2:
            formatted += "-" + parts[1]
        if len(parts) >= 3:
            formatted += "-" + parts[2]
        if len(parts) >= 4:
            formatted += " " + parts[3]
        if len(raw) > 10:
            formatted += ":" + raw[10:12]
        if formatted != self.get():
            self.delete(0, tk.END)
            self.insert(0, formatted)
            self.icursor(tk.END)


class DateEntry(tk.Entry):
    """Entrada que formata 8 dígitos como DD-MM-AAAA."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind("<KeyRelease>", self._format)

    def _format(self, event=None):
        if event and event.keysym in {
            "Left", "Right", "Home", "End", "Tab", "Shift_L",
            "Shift_R", "Control_L", "Control_R", "Escape"
        }:
            return
        raw = "".join(ch for ch in self.get() if ch.isdigit())[:8]
        formatted = raw
        if len(raw) > 2:
            formatted = raw[:2] + "-" + raw[2:]
        if len(raw) > 4:
            formatted = raw[:2] + "-" + raw[2:4] + "-" + raw[4:]
        if formatted != self.get():
            self.delete(0, tk.END)
            self.insert(0, formatted)
            self.icursor(tk.END)


def make_card(parent, title, value, subtitle=""):
    card = tk.Frame(
        parent, bg=WHITE, highlightbackground=BORDER,
        highlightthickness=1
    )
    tk.Label(
        card, text=title.upper(), bg=WHITE, fg=GRAY,
        font=("Arial", 8, "bold")
    ).pack(anchor="w", padx=14, pady=(14, 7))
    value_label = tk.Label(
        card, text=value, bg=WHITE, fg=BLACK,
        font=("Arial", 21, "bold")
    )
    value_label.pack(anchor="w", padx=14)
    tk.Label(
        card, text=subtitle, bg=WHITE, fg=GRAY,
        font=("Arial", 8)
    ).pack(anchor="w", padx=14, pady=(5, 14))
    return card, value_label
