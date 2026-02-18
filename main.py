# -*- coding: utf-8 -*-
"""
main.py — Interface Gráfica Principal (CustomTkinter)
Sistema Oficina 2026

Executar: python main.py
"""

import customtkinter as ctk
from tkinter import messagebox, StringVar, END
import database
import backup
import print_engine
from datetime import datetime
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def carregar_config():
    """Carrega configurações da empresa do arquivo JSON."""
    defaults = {
        "nome": "ELETRÔNICA EXEMPLO",
        "endereco": "Rua Exemplo, 123 — Centro — Cidade/UF",
        "telefone": "(00) 0000-0000",
        "cnpj": "00.000.000/0001-00",
    }
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
                defaults.update(dados)
    except Exception:
        pass
    return defaults

def salvar_config(dados):
    """Salva configurações da empresa no arquivo JSON."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        # Atualiza print_engine em tempo real
        import print_engine as pe
        pe.EMPRESA.update(dados)
        return True
    except Exception as e:
        print(f"[CONFIG] Erro ao salvar: {e}")
        return False

# ──────────────────────────── CONFIGURAÇÃO GLOBAL ────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Cores do tema
COR_SIDEBAR = "#1a2332"
COR_SIDEBAR_HOVER = "#263545"
COR_SIDEBAR_ACTIVE = "#2d4a6f"
COR_FUNDO = "#0f1923"
COR_CARD = "#1a2a3a"
COR_CARD_HOVER = "#223344"
COR_AZUL = "#3b82f6"
COR_AZUL_HOVER = "#2563eb"
COR_VERDE = "#22c55e"
COR_AMARELO = "#f59e0b"
COR_VERMELHO = "#ef4444"
COR_TEXTO = "#e2e8f0"
COR_TEXTO_SEC = "#94a3b8"
COR_BORDA = "#334155"

# Fontes
FONTE_TITULO = ("Segoe UI", 22, "bold")
FONTE_SUBTITULO = ("Segoe UI", 16, "bold")
FONTE_NORMAL = ("Segoe UI", 14)
FONTE_GRANDE = ("Segoe UI", 18)
FONTE_PEQUENA = ("Segoe UI", 12)
FONTE_MENU = ("Segoe UI", 15, "bold")
FONTE_CARD_NUM = ("Segoe UI", 42, "bold")


class App(ctk.CTk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()

        # ─── Inicialização ───
        database.init_db()
        backup.realizar_backup()

        # ─── Janela ───
        self.title("Sistema Oficina 2026")
        self.geometry("1280x800")
        self.minsize(1024, 700)

        # Variáveis de estado
        self.pagina_atual = None
        self.cliente_selecionado_id = None
        self.os_selecionada_ra = None

        # ─── Layout Principal: Sidebar + Content ───
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_sidebar()
        self._criar_area_conteudo()

        # Página inicial
        self.mostrar_dashboard()

        # ─── Atalhos de Teclado ───
        self.bind("<F2>", lambda e: self.mostrar_nova_os())
        self.bind("<F3>", lambda e: self.mostrar_buscar_os())
        self.bind("<F4>", lambda e: self.mostrar_clientes())
        self.bind("<F5>", lambda e: self.mostrar_dashboard())
        self.bind("<F1>", lambda e: self._mostrar_ajuda_atalhos())

    # ════════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ════════════════════════════════════════════════════════════════

    def _criar_sidebar(self):
        """Cria o menu lateral fixo."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=(25, 30), padx=15, fill="x")

        ctk.CTkLabel(
            logo_frame, text="🔧", font=("Segoe UI", 32)
        ).pack()
        ctk.CTkLabel(
            logo_frame, text="Oficina 2026",
            font=("Segoe UI", 18, "bold"), text_color=COR_AZUL
        ).pack(pady=(5, 0))

        # Botões do menu
        self.menu_buttons = {}
        menu_items = [
            ("📊", "Dashboard", self.mostrar_dashboard),
            ("📝", "Nova OS", self.mostrar_nova_os),
            ("🔍", "Buscar OS", self.mostrar_buscar_os),
            ("👥", "Clientes", self.mostrar_clientes),
            ("⚙️", "Configurações", self.mostrar_configuracoes),
        ]

        for icone, texto, comando in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icone}  {texto}",
                font=FONTE_MENU,
                fg_color="transparent",
                hover_color=COR_SIDEBAR_HOVER,
                anchor="w",
                height=50,
                corner_radius=8,
                command=comando,
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.menu_buttons[texto] = btn

        # Espaçador
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Toggle de tema
        self.tema_var = StringVar(value="dark")
        tema_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        tema_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            tema_frame, text="🌙 Tema", font=FONTE_PEQUENA, text_color=COR_TEXTO_SEC
        ).pack(side="left")

        self.tema_switch = ctk.CTkSwitch(
            tema_frame, text="", width=40,
            command=self._toggle_tema,
            onvalue="light", offvalue="dark",
            variable=self.tema_var,
        )
        self.tema_switch.pack(side="right")

        # Botão sair
        ctk.CTkButton(
            self.sidebar,
            text="  ⏻  Sair",
            font=FONTE_MENU,
            fg_color=COR_VERMELHO,
            hover_color="#dc2626",
            height=45,
            corner_radius=8,
            command=self._sair,
        ).pack(fill="x", padx=10, pady=(5, 20))

    def _toggle_tema(self):
        """Alterna entre modo escuro e claro."""
        modo = self.tema_var.get()
        ctk.set_appearance_mode(modo)

    def _atualizar_menu_ativo(self, nome):
        """Destaca o botão do menu ativo."""
        for key, btn in self.menu_buttons.items():
            if key == nome:
                btn.configure(fg_color=COR_SIDEBAR_ACTIVE)
            else:
                btn.configure(fg_color="transparent")

    def _sair(self):
        """Fecha a aplicação."""
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            self.destroy()

    # ════════════════════════════════════════════════════════════════
    #  ÁREA DE CONTEÚDO
    # ════════════════════════════════════════════════════════════════

    def _criar_area_conteudo(self):
        """Cria o frame principal de conteúdo."""
        self.content = ctk.CTkFrame(self, fg_color=COR_FUNDO, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _limpar_conteudo(self):
        """Remove todos os widgets da área de conteúdo."""
        for widget in self.content.winfo_children():
            widget.destroy()

    # ════════════════════════════════════════════════════════════════
    #  DASHBOARD
    # ════════════════════════════════════════════════════════════════

    def mostrar_dashboard(self):
        """Exibe o dashboard com contadores."""
        self._limpar_conteudo()
        self._atualizar_menu_ativo("Dashboard")
        self.pagina_atual = "Dashboard"

        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        ctk.CTkLabel(
            frame, text="📊  Dashboard", font=FONTE_TITULO, text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            frame, text=f"Hoje: {datetime.now().strftime('%d/%m/%Y')}",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SEC, anchor="w"
        ).pack(fill="x", pady=(0, 20))

        # Cards de contadores
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        pendentes = database.contar_pendentes()
        prontos = database.contar_prontos()
        contagens = database.contar_por_status()

        # Card Pendentes
        self._criar_card_dashboard(
            cards_frame, "⏳", "Pendentes", str(pendentes),
            COR_AMARELO, 0
        )
        # Card Prontos
        self._criar_card_dashboard(
            cards_frame, "✅", "Prontos p/ Retirar", str(prontos),
            COR_VERDE, 1
        )
        # Card Aguardando Peça
        aguardando = contagens.get("Aguardando Peça", 0)
        self._criar_card_dashboard(
            cards_frame, "🔧", "Aguardando Peça", str(aguardando),
            COR_AZUL, 2
        )

        # ─── Últimas OS ───
        ctk.CTkLabel(
            frame, text="📋  Últimas Ordens de Serviço",
            font=FONTE_SUBTITULO, text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(30, 10))

        servicos = database.listar_servicos()[:15]
        if servicos:
            self._criar_tabela_servicos(frame, servicos)
        else:
            ctk.CTkLabel(
                frame, text="Nenhuma ordem de serviço cadastrada ainda.",
                font=FONTE_NORMAL, text_color=COR_TEXTO_SEC
            ).pack(pady=20)

    def _criar_card_dashboard(self, parent, icone, titulo, valor, cor, col):
        """Cria um card de contagem no dashboard."""
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=12, height=160)
        card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")
        card.grid_propagate(False)

        # Conteúdo do card
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text=icone, font=("Segoe UI", 28)).pack()
        ctk.CTkLabel(
            inner, text=valor, font=FONTE_CARD_NUM, text_color=cor
        ).pack(pady=(5, 0))
        ctk.CTkLabel(
            inner, text=titulo, font=FONTE_NORMAL, text_color=COR_TEXTO_SEC
        ).pack()

    # ════════════════════════════════════════════════════════════════
    #  NOVA OS
    # ════════════════════════════════════════════════════════════════

    def mostrar_nova_os(self):
        """Exibe o formulário de nova Ordem de Serviço."""
        self._limpar_conteudo()
        self._atualizar_menu_ativo("Nova OS")
        self.pagina_atual = "Nova OS"
        self.cliente_selecionado_id = None

        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        novo_ra = database.gerar_ra()
        ctk.CTkLabel(
            frame, text="📝  Nova Ordem de Serviço", font=FONTE_TITULO,
            text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            frame, text=f"RA: {novo_ra}", font=FONTE_GRANDE,
            text_color=COR_AZUL, anchor="w"
        ).pack(fill="x", pady=(0, 20))

        self.ra_atual = novo_ra

        # ─── Seção: Cliente ───
        sec_cliente = self._criar_secao(frame, "👤  Cliente")

        # Busca de cliente
        busca_frame = ctk.CTkFrame(sec_cliente, fg_color="transparent")
        busca_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            busca_frame, text="Buscar cliente:", font=FONTE_NORMAL, text_color=COR_TEXTO
        ).pack(anchor="w")

        self.busca_cliente_var = StringVar()
        self.busca_cliente_var.trace_add("write", self._ao_buscar_cliente)
        self.entry_busca_cliente = ctk.CTkEntry(
            busca_frame, textvariable=self.busca_cliente_var,
            font=FONTE_NORMAL, height=40,
            placeholder_text="Digite o nome ou telefone..."
        )
        self.entry_busca_cliente.pack(fill="x", pady=5)

        # Lista de resultados da busca
        self.lista_clientes_frame = ctk.CTkFrame(busca_frame, fg_color=COR_CARD, corner_radius=8)

        # Label cliente selecionado
        self.label_cliente_sel = ctk.CTkLabel(
            busca_frame, text="Nenhum cliente selecionado",
            font=FONTE_NORMAL, text_color=COR_AMARELO, anchor="w"
        )
        self.label_cliente_sel.pack(fill="x", pady=5)

        # Botão novo cliente
        ctk.CTkButton(
            busca_frame, text="➕ Cadastrar Novo Cliente",
            font=FONTE_NORMAL, fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
            height=38, command=self._toggle_form_novo_cliente
        ).pack(anchor="w", pady=5)

        # Form novo cliente (oculto inicialmente)
        self.form_novo_cliente = ctk.CTkFrame(sec_cliente, fg_color=COR_CARD, corner_radius=8)
        self.campos_cliente = {}
        campos = [
            ("nome", "Nome *"),
            ("telefone", "Telefone"),
            ("documento", "CPF/CNPJ"),
            ("endereco", "Endereço"),
        ]
        for key, label in campos:
            row = ctk.CTkFrame(self.form_novo_cliente, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(row, text=label, font=FONTE_NORMAL, text_color=COR_TEXTO, width=120, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, font=FONTE_NORMAL, height=38)
            entry.pack(side="left", fill="x", expand=True)
            self.campos_cliente[key] = entry

        btn_salvar_cli = ctk.CTkButton(
            self.form_novo_cliente, text="💾 Salvar Cliente",
            font=FONTE_NORMAL, fg_color=COR_VERDE, hover_color="#16a34a",
            height=38, command=self._salvar_novo_cliente_inline
        )
        btn_salvar_cli.pack(padx=15, pady=10, anchor="e")

        self.form_novo_cliente_visivel = False

        # ─── Seção: Aparelho ───
        sec_aparelho = self._criar_secao(frame, "📱  Aparelho")

        self.campos_aparelho = {}
        campos_ap = [
            ("aparelho", "Aparelho *"),
            ("marca", "Marca"),
            ("modelo", "Modelo"),
            ("numero_serie", "Nº Série"),
        ]
        row_frame = ctk.CTkFrame(sec_aparelho, fg_color="transparent")
        row_frame.pack(fill="x")
        row_frame.grid_columnconfigure((0, 1), weight=1)

        for i, (key, label) in enumerate(campos_ap):
            r, c = divmod(i, 2)
            cell = ctk.CTkFrame(row_frame, fg_color="transparent")
            cell.grid(row=r, column=c, padx=5, pady=4, sticky="ew")
            ctk.CTkLabel(cell, text=label, font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").pack(anchor="w")
            entry = ctk.CTkEntry(cell, font=FONTE_NORMAL, height=38)
            entry.pack(fill="x")
            self.campos_aparelho[key] = entry

        # Defeito
        ctk.CTkLabel(
            sec_aparelho, text="Defeito Relatado:", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(10, 2))
        self.text_defeito = ctk.CTkTextbox(sec_aparelho, font=FONTE_NORMAL, height=80, corner_radius=8)
        self.text_defeito.pack(fill="x")

        # ─── Seção: Peças ───
        sec_pecas = self._criar_secao(frame, "🔩  Peças / Serviços")

        peca_row = ctk.CTkFrame(sec_pecas, fg_color="transparent")
        peca_row.pack(fill="x")
        peca_row.grid_columnconfigure(0, weight=3)
        peca_row.grid_columnconfigure(1, weight=1)

        self.entry_peca_desc = ctk.CTkEntry(
            peca_row, font=FONTE_NORMAL, height=38, placeholder_text="Descrição da peça/serviço"
        )
        self.entry_peca_desc.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.entry_peca_valor = ctk.CTkEntry(
            peca_row, font=FONTE_NORMAL, height=38, placeholder_text="Valor (R$)"
        )
        self.entry_peca_valor.grid(row=0, column=1, padx=(0, 5), sticky="ew")

        ctk.CTkButton(
            peca_row, text="➕", font=FONTE_NORMAL, width=50,
            fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
            height=38, command=self._adicionar_peca_lista
        ).grid(row=0, column=2)

        # Lista de peças adicionadas
        self.pecas_lista_frame = ctk.CTkFrame(sec_pecas, fg_color="transparent")
        self.pecas_lista_frame.pack(fill="x", pady=10)
        self.pecas_temp = []  # [(desc, valor), ...]

        # Valor total
        self.label_valor_total = ctk.CTkLabel(
            sec_pecas, text="Valor Total: R$ 0,00",
            font=FONTE_SUBTITULO, text_color=COR_VERDE, anchor="e"
        )
        self.label_valor_total.pack(fill="x")

        # ─── Botões de Ação ───
        acoes = ctk.CTkFrame(frame, fg_color="transparent")
        acoes.pack(fill="x", pady=20)

        ctk.CTkButton(
            acoes, text="💾  Salvar OS", font=FONTE_GRANDE,
            fg_color=COR_VERDE, hover_color="#16a34a",
            height=50, corner_radius=10,
            command=self._salvar_os
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            acoes, text="🖨️  Salvar e Imprimir", font=FONTE_GRANDE,
            fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
            height=50, corner_radius=10,
            command=lambda: self._salvar_os(imprimir=True)
        ).pack(side="left")

    def _criar_secao(self, parent, titulo):
        """Cria uma seção com título e retorna o frame de conteúdo."""
        ctk.CTkLabel(
            parent, text=titulo, font=FONTE_SUBTITULO, text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(20, 8))
        frame = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=10)
        frame.pack(fill="x", padx=0, pady=(0, 5))
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        return inner

    def _ao_buscar_cliente(self, *args):
        """Callback de busca as-you-type de clientes."""
        query = self.busca_cliente_var.get().strip()

        # Limpa resultados anteriores
        for w in self.lista_clientes_frame.winfo_children():
            w.destroy()

        if len(query) < 2:
            self.lista_clientes_frame.pack_forget()
            return

        resultados = database.buscar_clientes(query)
        if not resultados:
            self.lista_clientes_frame.pack_forget()
            return

        self.lista_clientes_frame.pack(fill="x", pady=2)

        for cli in resultados[:8]:
            btn = ctk.CTkButton(
                self.lista_clientes_frame,
                text=f"  {cli['nome']}  —  Tel: {cli.get('telefone', '')}",
                font=FONTE_NORMAL,
                fg_color="transparent",
                hover_color=COR_SIDEBAR_HOVER,
                anchor="w", height=36,
                command=lambda c=cli: self._selecionar_cliente(c)
            )
            btn.pack(fill="x", padx=5, pady=1)

    def _selecionar_cliente(self, cliente):
        """Seleciona um cliente da busca."""
        self.cliente_selecionado_id = cliente["id"]
        self.label_cliente_sel.configure(
            text=f"✅ {cliente['nome']}  |  Tel: {cliente.get('telefone', '')}  |  Doc: {cliente.get('documento', '')}",
            text_color=COR_VERDE
        )
        self.lista_clientes_frame.pack_forget()
        self.busca_cliente_var.set("")

    def _toggle_form_novo_cliente(self):
        """Mostra/oculta o formulário de novo cliente."""
        if self.form_novo_cliente_visivel:
            self.form_novo_cliente.pack_forget()
        else:
            self.form_novo_cliente.pack(fill="x", pady=10)
        self.form_novo_cliente_visivel = not self.form_novo_cliente_visivel

    def _salvar_novo_cliente_inline(self):
        """Salva um novo cliente diretamente do formulário da OS."""
        nome = self.campos_cliente["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "O nome do cliente é obrigatório!")
            return

        telefone = self.campos_cliente["telefone"].get().strip()
        documento = self.campos_cliente["documento"].get().strip()
        endereco = self.campos_cliente["endereco"].get().strip()

        try:
            cliente_id = database.salvar_cliente(nome, endereco, telefone, documento)
            if cliente_id:
                self.cliente_selecionado_id = cliente_id
                self.label_cliente_sel.configure(
                    text=f"✅ {nome}  |  Tel: {telefone}  |  Doc: {documento}",
                    text_color=COR_VERDE
                )
                self.form_novo_cliente.pack_forget()
                self.form_novo_cliente_visivel = False
                # Limpa campos
                for entry in self.campos_cliente.values():
                    entry.delete(0, END)
                messagebox.showinfo("Sucesso", f"Cliente '{nome}' cadastrado com sucesso!")
            else:
                messagebox.showerror("Erro", "Não foi possível salvar o cliente.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar cliente: {e}")

    def _adicionar_peca_lista(self):
        """Adiciona uma peça à lista temporária."""
        desc = self.entry_peca_desc.get().strip()
        valor_str = self.entry_peca_valor.get().strip().replace(",", ".")

        if not desc:
            messagebox.showwarning("Atenção", "Informe a descrição da peça/serviço.")
            return
        try:
            valor = float(valor_str) if valor_str else 0.0
        except ValueError:
            messagebox.showwarning("Atenção", "Valor inválido! Use números (ex: 50.00)")
            return

        self.pecas_temp.append((desc, valor))
        self._atualizar_lista_pecas()

        self.entry_peca_desc.delete(0, END)
        self.entry_peca_valor.delete(0, END)
        self.entry_peca_desc.focus()

    def _atualizar_lista_pecas(self):
        """Redesenha a lista de peças temporárias."""
        for w in self.pecas_lista_frame.winfo_children():
            w.destroy()

        total = 0.0
        for i, (desc, valor) in enumerate(self.pecas_temp):
            row = ctk.CTkFrame(self.pecas_lista_frame, fg_color=COR_CARD, corner_radius=6, height=36)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            ctk.CTkLabel(
                row, text=f"  {desc}", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w"
            ).pack(side="left", fill="x", expand=True, padx=5)

            ctk.CTkLabel(
                row, text=f"R$ {valor:.2f}", font=FONTE_NORMAL, text_color=COR_VERDE
            ).pack(side="left", padx=10)

            ctk.CTkButton(
                row, text="✕", width=30, height=28,
                fg_color=COR_VERMELHO, hover_color="#dc2626",
                font=("Segoe UI", 12, "bold"),
                command=lambda idx=i: self._remover_peca_temp(idx)
            ).pack(side="right", padx=5)

            total += valor

        self.label_valor_total.configure(text=f"Valor Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def _remover_peca_temp(self, idx):
        """Remove uma peça da lista temporária."""
        if 0 <= idx < len(self.pecas_temp):
            self.pecas_temp.pop(idx)
            self._atualizar_lista_pecas()

    def _salvar_os(self, imprimir=False):
        """Salva a Ordem de Serviço no banco de dados."""
        if not self.cliente_selecionado_id:
            messagebox.showwarning("Atenção", "Selecione ou cadastre um cliente antes de salvar!")
            return

        aparelho = self.campos_aparelho["aparelho"].get().strip()
        if not aparelho:
            messagebox.showwarning("Atenção", "Informe o aparelho!")
            return

        try:
            # Calcula valor total
            valor_total = sum(v for _, v in self.pecas_temp)

            # Salva serviço
            ok = database.salvar_servico(
                ra=self.ra_atual,
                cliente_id=self.cliente_selecionado_id,
                aparelho=aparelho,
                marca=self.campos_aparelho["marca"].get().strip(),
                modelo=self.campos_aparelho["modelo"].get().strip(),
                numero_serie=self.campos_aparelho["numero_serie"].get().strip(),
                defeito_relatado=self.text_defeito.get("1.0", END).strip(),
                valor_total=valor_total,
            )

            if not ok:
                messagebox.showerror("Erro", "Falha ao salvar a OS no banco de dados.")
                return

            # Salva peças
            for desc, valor in self.pecas_temp:
                database.adicionar_peca(self.ra_atual, desc, valor)

            messagebox.showinfo("Sucesso", f"OS {self.ra_atual} salva com sucesso!")

            if imprimir:
                print_engine.gerar_pdf_ra(self.ra_atual)

            # Volta ao dashboard
            self.mostrar_dashboard()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar OS: {e}")

    # ════════════════════════════════════════════════════════════════
    #  BUSCAR OS
    # ════════════════════════════════════════════════════════════════

    def mostrar_buscar_os(self):
        """Exibe a tela de busca de Ordens de Serviço."""
        self._limpar_conteudo()
        self._atualizar_menu_ativo("Buscar OS")
        self.pagina_atual = "Buscar OS"

        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        ctk.CTkLabel(
            frame, text="🔍  Buscar Ordens de Serviço", font=FONTE_TITULO,
            text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(0, 15))

        # Barra de busca
        busca_frame = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=10)
        busca_frame.pack(fill="x", pady=(0, 15))

        inner_busca = ctk.CTkFrame(busca_frame, fg_color="transparent")
        inner_busca.pack(fill="x", padx=15, pady=12)

        self.busca_os_var = StringVar()
        entry_busca = ctk.CTkEntry(
            inner_busca, textvariable=self.busca_os_var,
            font=FONTE_NORMAL, height=42,
            placeholder_text="Digite o RA ou nome do cliente..."
        )
        entry_busca.pack(side="left", fill="x", expand=True, padx=(0, 10))
        entry_busca.bind("<Return>", lambda e: self._executar_busca_os())

        ctk.CTkButton(
            inner_busca, text="🔍 Buscar", font=FONTE_NORMAL,
            fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
            height=42, width=120,
            command=self._executar_busca_os
        ).pack(side="right")

        # Filtros rápidos
        filtros = ctk.CTkFrame(frame, fg_color="transparent")
        filtros.pack(fill="x", pady=(0, 15))

        for status_name, cor in [("Todos", COR_TEXTO_SEC), ("Aberto", COR_AMARELO),
                                  ("Aguardando Peça", COR_AZUL), ("Pronto", COR_VERDE),
                                  ("Entregue", COR_TEXTO_SEC)]:
            ctk.CTkButton(
                filtros, text=status_name, font=FONTE_PEQUENA,
                fg_color=COR_CARD, hover_color=COR_CARD_HOVER,
                text_color=cor, height=34, corner_radius=20,
                command=lambda s=status_name: self._filtrar_os(s)
            ).pack(side="left", padx=3)

        # Frame de resultados
        self.resultados_os_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.resultados_os_frame.pack(fill="both", expand=True)

        # Mostra todos inicialmente
        self._filtrar_os("Todos")

    def _executar_busca_os(self):
        """Executa a busca de OS."""
        query = self.busca_os_var.get().strip()
        if not query:
            self._filtrar_os("Todos")
            return

        servicos = database.buscar_servicos(query)
        self._exibir_resultados_os(servicos)

    def _filtrar_os(self, status):
        """Filtra OS por status."""
        if status == "Todos":
            servicos = database.listar_servicos()
        else:
            servicos = database.listar_servicos(status)
        self._exibir_resultados_os(servicos)

    def _exibir_resultados_os(self, servicos):
        """Exibe resultados de busca/filtro de OS."""
        for w in self.resultados_os_frame.winfo_children():
            w.destroy()

        if not servicos:
            ctk.CTkLabel(
                self.resultados_os_frame, text="Nenhuma OS encontrada.",
                font=FONTE_NORMAL, text_color=COR_TEXTO_SEC
            ).pack(pady=20)
            return

        self._criar_tabela_servicos(self.resultados_os_frame, servicos, com_acoes=True)

    def _criar_tabela_servicos(self, parent, servicos, com_acoes=False):
        """Cria a tabela de serviços."""
        # Cabeçalho
        header = ctk.CTkFrame(parent, fg_color=COR_SIDEBAR, corner_radius=8, height=40)
        header.pack(fill="x", pady=(0, 2))
        header.pack_propagate(False)

        cols = [("RA", 0.12), ("Cliente", 0.22), ("Aparelho", 0.15),
                ("Status", 0.13), ("Valor", 0.1), ("Data", 0.12)]
        if com_acoes:
            cols.append(("Ações", 0.16))

        for text, w in cols:
            ctk.CTkLabel(
                header, text=text, font=("Segoe UI", 12, "bold"),
                text_color=COR_TEXTO_SEC, anchor="w"
            ).place(relx=sum(c[1] for c in cols[:cols.index((text, w))]), rely=0.5, anchor="w", relwidth=w)

        # Linhas
        for srv in servicos:
            row = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=6, height=42)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            status = srv.get("status", "")
            status_cor = {
                "Aberto": COR_AMARELO,
                "Aguardando Peça": COR_AZUL,
                "Pronto": COR_VERDE,
                "Entregue": COR_TEXTO_SEC,
            }.get(status, COR_TEXTO)

            valores = [
                (srv.get("ra", ""), COR_AZUL),
                (srv.get("cliente_nome", ""), COR_TEXTO),
                (srv.get("aparelho", ""), COR_TEXTO),
                (status, status_cor),
                (f"R$ {srv.get('valor_total', 0):.2f}", COR_VERDE),
                (srv.get("data_entrada", ""), COR_TEXTO_SEC),
            ]

            rx = 0.0
            for j, ((text, w), (val, cor)) in enumerate(zip(cols[:6], valores)):
                ctk.CTkLabel(
                    row, text=val, font=FONTE_PEQUENA,
                    text_color=cor, anchor="w"
                ).place(relx=rx, rely=0.5, anchor="w", relwidth=w)
                rx += w

            if com_acoes:
                acoes_frame = ctk.CTkFrame(row, fg_color="transparent")
                acoes_frame.place(relx=rx, rely=0.5, anchor="w", relwidth=0.16, relheight=0.9)

                ra = srv.get("ra", "")
                ctk.CTkButton(
                    acoes_frame, text="👁", width=32, height=28,
                    font=("Segoe UI", 12), fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
                    command=lambda r=ra: self._abrir_detalhes_os(r)
                ).pack(side="left", padx=1)

                ctk.CTkButton(
                    acoes_frame, text="🖨", width=32, height=28,
                    font=("Segoe UI", 12), fg_color=COR_SIDEBAR_ACTIVE, hover_color=COR_SIDEBAR_HOVER,
                    command=lambda r=ra: print_engine.gerar_pdf_ra(r)
                ).pack(side="left", padx=1)

    def _abrir_detalhes_os(self, ra):
        """Exibe os detalhes de uma OS com opção de editar status."""
        servico = database.obter_servico(ra)
        if not servico:
            messagebox.showerror("Erro", f"OS {ra} não encontrada!")
            return

        pecas = database.listar_pecas(ra)
        self._limpar_conteudo()
        self.pagina_atual = "Detalhes OS"

        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        ctk.CTkLabel(
            frame, text=f"📋  Detalhes — RA: {ra}", font=FONTE_TITULO,
            text_color=COR_AZUL, anchor="w"
        ).pack(fill="x", pady=(0, 20))

        # Card de info
        info_card = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=10)
        info_card.pack(fill="x", pady=(0, 15))
        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="x", padx=20, pady=15)

        campos_info = [
            ("Cliente", servico.get("cliente_nome", "")),
            ("Telefone", servico.get("cliente_telefone", "")),
            ("Documento", servico.get("cliente_documento", "")),
            ("Aparelho", f"{servico.get('aparelho', '')} — {servico.get('marca', '')} {servico.get('modelo', '')}"),
            ("Nº Série", servico.get("numero_serie", "")),
            ("Defeito", servico.get("defeito_relatado", "")),
            ("Serviço Realizado", servico.get("servico_realizado", "")),
            ("Data Entrada", servico.get("data_entrada", "")),
            ("Data Saída", servico.get("data_saida", "")),
        ]

        for label, valor in campos_info:
            row = ctk.CTkFrame(info_inner, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                row, text=f"{label}:", font=("Segoe UI", 13, "bold"),
                text_color=COR_TEXTO_SEC, width=160, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=valor, font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w"
            ).pack(side="left", fill="x", expand=True)

        # Status + alterar
        status_frame = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=10)
        status_frame.pack(fill="x", pady=(0, 15))
        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            status_inner, text="Status Atual:", font=FONTE_SUBTITULO, text_color=COR_TEXTO
        ).pack(side="left")

        status_options = ["Aberto", "Aguardando Peça", "Pronto", "Entregue"]
        self.combo_status = ctk.CTkComboBox(
            status_inner, values=status_options,
            font=FONTE_NORMAL, height=38, width=200
        )
        self.combo_status.set(servico.get("status", "Aberto"))
        self.combo_status.pack(side="left", padx=15)

        ctk.CTkButton(
            status_inner, text="✅ Atualizar", font=FONTE_NORMAL,
            fg_color=COR_VERDE, hover_color="#16a34a",
            height=38,
            command=lambda: self._atualizar_status_os(ra)
        ).pack(side="left")

        # Serviço realizado (editável)
        srv_frame = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=10)
        srv_frame.pack(fill="x", pady=(0, 15))
        srv_inner = ctk.CTkFrame(srv_frame, fg_color="transparent")
        srv_inner.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            srv_inner, text="Serviço Realizado:", font=FONTE_SUBTITULO, text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(0, 5))

        self.text_servico_realizado = ctk.CTkTextbox(srv_inner, font=FONTE_NORMAL, height=80, corner_radius=8)
        self.text_servico_realizado.pack(fill="x")
        self.text_servico_realizado.insert("1.0", servico.get("servico_realizado", ""))

        ctk.CTkButton(
            srv_inner, text="💾 Salvar Serviço Realizado", font=FONTE_NORMAL,
            fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER, height=38,
            command=lambda: self._salvar_servico_realizado(ra)
        ).pack(anchor="e", pady=(10, 0))

        # Peças
        if pecas:
            ctk.CTkLabel(
                frame, text="🔩  Peças / Serviços", font=FONTE_SUBTITULO,
                text_color=COR_TEXTO, anchor="w"
            ).pack(fill="x", pady=(10, 5))

            for p in pecas:
                row = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=6, height=36)
                row.pack(fill="x", pady=1)
                row.pack_propagate(False)
                ctk.CTkLabel(
                    row, text=f"  {p['descricao']}", font=FONTE_NORMAL,
                    text_color=COR_TEXTO, anchor="w"
                ).pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(
                    row, text=f"R$ {p.get('valor_unitario', 0):.2f}",
                    font=FONTE_NORMAL, text_color=COR_VERDE
                ).pack(side="right", padx=15)

        # Valor total
        valor = servico.get("valor_total", 0) or 0
        ctk.CTkLabel(
            frame, text=f"Valor Total: R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            font=FONTE_SUBTITULO, text_color=COR_VERDE, anchor="e"
        ).pack(fill="x", pady=10)

        # Botões
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(
            btn_frame, text="🖨️  Imprimir OS", font=FONTE_GRANDE,
            fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
            height=48, corner_radius=10,
            command=lambda: print_engine.gerar_pdf_ra(ra)
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="⬅  Voltar", font=FONTE_GRANDE,
            fg_color=COR_SIDEBAR_ACTIVE, hover_color=COR_SIDEBAR_HOVER,
            height=48, corner_radius=10,
            command=self.mostrar_buscar_os
        ).pack(side="left")

    def _atualizar_status_os(self, ra):
        """Atualiza o status de uma OS."""
        try:
            novo_status = self.combo_status.get()
            if database.atualizar_status(ra, novo_status):
                messagebox.showinfo("Sucesso", f"Status da OS {ra} atualizado para '{novo_status}'.")
                self._abrir_detalhes_os(ra)
            else:
                messagebox.showerror("Erro", "Não foi possível atualizar o status.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar status: {e}")

    def _salvar_servico_realizado(self, ra):
        """Salva o campo 'serviço realizado' de uma OS."""
        try:
            texto = self.text_servico_realizado.get("1.0", END).strip()
            # Recalcula valor com peças existentes
            servico = database.obter_servico(ra)
            valor = servico.get("valor_total", 0) if servico else 0
            if database.atualizar_servico(ra, servico_realizado=texto, valor_total=valor):
                messagebox.showinfo("Sucesso", "Serviço realizado salvo com sucesso!")
            else:
                messagebox.showerror("Erro", "Não foi possível salvar.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")

    # ════════════════════════════════════════════════════════════════
    #  CLIENTES
    # ════════════════════════════════════════════════════════════════

    def mostrar_clientes(self):
        """Exibe a lista de clientes."""
        self._limpar_conteudo()
        self._atualizar_menu_ativo("Clientes")
        self.pagina_atual = "Clientes"

        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Título
        ctk.CTkLabel(
            frame, text="👥  Clientes", font=FONTE_TITULO,
            text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(0, 15))

        # Busca
        busca_frame = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=10)
        busca_frame.pack(fill="x", pady=(0, 15))
        inner = ctk.CTkFrame(busca_frame, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)

        self.busca_cli_list_var = StringVar()
        entry_busca = ctk.CTkEntry(
            inner, textvariable=self.busca_cli_list_var,
            font=FONTE_NORMAL, height=42,
            placeholder_text="Buscar por nome ou telefone..."
        )
        entry_busca.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            inner, text="🔍 Buscar", font=FONTE_NORMAL,
            fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
            height=42, width=120,
            command=self._executar_busca_clientes
        ).pack(side="right")

        # Resultados
        self.resultados_cli_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.resultados_cli_frame.pack(fill="both", expand=True)

        self._listar_clientes_todos()

    def _executar_busca_clientes(self):
        """Busca clientes pela query."""
        query = self.busca_cli_list_var.get().strip()
        if not query:
            self._listar_clientes_todos()
            return
        clientes = database.buscar_clientes(query)
        self._exibir_clientes(clientes)

    def _listar_clientes_todos(self):
        """Lista todos os clientes."""
        clientes = database.listar_todos_clientes()
        self._exibir_clientes(clientes)

    def _exibir_clientes(self, clientes):
        """Exibe a lista de clientes."""
        for w in self.resultados_cli_frame.winfo_children():
            w.destroy()

        if not clientes:
            ctk.CTkLabel(
                self.resultados_cli_frame, text="Nenhum cliente encontrado.",
                font=FONTE_NORMAL, text_color=COR_TEXTO_SEC
            ).pack(pady=20)
            return

        # Cabeçalho
        header = ctk.CTkFrame(self.resultados_cli_frame, fg_color=COR_SIDEBAR, corner_radius=8, height=40)
        header.pack(fill="x", pady=(0, 2))
        header.pack_propagate(False)

        colunas = [("Nome", 0.3), ("Telefone", 0.2), ("Documento", 0.2), ("Endereço", 0.3)]
        for text, w in colunas:
            ctk.CTkLabel(
                header, text=text, font=("Segoe UI", 12, "bold"),
                text_color=COR_TEXTO_SEC, anchor="w"
            ).place(relx=sum(c[1] for c in colunas[:colunas.index((text, w))]), rely=0.5, anchor="w", relwidth=w)

        for cli in clientes:
            row = ctk.CTkFrame(self.resultados_cli_frame, fg_color=COR_CARD, corner_radius=6, height=42)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            valores = [
                (cli.get("nome", ""), COR_TEXTO),
                (cli.get("telefone", ""), COR_TEXTO_SEC),
                (cli.get("documento", ""), COR_TEXTO_SEC),
                (cli.get("endereco", ""), COR_TEXTO_SEC),
            ]

            rx = 0.0
            for (_, w), (val, cor) in zip(colunas, valores):
                ctk.CTkLabel(
                    row, text=val, font=FONTE_PEQUENA,
                    text_color=cor, anchor="w"
                ).place(relx=rx, rely=0.5, anchor="w", relwidth=w)
                rx += w

    # ════════════════════════════════════════════════════════════════
    #  CONFIGURAÇÕES
    # ════════════════════════════════════════════════════════════════

    def mostrar_configuracoes(self):
        """Tela de configurações da empresa."""
        self._limpar_conteudo()
        self._atualizar_menu_ativo("Configurações")
        self.pagina_atual = "Configurações"

        frame = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            frame, text="⚙️  Configurações da Empresa", font=FONTE_TITULO,
            text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(
            frame, text="Esses dados aparecem no cabeçalho do PDF da OS.",
            font=FONTE_PEQUENA, text_color=COR_TEXTO_SEC, anchor="w"
        ).pack(fill="x", pady=(0, 20))

        # Card de formulário
        card = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=12)
        card.pack(fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=20)

        config_atual = carregar_config()
        self.campos_config = {}

        campos = [
            ("nome",     "Nome da Empresa *"),
            ("endereco", "Endereço"),
            ("telefone", "Telefone"),
            ("cnpj",     "CNPJ"),
        ]

        for key, label in campos:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(
                row, text=label, font=FONTE_NORMAL, text_color=COR_TEXTO,
                width=180, anchor="w"
            ).pack(side="left")
            entry = ctk.CTkEntry(row, font=FONTE_NORMAL, height=40)
            entry.pack(side="left", fill="x", expand=True)
            entry.insert(0, config_atual.get(key, ""))
            self.campos_config[key] = entry

        # Botão salvar
        ctk.CTkButton(
            inner, text="💾  Salvar Configurações",
            font=FONTE_GRANDE, fg_color=COR_VERDE, hover_color="#16a34a",
            height=48, corner_radius=10,
            command=self._salvar_configuracoes
        ).pack(anchor="e", pady=(20, 0))

        # Seção de atalhos
        ctk.CTkLabel(
            frame, text="⌨️  Atalhos de Teclado",
            font=FONTE_SUBTITULO, text_color=COR_TEXTO, anchor="w"
        ).pack(fill="x", pady=(30, 10))

        atalhos_card = ctk.CTkFrame(frame, fg_color=COR_CARD, corner_radius=12)
        atalhos_card.pack(fill="x")
        atalhos_inner = ctk.CTkFrame(atalhos_card, fg_color="transparent")
        atalhos_inner.pack(fill="x", padx=20, pady=15)

        atalhos = [
            ("F1", "Mostrar esta ajuda de atalhos"),
            ("F2", "Nova Ordem de Serviço"),
            ("F3", "Buscar OS"),
            ("F4", "Clientes"),
            ("F5", "Dashboard"),
        ]
        for tecla, descricao in atalhos:
            row = ctk.CTkFrame(atalhos_inner, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row, text=tecla,
                font=("Segoe UI", 13, "bold"), text_color=COR_AZUL,
                width=60, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=descricao,
                font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w"
            ).pack(side="left")

    def _salvar_configuracoes(self):
        """Salva as configurações da empresa."""
        nome = self.campos_config["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "O nome da empresa é obrigatório!")
            return
        dados = {k: e.get().strip() for k, e in self.campos_config.items()}
        if salvar_config(dados):
            messagebox.showinfo("Sucesso", "Configurações salvas!\nO PDF já usará os novos dados.")
        else:
            messagebox.showerror("Erro", "Não foi possível salvar as configurações.")

    def _mostrar_ajuda_atalhos(self):
        """Mostra popup com atalhos de teclado."""
        msg = (
            "ATALHOS DE TECLADO\n\n"
            "F1  →  Esta ajuda\n"
            "F2  →  Nova OS\n"
            "F3  →  Buscar OS\n"
            "F4  →  Clientes\n"
            "F5  →  Dashboard\n"
        )
        messagebox.showinfo("Atalhos de Teclado", msg)


# ════════════════════════════════════════════════════════════════
#  PONTO DE ENTRADA
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Aplica config salva ao print_engine antes de iniciar
    import print_engine as pe
    pe.EMPRESA.update(carregar_config())

    app = App()
    app.mainloop()
