import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import math
import os


BG = "#F4F5F7"
WHITE = "#FFFFFF"
BLACK = "#171717"
GRAY = "#6B7280"
BORDER = "#E5E7EB"
RED = "#B91C1C"
GREEN = "#15803D"


class NimbusApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Nimbus | Análise Meteorológica")
        self.geometry("1250x780")
        self.minsize(1050, 680)
        self.configure(bg=BG)

        self.pasta = os.path.dirname(os.path.abspath(__file__))

        self.arquivos = {
            "pontos": os.path.join(self.pasta, "pontos_observacao.json"),
            "fontes": os.path.join(self.pasta, "fontes_dados.json"),
            "registros": os.path.join(self.pasta, "registros_meteorologicos.json")
        }

        self.pontos = self.carregar_dados("pontos")
        self.fontes = self.carregar_dados("fontes")
        self.registros = self.carregar_dados("registros")

        self.proximo_id_ponto = self.proximo_id(self.pontos)
        self.proximo_id_fonte = self.proximo_id(self.fontes)
        self.proximo_id_registro = self.proximo_id(self.registros)

        self.id_ponto_edicao = None
        self.id_fonte_edicao = None
        self.id_registro_edicao = None

        self.nav_buttons = {}
        self.logo_image = None

        self.criar_layout()
        self.mostrar_tela("Dashboard")

    # ARMAZENAMENTO LOCAL PARA TESTES

    def carregar_dados(self, entidade):
        try:
            with open(self.arquivos[entidade], "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
                return dados if isinstance(dados, list) else []
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            return []

    def salvar_dados(self, entidade):
        temporario = self.arquivos[entidade] + ".tmp"
        try:
            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(
                    getattr(self, entidade),
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )
            os.replace(temporario, self.arquivos[entidade])
            return True
        except OSError:
            try:
                if os.path.exists(temporario):
                    os.remove(temporario)
            except OSError:
                pass
            return False

    def proximo_id(self, dados):
        return max((int(item.get("id", 0)) for item in dados), default=0) + 1

    # ESTRUTURA PRINCIPAL

    def criar_layout(self):
        self.menu = tk.Frame(
            self,
            bg=WHITE,
            width=245,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        self.menu.pack(side="left", fill="y")
        self.menu.pack_propagate(False)

        caminho_logo = os.path.join(self.pasta, "nimbus_logo.png")
        try:
            self.logo_image = tk.PhotoImage(file=caminho_logo).subsample(2, 2)
            tk.Label(self.menu, image=self.logo_image, bg=WHITE).pack(pady=(12, 0))
        except tk.TclError:
            tk.Label(
                self.menu,
                text="NIMBUS",
                bg=WHITE,
                fg=BLACK,
                font=("Arial", 23, "bold")
            ).pack(pady=35)

        tk.Label(
            self.menu,
            text="SISTEMA DE ANÁLISE METEOROLÓGICA",
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 8, "bold")
        ).pack(pady=(0, 25))

        tk.Label(
            self.menu,
            text="MENU PRINCIPAL",
            bg=WHITE,
            fg="#9CA3AF",
            font=("Arial", 8, "bold")
        ).pack(anchor="w", padx=20, pady=(0, 10))

        opcoes = [
            "Dashboard",
            "Pontos de observação",
            "Fontes de dados",
            "Registros meteorológicos",
            "Importação CSV"
        ]

        for opcao in opcoes:
            botao = tk.Button(
                self.menu,
                text=opcao,
                command=lambda nome=opcao: self.mostrar_tela(nome),
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY,
                activebackground="#EEEEF0",
                activeforeground=BLACK,
                relief="flat",
                bd=0,
                anchor="w",
                padx=18,
                pady=14,
                cursor="hand2"
            )
            botao.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[opcao] = botao

        rodape = tk.Frame(self.menu, bg="#F9FAFB")
        rodape.pack(side="bottom", fill="x", padx=12, pady=15)

        tk.Label(
            rodape,
            text="●  API aguardando integração",
            bg="#F9FAFB",
            fg="#B7791F",
            font=("Arial", 9)
        ).pack(anchor="w", padx=10, pady=12)

        tk.Label(
            rodape,
            text="Nimbus | Projeto PAV",
            bg="#F9FAFB",
            fg=GRAY,
            font=("Arial", 8)
        ).pack(anchor="w", padx=10, pady=(0, 10))

        self.area_principal = tk.Frame(self, bg=BG)
        self.area_principal.pack(side="right", fill="both", expand=True)

        cabecalho = tk.Frame(
            self.area_principal,
            bg=WHITE,
            height=65,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        cabecalho.pack(fill="x")
        cabecalho.pack_propagate(False)

        tk.Label(
            cabecalho,
            text="Nimbus",
            bg=WHITE,
            fg=BLACK,
            font=("Arial", 13, "bold")
        ).pack(side="left", padx=28)

        tk.Label(
            cabecalho,
            text="SISTEMA DE MONITORAMENTO",
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 8, "bold")
        ).pack(side="right", padx=25)

        self.conteudo = tk.Frame(self.area_principal, bg=BG)
        self.conteudo.pack(fill="both", expand=True)

    def limpar_conteudo(self):
        for widget in self.conteudo.winfo_children():
            widget.destroy()

    def atualizar_menu(self, selecionado):
        for nome, botao in self.nav_buttons.items():
            if nome == selecionado:
                botao.configure(
                    bg=BLACK,
                    fg=WHITE,
                    activebackground=BLACK,
                    activeforeground=WHITE
                )
            else:
                botao.configure(
                    bg=WHITE,
                    fg=GRAY,
                    activebackground="#EEEEF0",
                    activeforeground=BLACK
                )

    def mostrar_tela(self, nome):
        self.limpar_conteudo()
        self.atualizar_menu(nome)

        if nome == "Dashboard":
            self.criar_dashboard()
        elif nome == "Pontos de observação":
            self.criar_tela_pontos()
        elif nome == "Fontes de dados":
            self.criar_tela_fontes()
        elif nome == "Registros meteorológicos":
            self.criar_tela_registros()
        else:
            self.criar_tela_csv()

    # COMPONENTES REUTILIZÁVEIS

    def titulo_pagina(self, titulo, descricao):
        tk.Label(
            self.conteudo,
            text=titulo,
            bg=BG,
            fg=BLACK,
            font=("Arial", 23, "bold")
        ).pack(anchor="w", padx=25, pady=(22, 4))

        tk.Label(
            self.conteudo,
            text=descricao,
            bg=BG,
            fg=GRAY,
            font=("Arial", 10)
        ).pack(anchor="w", padx=26, pady=(0, 18))

    def criar_entrada(self, pai, rotulo, chave, dicionario):
        tk.Label(
            pai,
            text=rotulo,
            bg=WHITE,
            fg="#374151",
            font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=16, pady=(7, 3))

        entrada = tk.Entry(
            pai,
            font=("Arial", 10),
            bg="#F9FAFB",
            fg=BLACK,
            relief="solid",
            bd=1
        )
        entrada.pack(fill="x", padx=16, ipady=6)
        dicionario[chave] = entrada
        return entrada

    def criar_status(self, pai, texto):
        status = tk.Label(
            pai,
            text=texto,
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 8),
            wraplength=275,
            justify="left"
        )
        status.pack(anchor="w", padx=16, pady=(0, 10))
        return status

    def mensagem_erro(self, status, mensagem):
        status.configure(text=mensagem, fg="#DC2626")
        messagebox.showerror("Dados inválidos", mensagem, parent=self)

    def mensagem_sucesso(self, status, mensagem):
        status.configure(text=mensagem, fg=GREEN)

    def criar_tabela(self, pai, colunas, titulos, larguras):
        moldura = tk.Frame(pai, bg=WHITE)
        moldura.pack(fill="both", expand=True, padx=12, pady=5)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "Treeview",
            background=WHITE,
            fieldbackground=WHITE,
            foreground=BLACK,
            rowheight=30,
            font=("Arial", 9)
        )
        estilo.configure(
            "Treeview.Heading",
            background="#F3F4F6",
            foreground=BLACK,
            font=("Arial", 9, "bold")
        )

        tabela = ttk.Treeview(
            moldura,
            columns=colunas,
            show="headings",
            height=12
        )

        for coluna in colunas:
            tabela.heading(coluna, text=titulos[coluna])
            tabela.column(
                coluna,
                width=larguras.get(coluna, 100),
                anchor="center"
            )

        barra = ttk.Scrollbar(
            moldura,
            orient="vertical",
            command=tabela.yview
        )
        tabela.configure(yscrollcommand=barra.set)
        tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabela

    def atualizar_contador(self, label, entidade, nome):
        label.configure(
            text=f"Total de {nome}: {len(entidade)}"
        )

    def converter_numero(self, valor):
        numero = float(valor.strip().replace(",", "."))
        if not math.isfinite(numero):
            raise ValueError
        return numero

    # DASHBOARD

    def criar_dashboard(self):
        self.titulo_pagina(
            "Visão geral",
            "Acompanhe os dados e indicadores meteorológicos."
        )

        if self.registros:
            temperaturas = [float(r["temperatura"]) for r in self.registros]
            umidades = [float(r["umidade"]) for r in self.registros]
            precipitacoes = [float(r["precipitacao"]) for r in self.registros]

            temp_media = f"{sum(temperaturas) / len(temperaturas):.1f} °C"
            umid_media = f"{sum(umidades) / len(umidades):.1f} %"
            precip_total = f"{sum(precipitacoes):.1f} mm"
        else:
            temp_media = "-- °C"
            umid_media = "-- %"
            precip_total = "-- mm"

        indicadores = [
            ("TEMPERATURA MÉDIA", temp_media),
            ("UMIDADE MÉDIA", umid_media),
            ("PRECIPITAÇÃO TOTAL", precip_total),
            ("REGISTROS", str(len(self.registros)))
        ]

        cards = tk.Frame(self.conteudo, bg=BG)
        cards.pack(fill="x", padx=20)

        for indice, (titulo, valor) in enumerate(indicadores):
            card = tk.Frame(
                cards,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1
            )
            card.grid(row=0, column=indice, padx=7, sticky="nsew")

            tk.Label(
                card,
                text=titulo,
                bg=WHITE,
                fg=GRAY,
                font=("Arial", 8, "bold")
            ).pack(anchor="w", padx=13, pady=(17, 9))

            tk.Label(
                card,
                text=valor,
                bg=WHITE,
                fg=BLACK,
                font=("Arial", 21, "bold")
            ).pack(anchor="w", padx=13, pady=(0, 17))

            cards.grid_columnconfigure(indice, weight=1)

        painel = tk.Frame(
            self.conteudo,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        painel.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(
            painel,
            text="Bem-vindo ao Nimbus!",
            bg=WHITE,
            fg=BLACK,
            font=("Arial", 18, "bold")
        ).pack(anchor="w", padx=25, pady=(25, 10))

        tk.Label(
            painel,
            text=(
                f"Pontos de observação cadastrados: {len(self.pontos)}\n"
                f"Fontes de dados cadastradas: {len(self.fontes)}\n"
                f"Registros meteorológicos cadastrados: {len(self.registros)}\n\n"
                "As estatísticas são calculadas a partir dos registros armazenados."
            ),
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 11),
            justify="left"
        ).pack(anchor="w", padx=25)

    # PONTOS DE OBSERVAÇÃO

    def criar_tela_pontos(self):
        self.titulo_pagina(
            "Pontos de observação",
            "Cadastre, consulte, edite e exclua locais de monitoramento."
        )

        area = tk.Frame(self.conteudo, bg=BG)
        area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        area.grid_columnconfigure(0, weight=0, minsize=300)
        area.grid_columnconfigure(1, weight=1)
        area.grid_rowconfigure(0, weight=1)

        formulario = tk.Frame(
            area, bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            formulario, text="Dados do ponto",
            bg=WHITE, fg=BLACK,
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 8))

        self.campos_ponto = {}
        campos = [
            ("Nome do ponto *", "nome"),
            ("Latitude *", "latitude"),
            ("Longitude *", "longitude"),
            ("Cidade *", "cidade"),
            ("Estado (UF) *", "estado")
        ]

        for rotulo, chave in campos:
            self.criar_entrada(formulario, rotulo, chave, self.campos_ponto)

        botoes = tk.Frame(formulario, bg=WHITE)
        botoes.pack(fill="x", padx=16, pady=14)

        self.botao_ponto_salvar = tk.Button(
            botoes, text="Cadastrar ponto",
            command=self.salvar_ponto,
            bg=BLACK, fg=WHITE, relief="flat",
            font=("Arial", 9, "bold"), pady=9
        )
        self.botao_ponto_salvar.pack(fill="x", pady=(0, 6))

        self.botao_ponto_limpar = tk.Button(
            botoes, text="Limpar formulário",
            command=self.limpar_formulario_ponto,
            bg="#F3F4F6", fg=BLACK, relief="flat",
            font=("Arial", 9), pady=8
        )
        self.botao_ponto_limpar.pack(fill="x")

        self.status_ponto = self.criar_status(
            formulario, "* Todos os campos são obrigatórios."
        )

        tabela_painel = tk.Frame(
            area, bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        tabela_painel.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            tabela_painel, text="Pontos cadastrados",
            bg=WHITE, fg=BLACK,
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 4))

        self.tabela_pontos = self.criar_tabela(
            tabela_painel,
            ("id", "nome", "latitude", "longitude", "cidade", "estado"),
            {
                "id": "ID", "nome": "Ponto", "latitude": "Latitude",
                "longitude": "Longitude", "cidade": "Cidade", "estado": "UF"
            },
            {
                "id": 40, "nome": 130, "latitude": 85,
                "longitude": 85, "cidade": 100, "estado": 45
            }
        )

        self.tabela_pontos.bind(
            "<Double-1>", lambda evento: self.preparar_edicao_ponto()
        )

        self.contador_pontos = tk.Label(
            tabela_painel,
            text="",
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 9)
        )
        self.contador_pontos.pack(side="left", padx=15, pady=12)

        botoes_tabela = tk.Frame(tabela_painel, bg=WHITE)
        botoes_tabela.pack(side="right", padx=12, pady=8)

        tk.Button(
            botoes_tabela, text="Editar selecionado",
            command=self.preparar_edicao_ponto,
            bg="#E5E7EB", fg=BLACK, relief="flat",
            padx=9, pady=8
        ).pack(side="left", padx=3)

        tk.Button(
            botoes_tabela, text="Excluir selecionado",
            command=self.excluir_ponto,
            bg="#FEE2E2", fg=RED, relief="flat",
            padx=9, pady=8
        ).pack(side="left", padx=3)

        self.atualizar_tabela_pontos()

    def dados_validos_ponto(self):
        valores = {k: v.get().strip() for k, v in self.campos_ponto.items()}

        if any(not valor for valor in valores.values()):
            self.mensagem_erro(self.status_ponto, "Todos os campos são obrigatórios.")
            return None

        try:
            latitude = self.converter_numero(valores["latitude"])
            longitude = self.converter_numero(valores["longitude"])
        except ValueError:
            self.mensagem_erro(
                self.status_ponto,
                "Latitude e longitude devem conter apenas números válidos."
            )
            return None

        if not -90 <= latitude <= 90:
            self.mensagem_erro(self.status_ponto, "Latitude inválida: utilize um valor entre -90 e 90.")
            return None

        if not -180 <= longitude <= 180:
            self.mensagem_erro(self.status_ponto, "Longitude inválida: utilize um valor entre -180 e 180.")
            return None

        estado = valores["estado"].upper()
        if len(estado) != 2 or not estado.isascii() or not estado.isalpha():
            self.mensagem_erro(self.status_ponto, "Estado inválido: informe uma sigla de duas letras, como RJ.")
            return None

        return {
            "nome": valores["nome"].upper(),
            "latitude": f"{latitude:.4f}",
            "longitude": f"{longitude:.4f}",
            "cidade": valores["cidade"].upper(),
            "estado": estado
        }

    def salvar_ponto(self):
        dados = self.dados_validos_ponto()
        if dados is None:
            return

        if self.id_ponto_edicao is None:
            ponto = {"id": self.proximo_id_ponto, **dados}
            self.pontos.append(ponto)
            if not self.salvar_dados("pontos"):
                self.pontos.pop()
                self.mensagem_erro(self.status_ponto, "Não foi possível salvar o ponto.")
                return
            self.proximo_id_ponto += 1
            mensagem = "Ponto cadastrado com sucesso!"
        else:
            indice = next(
                (i for i, p in enumerate(self.pontos) if int(p["id"]) == self.id_ponto_edicao),
                None
            )
            if indice is None:
                self.mensagem_erro(self.status_ponto, "Ponto não encontrado.")
                return
            anterior = self.pontos[indice].copy()
            self.pontos[indice] = {"id": self.id_ponto_edicao, **dados}
            if not self.salvar_dados("pontos"):
                self.pontos[indice] = anterior
                self.mensagem_erro(self.status_ponto, "Não foi possível salvar as alterações.")
                return
            mensagem = "Ponto atualizado com sucesso!"

        self.atualizar_tabela_pontos()
        self.limpar_formulario_ponto()
        self.status_ponto.configure(text=mensagem, fg=GREEN)

    def preparar_edicao_ponto(self):
        selecionados = self.tabela_pontos.selection()
        if not selecionados:
            self.status_ponto.configure(text="Selecione um ponto para editar.", fg=RED)
            return

        ponto_id = int(selecionados[0])
        ponto = next((p for p in self.pontos if int(p["id"]) == ponto_id), None)
        if ponto is None:
            return

        self.id_ponto_edicao = ponto_id
        for chave, entrada in self.campos_ponto.items():
            entrada.delete(0, tk.END)
            entrada.insert(0, ponto[chave])

        self.botao_ponto_salvar.configure(text="Salvar alterações")
        self.botao_ponto_limpar.configure(text="Cancelar edição")
        self.status_ponto.configure(text=f"Editando o ponto {ponto_id}.", fg="#B7791F")

    def limpar_formulario_ponto(self):
        for entrada in self.campos_ponto.values():
            entrada.delete(0, tk.END)
        self.id_ponto_edicao = None
        self.botao_ponto_salvar.configure(text="Cadastrar ponto")
        self.botao_ponto_limpar.configure(text="Limpar formulário")
        self.status_ponto.configure(text="* Todos os campos são obrigatórios.", fg=GRAY)

    def excluir_ponto(self):
        selecionados = self.tabela_pontos.selection()
        if not selecionados:
            self.status_ponto.configure(text="Selecione um ponto para excluir.", fg=RED)
            return

        ponto_id = int(selecionados[0])
        associado = any(
            int(registro["ponto_observacao_id"]) == ponto_id
            for registro in self.registros
        )

        if associado:
            messagebox.showerror(
                "Exclusão não permitida",
                "Este ponto possui registros meteorológicos associados e não pode ser excluído.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir o ponto selecionado?",
            parent=self
        ):
            return

        indice = next((i for i, p in enumerate(self.pontos) if int(p["id"]) == ponto_id), None)
        if indice is None:
            return

        removido = self.pontos.pop(indice)
        if not self.salvar_dados("pontos"):
            self.pontos.insert(indice, removido)
            self.mensagem_erro(self.status_ponto, "Não foi possível salvar a exclusão.")
            return

        if self.id_ponto_edicao == ponto_id:
            self.limpar_formulario_ponto()

        self.atualizar_tabela_pontos()
        self.status_ponto.configure(text="Ponto excluído com sucesso!", fg=GREEN)

    def atualizar_tabela_pontos(self):
        for item in self.tabela_pontos.get_children():
            self.tabela_pontos.delete(item)

        for ponto in self.pontos:
            self.tabela_pontos.insert(
                "", "end", iid=str(ponto["id"]),
                values=(
                    ponto["id"], ponto["nome"], ponto["latitude"],
                    ponto["longitude"], ponto["cidade"], ponto["estado"]
                )
            )

        self.atualizar_contador(self.contador_pontos, self.pontos, "pontos")

    # FONTES DE DADOS

    def criar_tela_fontes(self):
        self.titulo_pagina(
            "Fontes de dados",
            "Cadastre e gerencie as origens das observações meteorológicas."
        )

        area = tk.Frame(self.conteudo, bg=BG)
        area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        area.grid_columnconfigure(0, weight=0, minsize=300)
        area.grid_columnconfigure(1, weight=1)
        area.grid_rowconfigure(0, weight=1)

        formulario = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            formulario, text="Dados da fonte",
            bg=WHITE, fg=BLACK,
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 8))

        self.campos_fonte = {}
        self.criar_entrada(formulario, "Nome da fonte *", "nome", self.campos_fonte)
        self.criar_entrada(formulario, "Tipo da fonte *", "tipo", self.campos_fonte)
        self.criar_entrada(formulario, "Descrição (opcional)", "descricao", self.campos_fonte)

        botoes = tk.Frame(formulario, bg=WHITE)
        botoes.pack(fill="x", padx=16, pady=14)

        self.botao_fonte_salvar = tk.Button(
            botoes, text="Cadastrar fonte",
            command=self.salvar_fonte,
            bg=BLACK, fg=WHITE, relief="flat",
            font=("Arial", 9, "bold"), pady=9
        )
        self.botao_fonte_salvar.pack(fill="x", pady=(0, 6))

        self.botao_fonte_limpar = tk.Button(
            botoes, text="Limpar formulário",
            command=self.limpar_formulario_fonte,
            bg="#F3F4F6", fg=BLACK, relief="flat",
            font=("Arial", 9), pady=8
        )
        self.botao_fonte_limpar.pack(fill="x")

        self.status_fonte = self.criar_status(
            formulario,
            "* Nome e tipo são obrigatórios. A descrição é opcional."
        )

        tabela_painel = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tabela_painel.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            tabela_painel, text="Fontes cadastradas",
            bg=WHITE, fg=BLACK,
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 4))

        self.tabela_fontes = self.criar_tabela(
            tabela_painel,
            ("id", "nome", "tipo", "descricao"),
            {"id": "ID", "nome": "Nome", "tipo": "Tipo", "descricao": "Descrição"},
            {"id": 40, "nome": 150, "tipo": 120, "descricao": 240}
        )

        self.contador_fontes = tk.Label(
            tabela_painel, text="", bg=WHITE, fg=GRAY, font=("Arial", 9)
        )
        self.contador_fontes.pack(side="left", padx=15, pady=12)

        botoes_tabela = tk.Frame(tabela_painel, bg=WHITE)
        botoes_tabela.pack(side="right", padx=12, pady=8)

        tk.Button(
            botoes_tabela, text="Editar selecionada",
            command=self.preparar_edicao_fonte,
            bg="#E5E7EB", fg=BLACK, relief="flat",
            padx=9, pady=8
        ).pack(side="left", padx=3)

        tk.Button(
            botoes_tabela, text="Excluir selecionada",
            command=self.excluir_fonte,
            bg="#FEE2E2", fg=RED, relief="flat",
            padx=9, pady=8
        ).pack(side="left", padx=3)

        self.tabela_fontes.bind(
            "<Double-1>", lambda evento: self.preparar_edicao_fonte()
        )
        self.atualizar_tabela_fontes()

    def salvar_fonte(self):
        valores = {k: v.get().strip() for k, v in self.campos_fonte.items()}

        if not valores["nome"] or not valores["tipo"]:
            self.mensagem_erro(self.status_fonte, "Nome e tipo da fonte são obrigatórios.")
            return

        dados = {
            "nome": valores["nome"].upper(),
            "tipo": valores["tipo"].upper(),
            "descricao": valores["descricao"].upper()
        }

        if self.id_fonte_edicao is None:
            fonte = {"id": self.proximo_id_fonte, **dados}
            self.fontes.append(fonte)
            if not self.salvar_dados("fontes"):
                self.fontes.pop()
                self.mensagem_erro(self.status_fonte, "Não foi possível salvar a fonte.")
                return
            self.proximo_id_fonte += 1
            mensagem = "Fonte cadastrada com sucesso!"
        else:
            indice = next(
                (i for i, f in enumerate(self.fontes) if int(f["id"]) == self.id_fonte_edicao),
                None
            )
            if indice is None:
                self.mensagem_erro(self.status_fonte, "Fonte não encontrada.")
                return
            anterior = self.fontes[indice].copy()
            self.fontes[indice] = {"id": self.id_fonte_edicao, **dados}
            if not self.salvar_dados("fontes"):
                self.fontes[indice] = anterior
                self.mensagem_erro(self.status_fonte, "Não foi possível salvar as alterações.")
                return
            mensagem = "Fonte atualizada com sucesso!"

        self.atualizar_tabela_fontes()
        self.limpar_formulario_fonte()
        self.status_fonte.configure(text=mensagem, fg=GREEN)

    def preparar_edicao_fonte(self):
        selecionados = self.tabela_fontes.selection()
        if not selecionados:
            self.status_fonte.configure(text="Selecione uma fonte para editar.", fg=RED)
            return

        fonte_id = int(selecionados[0])
        fonte = next((f for f in self.fontes if int(f["id"]) == fonte_id), None)
        if fonte is None:
            return

        self.id_fonte_edicao = fonte_id
        for chave, entrada in self.campos_fonte.items():
            entrada.delete(0, tk.END)
            entrada.insert(0, fonte.get(chave, ""))

        self.botao_fonte_salvar.configure(text="Salvar alterações")
        self.botao_fonte_limpar.configure(text="Cancelar edição")
        self.status_fonte.configure(text=f"Editando a fonte {fonte_id}.", fg="#B7791F")

    def limpar_formulario_fonte(self):
        for entrada in self.campos_fonte.values():
            entrada.delete(0, tk.END)
        self.id_fonte_edicao = None
        self.botao_fonte_salvar.configure(text="Cadastrar fonte")
        self.botao_fonte_limpar.configure(text="Limpar formulário")
        self.status_fonte.configure(
            text="* Nome e tipo são obrigatórios. A descrição é opcional.",
            fg=GRAY
        )

    def excluir_fonte(self):
        selecionados = self.tabela_fontes.selection()
        if not selecionados:
            self.status_fonte.configure(text="Selecione uma fonte para excluir.", fg=RED)
            return

        fonte_id = int(selecionados[0])
        associado = any(
            int(registro["fonte_dados_id"]) == fonte_id
            for registro in self.registros
        )

        if associado:
            messagebox.showerror(
                "Exclusão não permitida",
                "Esta fonte possui registros meteorológicos associados e não pode ser excluída.",
                parent=self
            )
            return

        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir a fonte selecionada?",
            parent=self
        ):
            return

        indice = next((i for i, f in enumerate(self.fontes) if int(f["id"]) == fonte_id), None)
        if indice is None:
            return

        removida = self.fontes.pop(indice)
        if not self.salvar_dados("fontes"):
            self.fontes.insert(indice, removida)
            self.mensagem_erro(self.status_fonte, "Não foi possível salvar a exclusão.")
            return

        if self.id_fonte_edicao == fonte_id:
            self.limpar_formulario_fonte()

        self.atualizar_tabela_fontes()
        self.status_fonte.configure(text="Fonte excluída com sucesso!", fg=GREEN)

    def atualizar_tabela_fontes(self):
        for item in self.tabela_fontes.get_children():
            self.tabela_fontes.delete(item)

        for fonte in self.fontes:
            self.tabela_fontes.insert(
                "", "end", iid=str(fonte["id"]),
                values=(
                    fonte["id"], fonte["nome"], fonte["tipo"], fonte.get("descricao", "")
                )
            )

        self.atualizar_contador(self.contador_fontes, self.fontes, "fontes")

    # REGISTROS METEOROLÓGICOS

    def criar_tela_registros(self):
        self.titulo_pagina(
            "Registros meteorológicos",
            "Registre temperatura, umidade e precipitação por ponto e fonte."
        )

        area = tk.Frame(self.conteudo, bg=BG)
        area.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        area.grid_columnconfigure(0, weight=0, minsize=325)
        area.grid_columnconfigure(1, weight=1)
        area.grid_rowconfigure(0, weight=1)

        formulario = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        formulario.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        tk.Label(
            formulario, text="Novo registro",
            bg=WHITE, fg=BLACK,
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=16, pady=(15, 8))

        self.campos_registro = {}

        tk.Label(
            formulario, text="Ponto de observação *",
            bg=WHITE, fg="#374151", font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=16, pady=(6, 3))

        self.combo_ponto = ttk.Combobox(formulario, state="readonly", font=("Arial", 9))
        self.combo_ponto.pack(fill="x", padx=16, ipady=4)

        tk.Label(
            formulario, text="Fonte de dados *",
            bg=WHITE, fg="#374151", font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=16, pady=(8, 3))

        self.combo_fonte = ttk.Combobox(formulario, state="readonly", font=("Arial", 9))
        self.combo_fonte.pack(fill="x", padx=16, ipady=4)

        entrada_data = self.criar_entrada(
            formulario,
            "Data e hora * (DD-MM-AAAA HH:MM)",
            "data_hora",
            self.campos_registro
        )
        entrada_data.bind("<KeyRelease>", self.aplicar_mascara_data)
        self.criar_entrada(formulario, "Temperatura (°C) *", "temperatura", self.campos_registro)
        self.criar_entrada(formulario, "Umidade (%) *", "umidade", self.campos_registro)
        self.criar_entrada(formulario, "Precipitação (mm) *", "precipitacao", self.campos_registro)

        botoes = tk.Frame(formulario, bg=WHITE)
        botoes.pack(fill="x", padx=16, pady=12)

        self.botao_registro_salvar = tk.Button(
            botoes, text="Cadastrar registro",
            command=self.salvar_registro,
            bg=BLACK, fg=WHITE, relief="flat",
            font=("Arial", 9, "bold"), pady=9
        )
        self.botao_registro_salvar.pack(fill="x", pady=(0, 6))

        self.botao_registro_limpar = tk.Button(
            botoes, text="Limpar formulário",
            command=self.limpar_formulario_registro,
            bg="#F3F4F6", fg=BLACK, relief="flat",
            font=("Arial", 9), pady=8
        )
        self.botao_registro_limpar.pack(fill="x")

        self.status_registro = self.criar_status(
            formulario,
            "Todos os campos são obrigatórios. A data não pode estar no futuro."
        )

        tabela_painel = tk.Frame(area, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tabela_painel.grid(row=0, column=1, sticky="nsew")

        tk.Label(
            tabela_painel, text="Registros cadastrados",
            bg=WHITE, fg=BLACK,
            font=("Arial", 15, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 4))

        self.tabela_registros = self.criar_tabela(
            tabela_painel,
            ("id", "data", "ponto", "fonte", "temperatura", "umidade", "precipitacao"),
            {
                "id": "ID", "data": "Data e hora", "ponto": "Ponto",
                "fonte": "Fonte", "temperatura": "Temp. °C",
                "umidade": "Umidade %", "precipitacao": "Chuva mm"
            },
            {
                "id": 35, "data": 145, "ponto": 115, "fonte": 105,
                "temperatura": 75, "umidade": 75, "precipitacao": 80
            }
        )

        self.contador_registros = tk.Label(
            tabela_painel, text="", bg=WHITE, fg=GRAY, font=("Arial", 9)
        )
        self.contador_registros.pack(side="left", padx=15, pady=12)

        botoes_tabela = tk.Frame(tabela_painel, bg=WHITE)
        botoes_tabela.pack(side="right", padx=12, pady=8)

        tk.Button(
            botoes_tabela, text="Editar selecionado",
            command=self.preparar_edicao_registro,
            bg="#E5E7EB", fg=BLACK, relief="flat",
            padx=9, pady=8
        ).pack(side="left", padx=3)

        tk.Button(
            botoes_tabela, text="Excluir selecionado",
            command=self.excluir_registro,
            bg="#FEE2E2", fg=RED, relief="flat",
            padx=9, pady=8
        ).pack(side="left", padx=3)

        self.tabela_registros.bind(
            "<Double-1>", lambda evento: self.preparar_edicao_registro()
        )

        self.atualizar_opcoes_registro()
        self.atualizar_tabela_registros()

    def atualizar_opcoes_registro(self):
        self.mapa_pontos = {
            f"{p['id']} - {p['nome']}": int(p["id"])
            for p in self.pontos
        }

        self.mapa_fontes = {
            f"{f['id']} - {f['nome']}": int(f["id"])
            for f in self.fontes
        }

        self.combo_ponto["values"] = list(self.mapa_pontos.keys())
        self.combo_fonte["values"] = list(self.mapa_fontes.keys())

    def aplicar_mascara_data(self, evento):
        entrada = evento.widget
        texto = entrada.get()
        digitos = "".join(caractere for caractere in texto if "0" <= caractere <= "9")[:12]

        if len(digitos) <= 2:
            formatado = digitos
        elif len(digitos) <= 4:
            formatado = digitos[:2] + "-" + digitos[2:]
        elif len(digitos) <= 8:
            formatado = digitos[:2] + "-" + digitos[2:4] + "-" + digitos[4:]
        elif len(digitos) <= 10:
            formatado = (
                digitos[:2] + "-" + digitos[2:4] + "-" +
                digitos[4:8] + " " + digitos[8:]
            )
        else:
            formatado = (
                digitos[:2] + "-" + digitos[2:4] + "-" +
                digitos[4:8] + " " + digitos[8:10] + ":" + digitos[10:]
            )

        if texto != formatado:
            entrada.delete(0, tk.END)
            entrada.insert(0, formatado)
            entrada.icursor(tk.END)

    def data_para_exibicao(self, valor):
        try:
            return datetime.strptime(
                valor, "%Y-%m-%d %H:%M:%S"
            ).strftime("%d-%m-%Y %H:%M")
        except (TypeError, ValueError):
            return valor

    def dados_validos_registro(self):
        ponto_texto = self.combo_ponto.get().strip()
        fonte_texto = self.combo_fonte.get().strip()
        valores = {k: v.get().strip() for k, v in self.campos_registro.items()}

        if not ponto_texto or not fonte_texto or any(not v for v in valores.values()):
            self.mensagem_erro(self.status_registro, "Todos os campos do registro são obrigatórios.")
            return None

        if ponto_texto not in self.mapa_pontos:
            self.mensagem_erro(self.status_registro, "Selecione um ponto de observação válido.")
            return None

        if fonte_texto not in self.mapa_fontes:
            self.mensagem_erro(self.status_registro, "Selecione uma fonte de dados válida.")
            return None

        try:
            data = datetime.strptime(valores["data_hora"], "%d-%m-%Y %H:%M")
        except ValueError:
            self.mensagem_erro(
                self.status_registro,
                "Data inválida. Digite 12 números no formato DDMMAAAAHHMM. "
                "Exemplo: 181020262000 para 18-10-2026 20:00."
            )
            return None

        if data > datetime.now():
            self.mensagem_erro(self.status_registro, "A data e hora do registro não podem estar no futuro.")
            return None

        try:
            temperatura = self.converter_numero(valores["temperatura"])
            umidade = self.converter_numero(valores["umidade"])
            precipitacao = self.converter_numero(valores["precipitacao"])
        except ValueError:
            self.mensagem_erro(
                self.status_registro,
                "Temperatura, umidade e precipitação devem ser números válidos."
            )
            return None

        if not -90 <= temperatura <= 60:
            self.mensagem_erro(self.status_registro, "Temperatura inválida: utilize um valor entre -90 °C e 60 °C.")
            return None

        if not 0 <= umidade <= 100:
            self.mensagem_erro(self.status_registro, "Umidade inválida: utilize um valor entre 0% e 100%.")
            return None

        if precipitacao < 0:
            self.mensagem_erro(self.status_registro, "Precipitação inválida: o valor não pode ser negativo.")
            return None

        return {
            "ponto_observacao_id": self.mapa_pontos[ponto_texto],
            "fonte_dados_id": self.mapa_fontes[fonte_texto],
            "data_hora": data.strftime("%Y-%m-%d %H:%M:%S"),
            "temperatura": f"{temperatura:.2f}",
            "umidade": f"{umidade:.2f}",
            "precipitacao": f"{precipitacao:.2f}"
        }

    def salvar_registro(self):
        dados = self.dados_validos_registro()
        if dados is None:
            return

        duplicado = any(
            int(r["ponto_observacao_id"]) == dados["ponto_observacao_id"]
            and int(r["fonte_dados_id"]) == dados["fonte_dados_id"]
            and r["data_hora"] == dados["data_hora"]
            and int(r["id"]) != self.id_registro_edicao
            for r in self.registros
        )

        if duplicado:
            self.mensagem_erro(
                self.status_registro,
                "Já existe um registro dessa fonte para este ponto e horário."
            )
            return

        if self.id_registro_edicao is None:
            registro = {"id": self.proximo_id_registro, **dados}
            self.registros.append(registro)
            if not self.salvar_dados("registros"):
                self.registros.pop()
                self.mensagem_erro(self.status_registro, "Não foi possível salvar o registro.")
                return
            self.proximo_id_registro += 1
            mensagem = "Registro meteorológico cadastrado com sucesso!"
        else:
            indice = next(
                (i for i, r in enumerate(self.registros) if int(r["id"]) == self.id_registro_edicao),
                None
            )
            if indice is None:
                self.mensagem_erro(self.status_registro, "Registro não encontrado.")
                return
            anterior = self.registros[indice].copy()
            self.registros[indice] = {"id": self.id_registro_edicao, **dados}
            if not self.salvar_dados("registros"):
                self.registros[indice] = anterior
                self.mensagem_erro(self.status_registro, "Não foi possível salvar as alterações.")
                return
            mensagem = "Registro atualizado com sucesso!"

        self.atualizar_tabela_registros()
        self.limpar_formulario_registro()
        self.status_registro.configure(text=mensagem, fg=GREEN)

    def preparar_edicao_registro(self):
        selecionados = self.tabela_registros.selection()
        if not selecionados:
            self.status_registro.configure(text="Selecione um registro para editar.", fg=RED)
            return

        registro_id = int(selecionados[0])
        registro = next((r for r in self.registros if int(r["id"]) == registro_id), None)
        if registro is None:
            return

        self.id_registro_edicao = registro_id

        ponto_opcao = next(
            (k for k, v in self.mapa_pontos.items() if v == int(registro["ponto_observacao_id"])),
            ""
        )
        fonte_opcao = next(
            (k for k, v in self.mapa_fontes.items() if v == int(registro["fonte_dados_id"])),
            ""
        )

        self.combo_ponto.set(ponto_opcao)
        self.combo_fonte.set(fonte_opcao)

        for chave, entrada in self.campos_registro.items():
            entrada.delete(0, tk.END)
            valor = registro[chave]
            if chave == "data_hora":
                try:
                    valor = datetime.strptime(
                        valor, "%Y-%m-%d %H:%M:%S"
                    ).strftime("%d-%m-%Y %H:%M")
                except ValueError:
                    pass
            entrada.insert(0, valor)

        self.botao_registro_salvar.configure(text="Salvar alterações")
        self.botao_registro_limpar.configure(text="Cancelar edição")
        self.status_registro.configure(text=f"Editando o registro {registro_id}.", fg="#B7791F")

    def limpar_formulario_registro(self):
        self.combo_ponto.set("")
        self.combo_fonte.set("")
        for entrada in self.campos_registro.values():
            entrada.delete(0, tk.END)
        self.id_registro_edicao = None
        self.botao_registro_salvar.configure(text="Cadastrar registro")
        self.botao_registro_limpar.configure(text="Limpar formulário")
        self.status_registro.configure(
            text="Todos os campos são obrigatórios. A data não pode estar no futuro.",
            fg=GRAY
        )

    def excluir_registro(self):
        selecionados = self.tabela_registros.selection()
        if not selecionados:
            self.status_registro.configure(text="Selecione um registro para excluir.", fg=RED)
            return

        registro_id = int(selecionados[0])
        if not messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir o registro selecionado?",
            parent=self
        ):
            return

        indice = next((i for i, r in enumerate(self.registros) if int(r["id"]) == registro_id), None)
        if indice is None:
            return

        removido = self.registros.pop(indice)
        if not self.salvar_dados("registros"):
            self.registros.insert(indice, removido)
            self.mensagem_erro(self.status_registro, "Não foi possível salvar a exclusão.")
            return

        if self.id_registro_edicao == registro_id:
            self.limpar_formulario_registro()

        self.atualizar_tabela_registros()
        self.status_registro.configure(text="Registro excluído com sucesso!", fg=GREEN)

    def nome_ponto(self, ponto_id):
        ponto = next((p for p in self.pontos if int(p["id"]) == int(ponto_id)), None)
        return ponto["nome"] if ponto else f"ID {ponto_id}"

    def nome_fonte(self, fonte_id):
        fonte = next((f for f in self.fontes if int(f["id"]) == int(fonte_id)), None)
        return fonte["nome"] if fonte else f"ID {fonte_id}"

    def atualizar_tabela_registros(self):
        for item in self.tabela_registros.get_children():
            self.tabela_registros.delete(item)

        for registro in self.registros:
            self.tabela_registros.insert(
                "", "end", iid=str(registro["id"]),
                values=(
                    registro["id"],
                    self.data_para_exibicao(registro["data_hora"]),
                    self.nome_ponto(registro["ponto_observacao_id"]),
                    self.nome_fonte(registro["fonte_dados_id"]),
                    registro["temperatura"],
                    registro["umidade"],
                    registro["precipitacao"]
                )
            )

        self.atualizar_contador(
            self.contador_registros, self.registros, "registros"
        )

    # IMPORTAÇÃO CSV - PRÓXIMA ETAPA

    def criar_tela_csv(self):
        self.titulo_pagina(
            "Importação CSV",
            "Importe observações meteorológicas a partir de arquivos CSV."
        )

        painel = tk.Frame(
            self.conteudo,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        painel.pack(fill="both", expand=True, padx=28, pady=(0, 25))

        tk.Label(
            painel,
            text="Importação de dados meteorológicos",
            bg=WHITE,
            fg=BLACK,
            font=("Arial", 17, "bold")
        ).pack(pady=(80, 12))

        tk.Label(
            painel,
            text=(
                "A próxima etapa implementará a seleção e leitura de arquivos CSV,\n"
                "a validação de cada linha e o relatório de registros importados\n"
                "ou rejeitados."
            ),
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 10),
            justify="center"
        ).pack(pady=5)

        tk.Label(
            painel,
            text="Formato previsto: UTF-8 | Separador ; | Decimal com ponto",
            bg=WHITE,
            fg=GRAY,
            font=("Arial", 9)
        ).pack(pady=18)


if __name__ == "__main__":
    app = NimbusApp()
    app.mainloop()
