"""Ponto de entrada e navegação da interface Nimbus."""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import os

from .config import BG, WHITE, BLACK, GRAY, BORDER
from .services.storage import DataStore
from .services.upload_server import BrowserCSVUploadServer
from .telas.base import create_table_styles
from .telas.dashboard import DashboardPage
from .telas.pontos import PontosPage
from .telas.fontes import FontesPage
from .telas.registros import RegistrosPage
from .telas.importacao_csv import CSVPage
from .telas.analises import AnalisesPage


class NimbusApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nimbus | Sistema de Análise de Dados Meteorológicos")
        self.geometry("1280x850")
        self.minsize(1080, 720)
        self.configure(bg=BG)

        self.startup_failed = False
        try:
            self.store = DataStore()
        except (OSError, ValueError) as exc:
            self.startup_failed = True
            messagebox.showerror("Falha ao carregar dados", str(exc), parent=self)
            self.after_idle(self.destroy)
            return

        self.upload_server = None
        is_codespaces = os.environ.get("CODESPACES", "").lower() == "true" or bool(os.environ.get("CODESPACE_NAME"))
        if is_codespaces:
            try:
                self.upload_server = BrowserCSVUploadServer(
                    self.store.data_dir / "importacoes",
                    host="0.0.0.0",
                    port=8765,
                ).start()
            except OSError as exc:
                messagebox.showwarning(
                    "Envio de CSV pelo navegador",
                    f"Não foi possível iniciar o portal de envio na porta 8765: {exc}. "
                    "Você ainda poderá selecionar arquivos que já estejam no Codespace.",
                    parent=self,
                )

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        create_table_styles(self)
        self.nav_buttons = {}
        self.logo_image = None
        self.current_screen = "Dashboard"
        self._build_layout()
        self.show_screen("Dashboard")

    def _build_layout(self):
        self.sidebar = tk.Frame(
            self, bg=WHITE, width=245,
            highlightbackground=BORDER, highlightthickness=1
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_path = Path(__file__).resolve().parent / "recursos" / "nimbus_logo.png"
        try:
            self.logo_image = tk.PhotoImage(file=str(logo_path))
            scale = max(1, self.logo_image.width() // 205)
            if scale > 1:
                self.logo_image = self.logo_image.subsample(scale, scale)
            tk.Label(self.sidebar, image=self.logo_image, bg=WHITE).pack(pady=(14, 2))
        except tk.TclError:
            tk.Label(self.sidebar, text="NIMBUS", bg=WHITE, fg=BLACK, font=("Arial", 24, "bold")).pack(pady=30)

        tk.Label(
            self.sidebar, text="SISTEMA DE ANÁLISE METEOROLÓGICA",
            bg=WHITE, fg=GRAY, font=("Arial", 8, "bold")
        ).pack(pady=(0, 24))
        tk.Label(
            self.sidebar, text="MENU PRINCIPAL", bg=WHITE,
            fg="#9CA3AF", font=("Arial", 8, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 9))

        options = [
            "Dashboard", "Pontos de observação", "Fontes de dados",
            "Registros meteorológicos", "Importação CSV", "Análises",
        ]
        for name in options:
            button = tk.Button(
                self.sidebar, text=name,
                command=lambda screen=name: self.show_screen(screen),
                font=("Arial", 10), bg=WHITE, fg=GRAY,
                activebackground="#EEEEF0", activeforeground=BLACK,
                relief="flat", bd=0, anchor="w", padx=18, pady=13,
                cursor="hand2"
            )
            button.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[name] = button

        footer = tk.Frame(self.sidebar, bg="#F9FAFB")
        footer.pack(side="bottom", fill="x", padx=12, pady=14)
        tk.Label(
            footer, text="●  MODO LOCAL (JSON)", bg="#F9FAFB",
            fg="#B7791F", font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 4))
        tk.Label(
            footer, text="Aguardando integração com a API", bg="#F9FAFB",
            fg=GRAY, font=("Arial", 8)
        ).pack(anchor="w", padx=10, pady=(0, 10))

        self.main_area = tk.Frame(self, bg=BG)
        self.main_area.pack(side="right", fill="both", expand=True)

        header = tk.Frame(
            self.main_area, bg=WHITE, height=62,
            highlightbackground=BORDER, highlightthickness=1
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Nimbus", bg=WHITE, fg=BLACK,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=26)
        tk.Label(
            header, text="SISTEMA DE MONITORAMENTO", bg=WHITE,
            fg=GRAY, font=("Arial", 8, "bold")
        ).pack(side="right", padx=24)

        self.content = tk.Frame(self.main_area, bg=BG)
        self.content.pack(fill="both", expand=True)

    def _update_navigation(self, selected):
        for name, button in self.nav_buttons.items():
            active = name == selected
            button.configure(
                bg=BLACK if active else WHITE,
                fg=WHITE if active else GRAY,
                activebackground=BLACK if active else "#EEEEF0",
                activeforeground=WHITE if active else BLACK,
            )

    def show_screen(self, name):
        self.current_screen = name
        self._update_navigation(name)
        for child in self.content.winfo_children():
            child.destroy()

        screens = {
            "Dashboard": lambda: DashboardPage(self.content, self.store, self.show_screen),
            "Pontos de observação": lambda: PontosPage(self.content, self.store),
            "Fontes de dados": lambda: FontesPage(self.content, self.store),
            "Registros meteorológicos": lambda: RegistrosPage(self.content, self.store),
            "Importação CSV": lambda: CSVPage(
                self.content, self.store, browser_upload_enabled=self.upload_server is not None
            ),
            "Análises": lambda: AnalisesPage(self.content, self.store),
        }
        screen = screens[name]()
        screen.pack(fill="both", expand=True)

    def _on_close(self):
        if self.upload_server is not None:
            self.upload_server.stop()
        self.destroy()


def main():
    app = NimbusApp()
    if not app.startup_failed:
        app.mainloop()


if __name__ == "__main__":
    main()
