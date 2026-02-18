# -*- coding: utf-8 -*-
"""
main.py — Interface Principal (CustomTkinter)
Sistema Oficina 2026 — Tema Azul + Amarelo
"""

import customtkinter as ctk
from tkinter import messagebox, StringVar, END
import database
import backup
import print_engine
from datetime import datetime
import json
import os
from theme import *

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def carregar_config():
    defaults = {"nome": "ELETRONICA EXEMPLO", "endereco": "Rua Exemplo, 123", "telefone": "(00) 0000-0000", "cnpj": "00.000.000/0001-00"}
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                defaults.update(json.load(f))
    except Exception:
        pass
    return defaults

def salvar_config(dados):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print_engine.EMPRESA.update(dados)
        return True
    except Exception:
        return False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        database.init_db()
        backup.realizar_backup()
        self.title("Sistema Oficina 2026")
        self.geometry("1300x850")
        self.minsize(1024, 700)
        self.pagina_atual = None
        self.cliente_selecionado_id = None
        self.pecas_temp = []
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._criar_sidebar()
        self._criar_area_conteudo()
        self.mostrar_dashboard()
        self.bind("<F1>", lambda e: self._mostrar_ajuda())
        self.bind("<F2>", lambda e: self.mostrar_nova_os())
        self.bind("<F3>", lambda e: self.mostrar_buscar_os())
        self.bind("<F4>", lambda e: self.mostrar_clientes())
        self.bind("<F5>", lambda e: self.mostrar_dashboard())

    # ═══════════ SIDEBAR ═══════════
    def _criar_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color=COR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(pady=(20, 25), padx=15, fill="x")
        ctk.CTkLabel(logo_f, text="Oficina 2026", font=("Segoe UI", 20, "bold"), text_color=COR_AMARELO).pack()
        ctk.CTkLabel(logo_f, text="Sistema de Gestao", font=FONTE_PEQUENA, text_color=COR_TEXTO_SEC).pack()

        # Separador amarelo
        sep = ctk.CTkFrame(self.sidebar, fg_color=COR_AMARELO, height=2)
        sep.pack(fill="x", padx=20, pady=(0, 15))

        self.menu_buttons = {}
        items = [
            ("Dashboard", self.mostrar_dashboard, "F5"),
            ("Nova OS", self.mostrar_nova_os, "F2"),
            ("Buscar OS", self.mostrar_buscar_os, "F3"),
            ("Clientes", self.mostrar_clientes, "F4"),
            ("Financeiro", self.mostrar_financeiro, ""),
            ("Configuracoes", self.mostrar_configuracoes, ""),
        ]
        for texto, cmd, atalho in items:
            f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            f.pack(fill="x", padx=8, pady=2)
            btn = ctk.CTkButton(f, text=f"  {texto}", font=FONTE_MENU, fg_color="transparent",
                                hover_color=COR_SIDEBAR_HOVER, anchor="w", height=46, corner_radius=8, command=cmd)
            btn.pack(side="left", fill="x", expand=True)
            if atalho:
                ctk.CTkLabel(f, text=atalho, font=("Segoe UI", 10), text_color=COR_TEXTO_SEC, width=30).pack(side="right", padx=5)
            self.menu_buttons[texto] = btn

        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)
        ctk.CTkButton(self.sidebar, text="Sair", font=FONTE_MENU, fg_color=COR_VERMELHO, hover_color="#dc2626",
                      height=42, corner_radius=8, command=self._sair).pack(fill="x", padx=10, pady=(5, 15))

    def _atualizar_menu_ativo(self, nome):
        for key, btn in self.menu_buttons.items():
            btn.configure(fg_color=COR_SIDEBAR_ACTIVE if key == nome else "transparent",
                          text_color=COR_SIDEBAR if key == nome else COR_TEXTO)

    def _sair(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair?"):
            self.destroy()

    def _mostrar_ajuda(self):
        messagebox.showinfo("Atalhos", "F1 = Ajuda\nF2 = Nova OS\nF3 = Buscar OS\nF4 = Clientes\nF5 = Dashboard")

    # ═══════════ CONTEUDO ═══════════
    def _criar_area_conteudo(self):
        self.content = ctk.CTkFrame(self, fg_color=COR_FUNDO, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def _limpar(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _titulo_pagina(self, frame, titulo, subtitulo=""):
        ctk.CTkLabel(frame, text=titulo, font=FONTE_TITULO, text_color=COR_AMARELO, anchor="w").pack(fill="x", pady=(0, 2))
        if subtitulo:
            ctk.CTkLabel(frame, text=subtitulo, font=FONTE_PEQUENA, text_color=COR_TEXTO_SEC, anchor="w").pack(fill="x", pady=(0, 15))

    def _secao(self, parent, titulo):
        ctk.CTkLabel(parent, text=titulo, font=FONTE_SUBTITULO, text_color=COR_AZUL, anchor="w").pack(fill="x", pady=(15, 6))
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA)
        card.pack(fill="x")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        return inner

    # ═══════════ DASHBOARD ═══════════
    def mostrar_dashboard(self):
        self._limpar()
        self._atualizar_menu_ativo("Dashboard")
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        self._titulo_pagina(f, "Dashboard", f"Hoje: {datetime.now().strftime('%d/%m/%Y')}")

        # Cards
        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(fill="x", pady=5)
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1)

        pendentes = database.contar_pendentes()
        prontos = database.contar_prontos()
        contagens = database.contar_por_status()
        aguardando = contagens.get("Aguardando Peça", 0)
        resumo = database.resumo_financeiro_mes()

        dados_cards = [
            ("Pendentes", str(pendentes), COR_AMARELO, "Em aberto"),
            ("Prontos", str(prontos), COR_VERDE, "Para retirar"),
            ("Aguardando", str(aguardando), COR_AZUL, "Falta peca"),
            ("Faturado", f"R$ {resumo['faturado']:.0f}", COR_DESTAQUE, "Este mes"),
        ]
        for i, (t, v, cor, sub) in enumerate(dados_cards):
            card = ctk.CTkFrame(cards, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA, height=130)
            card.grid(row=0, column=i, padx=6, pady=5, sticky="nsew")
            card.grid_propagate(False)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(inner, text=v, font=FONTE_CARD_NUM, text_color=cor).pack()
            ctk.CTkLabel(inner, text=t, font=FONTE_NORMAL, text_color=COR_TEXTO).pack()
            ctk.CTkLabel(inner, text=sub, font=("Segoe UI", 10), text_color=COR_TEXTO_SEC).pack()

        # Tabela de OS recentes
        ctk.CTkLabel(f, text="Ultimas Ordens de Servico", font=FONTE_SUBTITULO, text_color=COR_AZUL, anchor="w").pack(fill="x", pady=(20, 8))
        servicos = database.listar_servicos()[:15]
        if servicos:
            self._tabela_servicos(f, servicos)
        else:
            ctk.CTkLabel(f, text="Nenhuma OS cadastrada.", font=FONTE_NORMAL, text_color=COR_TEXTO_SEC).pack(pady=20)

    def _tabela_servicos(self, parent, servicos, com_acoes=False):
        header = ctk.CTkFrame(parent, fg_color=COR_SIDEBAR, corner_radius=8, height=38)
        header.pack(fill="x", pady=(0, 2))
        header.pack_propagate(False)
        cols = [("RA", 0.1), ("Cliente", 0.2), ("Aparelho", 0.14), ("Status", 0.12), ("Valor", 0.1), ("Pgto", 0.1), ("Data", 0.1)]
        if com_acoes:
            cols.append(("Acoes", 0.14))
        rx = 0.01
        for text, w in cols:
            ctk.CTkLabel(header, text=text, font=("Segoe UI", 11, "bold"), text_color=COR_AMARELO, anchor="w").place(relx=rx, rely=0.5, anchor="w", relwidth=w)
            rx += w

        for srv in servicos:
            row = ctk.CTkFrame(parent, fg_color=COR_CARD, corner_radius=6, height=40)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            st = srv.get("status", "")
            st_cor = {"Aberto": COR_AMARELO, "Aguardando Peca": COR_AZUL, "Pronto": COR_VERDE, "Entregue": COR_TEXTO_SEC}.get(st, COR_TEXTO)
            vf = srv.get("valor_final", 0) or srv.get("valor_total", 0) or 0
            vals = [
                (srv.get("ra", ""), COR_DESTAQUE), (srv.get("cliente_nome", ""), COR_TEXTO),
                (srv.get("aparelho", ""), COR_TEXTO), (st, st_cor),
                (f"R$ {vf:.2f}", COR_VERDE), (srv.get("forma_pagamento", "") or "-", COR_TEXTO_SEC),
                (srv.get("data_entrada", ""), COR_TEXTO_SEC),
            ]
            rx = 0.01
            for (_, w), (val, cor) in zip(cols[:7], vals):
                ctk.CTkLabel(row, text=val, font=FONTE_PEQUENA, text_color=cor, anchor="w").place(relx=rx, rely=0.5, anchor="w", relwidth=w)
                rx += w
            if com_acoes:
                af = ctk.CTkFrame(row, fg_color="transparent")
                af.place(relx=rx, rely=0.5, anchor="w", relwidth=0.14, relheight=0.9)
                ra = srv.get("ra", "")
                ctk.CTkButton(af, text="Ver", width=40, height=26, font=("Segoe UI", 11), fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER,
                              command=lambda r=ra: self._abrir_detalhes_os(r)).pack(side="left", padx=2)
                ctk.CTkButton(af, text="PDF", width=40, height=26, font=("Segoe UI", 11), fg_color=COR_SIDEBAR_HOVER, hover_color=COR_SIDEBAR,
                              command=lambda r=ra: print_engine.gerar_pdf_ra(r)).pack(side="left", padx=2)

    # ═══════════ NOVA OS ═══════════
    def mostrar_nova_os(self):
        self._limpar()
        self._atualizar_menu_ativo("Nova OS")
        self.cliente_selecionado_id = None
        self.pecas_temp = []
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        self.ra_atual = database.gerar_ra()
        self._titulo_pagina(f, "Nova Ordem de Servico", f"RA: {self.ra_atual}")

        # === CLIENTE ===
        sec = self._secao(f, "Cliente")
        self.busca_cliente_var = StringVar()
        self.busca_cliente_var.trace_add("write", self._ao_buscar_cliente)
        self.entry_busca_cli = ctk.CTkEntry(sec, textvariable=self.busca_cliente_var, font=FONTE_NORMAL, height=40, placeholder_text="Buscar cliente por nome ou telefone...")
        self.entry_busca_cli.pack(fill="x", pady=(0, 5))
        self.lista_clientes_frame = ctk.CTkFrame(sec, fg_color=COR_CARD_HOVER, corner_radius=8)
        self.label_cliente_sel = ctk.CTkLabel(sec, text="Nenhum cliente selecionado", font=FONTE_NORMAL, text_color=COR_AMARELO, anchor="w")
        self.label_cliente_sel.pack(fill="x", pady=3)
        ctk.CTkButton(sec, text="+ Novo Cliente", font=FONTE_NORMAL, fg_color=COR_AZUL, hover_color=COR_AZUL_HOVER, height=36, command=self._toggle_novo_cli).pack(anchor="w", pady=3)
        self.form_cli = ctk.CTkFrame(sec, fg_color=COR_CARD_HOVER, corner_radius=8)
        self.campos_cli = {}
        for key, label in [("nome", "Nome *"), ("telefone", "Telefone"), ("documento", "CPF/CNPJ"), ("endereco", "Endereco")]:
            r = ctk.CTkFrame(self.form_cli, fg_color="transparent")
            r.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(r, text=label, font=FONTE_NORMAL, text_color=COR_TEXTO, width=100, anchor="w").pack(side="left")
            e = ctk.CTkEntry(r, font=FONTE_NORMAL, height=36)
            e.pack(side="left", fill="x", expand=True)
            self.campos_cli[key] = e
        ctk.CTkButton(self.form_cli, text="Salvar Cliente", font=FONTE_NORMAL, fg_color=COR_VERDE, hover_color="#16a34a", height=36, command=self._salvar_cli_inline).pack(padx=10, pady=8, anchor="e")
        self.form_cli_vis = False

        # === APARELHO ===
        sec_ap = self._secao(f, "Aparelho")
        self.campos_ap = {}
        grid = ctk.CTkFrame(sec_ap, fg_color="transparent")
        grid.pack(fill="x")
        grid.grid_columnconfigure((0, 1), weight=1)
        for i, (key, label) in enumerate([("aparelho", "Aparelho *"), ("marca", "Marca"), ("modelo", "Modelo"), ("numero_serie", "N Serie")]):
            r, c = divmod(i, 2)
            cell = ctk.CTkFrame(grid, fg_color="transparent")
            cell.grid(row=r, column=c, padx=4, pady=3, sticky="ew")
            ctk.CTkLabel(cell, text=label, font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").pack(anchor="w")
            e = ctk.CTkEntry(cell, font=FONTE_NORMAL, height=36)
            e.pack(fill="x")
            self.campos_ap[key] = e
        ctk.CTkLabel(sec_ap, text="Defeito Relatado:", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").pack(fill="x", pady=(8, 2))
        self.text_defeito = ctk.CTkTextbox(sec_ap, font=FONTE_NORMAL, height=70, corner_radius=8)
        self.text_defeito.pack(fill="x")

        # === OBSERVACOES ===
        ctk.CTkLabel(sec_ap, text="Observacoes Internas:", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").pack(fill="x", pady=(8, 2))
        self.text_obs = ctk.CTkTextbox(sec_ap, font=FONTE_NORMAL, height=50, corner_radius=8)
        self.text_obs.pack(fill="x")

        # === PECAS ===
        sec_pc = self._secao(f, "Pecas / Servicos")
        pr = ctk.CTkFrame(sec_pc, fg_color="transparent")
        pr.pack(fill="x")
        pr.grid_columnconfigure(0, weight=3)
        pr.grid_columnconfigure(1, weight=1)
        self.entry_peca_desc = ctk.CTkEntry(pr, font=FONTE_NORMAL, height=36, placeholder_text="Descricao")
        self.entry_peca_desc.grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self.entry_peca_valor = ctk.CTkEntry(pr, font=FONTE_NORMAL, height=36, placeholder_text="Valor R$")
        self.entry_peca_valor.grid(row=0, column=1, padx=(0, 4), sticky="ew")
        ctk.CTkButton(pr, text="+", font=FONTE_NORMAL, width=45, fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER, text_color=COR_SIDEBAR, height=36, command=self._add_peca).grid(row=0, column=2)
        self.pecas_frame = ctk.CTkFrame(sec_pc, fg_color="transparent")
        self.pecas_frame.pack(fill="x", pady=8)
        self.label_total = ctk.CTkLabel(sec_pc, text="Total: R$ 0,00", font=FONTE_SUBTITULO, text_color=COR_VERDE, anchor="e")
        self.label_total.pack(fill="x")

        # === PAGAMENTO ===
        sec_pg = self._secao(f, "Pagamento")
        pg_row = ctk.CTkFrame(sec_pg, fg_color="transparent")
        pg_row.pack(fill="x")
        pg_row.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(pg_row, text="Forma:", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").grid(row=0, column=0, sticky="w", padx=4)
        self.combo_pgto = ctk.CTkComboBox(pg_row, values=[""] + FORMAS_PAGAMENTO, font=FONTE_NORMAL, height=36, dropdown_font=FONTE_NORMAL, command=self._on_pgto_change)
        self.combo_pgto.grid(row=1, column=0, padx=4, sticky="ew")
        self.combo_pgto.set("")
        ctk.CTkLabel(pg_row, text="Desconto R$:", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").grid(row=0, column=1, sticky="w", padx=4)
        self.entry_desconto = ctk.CTkEntry(pg_row, font=FONTE_NORMAL, height=36, placeholder_text="0.00")
        self.entry_desconto.grid(row=1, column=1, padx=4, sticky="ew")
        self.entry_desconto.bind("<KeyRelease>", lambda e: self._recalc_final())
        self.label_sugestao = ctk.CTkLabel(pg_row, text="", font=("Segoe UI", 11), text_color=COR_AMARELO, anchor="w")
        self.label_sugestao.grid(row=2, column=0, columnspan=2, sticky="w", padx=4, pady=(4, 0))
        ctk.CTkLabel(pg_row, text="Valor Final:", font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").grid(row=0, column=2, sticky="w", padx=4)
        self.label_final = ctk.CTkLabel(pg_row, text="R$ 0,00", font=("Segoe UI", 18, "bold"), text_color=COR_AMARELO, anchor="w")
        self.label_final.grid(row=1, column=2, sticky="w", padx=4)

        # === BOTOES ===
        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(fill="x", pady=15)
        ctk.CTkButton(btns, text="Salvar OS", font=FONTE_GRANDE, fg_color=COR_VERDE, hover_color="#16a34a", height=48, corner_radius=10, command=self._salvar_os).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Salvar e Imprimir", font=FONTE_GRANDE, fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER, text_color=COR_SIDEBAR, height=48, corner_radius=10, command=lambda: self._salvar_os(imprimir=True)).pack(side="left")

    def _on_pgto_change(self, valor):
        if valor in DESCONTOS_SUGERIDOS:
            total = sum(v for _, v in self.pecas_temp)
            pct = DESCONTOS_SUGERIDOS[valor]
            desc_sugerido = round(total * pct / 100, 2)
            self.label_sugestao.configure(text=f"Sugestao: {pct}% de desconto = R$ {desc_sugerido:.2f} (pagamento {valor})")
            self.entry_desconto.delete(0, END)
            self.entry_desconto.insert(0, f"{desc_sugerido:.2f}")
        else:
            self.label_sugestao.configure(text="")
        self._recalc_final()

    def _recalc_final(self):
        total = sum(v for _, v in self.pecas_temp)
        try:
            desc = float(self.entry_desconto.get().replace(",", ".")) if self.entry_desconto.get().strip() else 0
        except ValueError:
            desc = 0
        final = max(total - desc, 0)
        self.label_final.configure(text=f"R$ {final:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def _ao_buscar_cliente(self, *a):
        q = self.busca_cliente_var.get().strip()
        for w in self.lista_clientes_frame.winfo_children():
            w.destroy()
        if len(q) < 2:
            self.lista_clientes_frame.pack_forget()
            return
        res = database.buscar_clientes(q)
        if not res:
            self.lista_clientes_frame.pack_forget()
            return
        self.lista_clientes_frame.pack(fill="x", pady=2)
        for cli in res[:8]:
            ctk.CTkButton(self.lista_clientes_frame, text=f"  {cli['nome']}  -  {cli.get('telefone', '')}", font=FONTE_NORMAL, fg_color="transparent", hover_color=COR_SIDEBAR_HOVER, anchor="w", height=34, command=lambda c=cli: self._sel_cli(c)).pack(fill="x", padx=4, pady=1)

    def _sel_cli(self, cli):
        self.cliente_selecionado_id = cli["id"]
        self.label_cliente_sel.configure(text=f"OK: {cli['nome']}  |  Tel: {cli.get('telefone', '')}  |  Doc: {cli.get('documento', '')}", text_color=COR_VERDE)
        self.lista_clientes_frame.pack_forget()
        self.busca_cliente_var.set("")

    def _toggle_novo_cli(self):
        if self.form_cli_vis:
            self.form_cli.pack_forget()
        else:
            self.form_cli.pack(fill="x", pady=8)
        self.form_cli_vis = not self.form_cli_vis

    def _salvar_cli_inline(self):
        nome = self.campos_cli["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Atencao", "Nome obrigatorio!")
            return
        try:
            cid = database.salvar_cliente(nome, self.campos_cli["endereco"].get().strip(), self.campos_cli["telefone"].get().strip(), self.campos_cli["documento"].get().strip())
            if cid:
                self.cliente_selecionado_id = cid
                self.label_cliente_sel.configure(text=f"OK: {nome}", text_color=COR_VERDE)
                self.form_cli.pack_forget()
                self.form_cli_vis = False
                for e in self.campos_cli.values():
                    e.delete(0, END)
                messagebox.showinfo("OK", f"Cliente '{nome}' cadastrado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")

    def _add_peca(self):
        desc = self.entry_peca_desc.get().strip()
        vs = self.entry_peca_valor.get().strip().replace(",", ".")
        if not desc:
            return
        try:
            v = float(vs) if vs else 0
        except ValueError:
            messagebox.showwarning("Atencao", "Valor invalido!")
            return
        self.pecas_temp.append((desc, v))
        self._refresh_pecas()
        self.entry_peca_desc.delete(0, END)
        self.entry_peca_valor.delete(0, END)
        self.entry_peca_desc.focus()

    def _refresh_pecas(self):
        for w in self.pecas_frame.winfo_children():
            w.destroy()
        total = 0
        for i, (d, v) in enumerate(self.pecas_temp):
            r = ctk.CTkFrame(self.pecas_frame, fg_color=COR_CARD_HOVER, corner_radius=6, height=34)
            r.pack(fill="x", pady=1)
            r.pack_propagate(False)
            ctk.CTkLabel(r, text=f"  {d}", font=FONTE_PEQUENA, text_color=COR_TEXTO, anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(r, text=f"R$ {v:.2f}", font=FONTE_PEQUENA, text_color=COR_VERDE).pack(side="left", padx=8)
            ctk.CTkButton(r, text="X", width=28, height=26, fg_color=COR_VERMELHO, hover_color="#dc2626", font=("Segoe UI", 11, "bold"), command=lambda idx=i: self._rm_peca(idx)).pack(side="right", padx=4)
            total += v
        self.label_total.configure(text=f"Total: R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self._recalc_final()

    def _rm_peca(self, idx):
        if 0 <= idx < len(self.pecas_temp):
            self.pecas_temp.pop(idx)
            self._refresh_pecas()

    def _salvar_os(self, imprimir=False):
        if not self.cliente_selecionado_id:
            messagebox.showwarning("Atencao", "Selecione ou cadastre um cliente!")
            return
        ap = self.campos_ap["aparelho"].get().strip()
        if not ap:
            messagebox.showwarning("Atencao", "Informe o aparelho!")
            return
        try:
            total = sum(v for _, v in self.pecas_temp)
            try:
                desc = float(self.entry_desconto.get().replace(",", ".")) if self.entry_desconto.get().strip() else 0
            except ValueError:
                desc = 0
            final = max(total - desc, 0)
            pgto = self.combo_pgto.get().strip()
            obs = self.text_obs.get("1.0", END).strip()
            ok = database.salvar_servico(
                ra=self.ra_atual, cliente_id=self.cliente_selecionado_id, aparelho=ap,
                marca=self.campos_ap["marca"].get().strip(), modelo=self.campos_ap["modelo"].get().strip(),
                numero_serie=self.campos_ap["numero_serie"].get().strip(), defeito_relatado=self.text_defeito.get("1.0", END).strip(),
                valor_total=total, desconto=desc, valor_final=final, forma_pagamento=pgto, observacoes=obs,
            )
            if not ok:
                messagebox.showerror("Erro", "Falha ao salvar OS!")
                return
            for d, v in self.pecas_temp:
                database.adicionar_peca(self.ra_atual, d, v)
            messagebox.showinfo("OK", f"OS {self.ra_atual} salva!")
            if imprimir:
                print_engine.gerar_pdf_ra(self.ra_atual)
            self.mostrar_dashboard()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")

    # ═══════════ BUSCAR OS ═══════════
    def mostrar_buscar_os(self):
        self._limpar()
        self._atualizar_menu_ativo("Buscar OS")
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        self._titulo_pagina(f, "Buscar OS")
        bf = ctk.CTkFrame(f, fg_color=COR_CARD, corner_radius=10, border_width=1, border_color=COR_BORDA)
        bf.pack(fill="x", pady=(0, 10))
        bi = ctk.CTkFrame(bf, fg_color="transparent")
        bi.pack(fill="x", padx=12, pady=10)
        self.busca_os_var = StringVar()
        e = ctk.CTkEntry(bi, textvariable=self.busca_os_var, font=FONTE_NORMAL, height=40, placeholder_text="RA ou nome do cliente...")
        e.pack(side="left", fill="x", expand=True, padx=(0, 8))
        e.bind("<Return>", lambda ev: self._exec_busca_os())
        ctk.CTkButton(bi, text="Buscar", font=FONTE_NORMAL, fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER, text_color=COR_SIDEBAR, height=40, width=100, command=self._exec_busca_os).pack(side="right")
        filtros = ctk.CTkFrame(f, fg_color="transparent")
        filtros.pack(fill="x", pady=(0, 10))
        for s, cor in [("Todos", COR_TEXTO_SEC), ("Aberto", COR_AMARELO), ("Aguardando Peca", COR_AZUL), ("Pronto", COR_VERDE), ("Entregue", COR_TEXTO_SEC)]:
            ctk.CTkButton(filtros, text=s, font=FONTE_PEQUENA, fg_color=COR_CARD, hover_color=COR_CARD_HOVER, text_color=cor, height=32, corner_radius=20, command=lambda st=s: self._filtrar_os(st)).pack(side="left", padx=3)
        self.res_os_frame = ctk.CTkFrame(f, fg_color="transparent")
        self.res_os_frame.pack(fill="both", expand=True)
        self._filtrar_os("Todos")

    def _exec_busca_os(self):
        q = self.busca_os_var.get().strip()
        if not q:
            self._filtrar_os("Todos")
            return
        self._mostrar_res_os(database.buscar_servicos(q))

    def _filtrar_os(self, st):
        self._mostrar_res_os(database.listar_servicos() if st == "Todos" else database.listar_servicos(st))

    def _mostrar_res_os(self, servicos):
        for w in self.res_os_frame.winfo_children():
            w.destroy()
        if not servicos:
            ctk.CTkLabel(self.res_os_frame, text="Nenhuma OS encontrada.", font=FONTE_NORMAL, text_color=COR_TEXTO_SEC).pack(pady=20)
            return
        self._tabela_servicos(self.res_os_frame, servicos, com_acoes=True)

    def _abrir_detalhes_os(self, ra):
        srv = database.obter_servico(ra)
        if not srv:
            return
        self._limpar()
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        self._titulo_pagina(f, f"OS: {ra}", f"Status: {srv.get('status', '')}  |  Data: {srv.get('data_entrada', '')}")
        sec = self._secao(f, "Detalhes")
        for label, val in [("Cliente", srv.get("cliente_nome", "")), ("Telefone", srv.get("cliente_telefone", "")), ("Aparelho", srv.get("aparelho", "")),
                           ("Marca/Modelo", f"{srv.get('marca', '')} {srv.get('modelo', '')}"), ("Defeito", srv.get("defeito_relatado", "")),
                           ("Pagamento", srv.get("forma_pagamento", "") or "-"), ("Desconto", f"R$ {srv.get('desconto', 0):.2f}"), ("Valor Final", f"R$ {srv.get('valor_final', 0):.2f}")]:
            r = ctk.CTkFrame(sec, fg_color="transparent")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{label}:", font=("Segoe UI", 13, "bold"), text_color=COR_AZUL, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(r, text=val, font=FONTE_NORMAL, text_color=COR_TEXTO, anchor="w").pack(side="left", fill="x", expand=True)
        # Status update
        sec2 = self._secao(f, "Alterar Status")
        st_frame = ctk.CTkFrame(sec2, fg_color="transparent")
        st_frame.pack(fill="x")
        for st in ["Aberto", "Aguardando Peca", "Pronto", "Entregue"]:
            cor = {"Aberto": COR_AMARELO, "Aguardando Peca": COR_AZUL, "Pronto": COR_VERDE, "Entregue": COR_TEXTO_SEC}.get(st, COR_TEXTO)
            ctk.CTkButton(st_frame, text=st, font=FONTE_NORMAL, fg_color=COR_CARD, hover_color=cor, text_color=cor, height=36, corner_radius=8,
                          command=lambda s=st: self._mudar_status(ra, s)).pack(side="left", padx=4)
        # Print
        ctk.CTkButton(f, text="Imprimir PDF", font=FONTE_GRANDE, fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER, text_color=COR_SIDEBAR, height=46, corner_radius=10,
                      command=lambda: print_engine.gerar_pdf_ra(ra)).pack(pady=15, anchor="w")
        ctk.CTkButton(f, text="Voltar", font=FONTE_NORMAL, fg_color=COR_CARD, hover_color=COR_CARD_HOVER, height=36, command=self.mostrar_buscar_os).pack(anchor="w")

    def _mudar_status(self, ra, st):
        if database.atualizar_status(ra, st):
            messagebox.showinfo("OK", f"Status alterado para: {st}")
            self._abrir_detalhes_os(ra)

    # ═══════════ CLIENTES ═══════════
    def mostrar_clientes(self):
        self._limpar()
        self._atualizar_menu_ativo("Clientes")
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        self._titulo_pagina(f, "Clientes")
        clientes = database.listar_todos_clientes()
        if not clientes:
            ctk.CTkLabel(f, text="Nenhum cliente cadastrado.", font=FONTE_NORMAL, text_color=COR_TEXTO_SEC).pack(pady=20)
            return
        h = ctk.CTkFrame(f, fg_color=COR_SIDEBAR, corner_radius=8, height=38)
        h.pack(fill="x", pady=(0, 2))
        h.pack_propagate(False)
        for text, rx, w in [("Nome", 0.01, 0.3), ("Telefone", 0.31, 0.2), ("Documento", 0.51, 0.2), ("Endereco", 0.71, 0.28)]:
            ctk.CTkLabel(h, text=text, font=("Segoe UI", 11, "bold"), text_color=COR_AMARELO, anchor="w").place(relx=rx, rely=0.5, anchor="w", relwidth=w)
        for cli in clientes:
            row = ctk.CTkFrame(f, fg_color=COR_CARD, corner_radius=6, height=38)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)
            for val, rx, w, cor in [(cli.get("nome", ""), 0.01, 0.3, COR_TEXTO), (cli.get("telefone", ""), 0.31, 0.2, COR_TEXTO_SEC),
                                     (cli.get("documento", ""), 0.51, 0.2, COR_TEXTO_SEC), (cli.get("endereco", ""), 0.71, 0.28, COR_TEXTO_SEC)]:
                ctk.CTkLabel(row, text=val, font=FONTE_PEQUENA, text_color=cor, anchor="w").place(relx=rx, rely=0.5, anchor="w", relwidth=w)

    # ═══════════ FINANCEIRO ═══════════
    def mostrar_financeiro(self):
        self._limpar()
        self._atualizar_menu_ativo("Financeiro")
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        agora = datetime.now()
        self._titulo_pagina(f, "Painel Financeiro", f"{MESES_PT.get(agora.month, '')} {agora.year}")

        resumo = database.resumo_financeiro_mes()
        # Cards
        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(fill="x", pady=5)
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for i, (t, v, cor) in enumerate([
            ("Faturado", f"R$ {resumo['faturado']:,.0f}".replace(",", "."), COR_AMARELO),
            ("Bruto", f"R$ {resumo['bruto']:,.0f}".replace(",", "."), COR_AZUL),
            ("Descontos", f"R$ {resumo['descontos']:,.0f}".replace(",", "."), COR_VERMELHO),
            ("Total OS", str(resumo["total_os"]), COR_VERDE),
        ]):
            card = ctk.CTkFrame(cards, fg_color=COR_CARD, corner_radius=12, border_width=1, border_color=COR_BORDA, height=110)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            card.grid_propagate(False)
            inn = ctk.CTkFrame(card, fg_color="transparent")
            inn.place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(inn, text=v, font=("Segoe UI", 24, "bold"), text_color=cor).pack()
            ctk.CTkLabel(inn, text=t, font=FONTE_NORMAL, text_color=COR_TEXTO).pack()

        # Pagamentos
        sec = self._secao(f, "Por Forma de Pagamento")
        pgtos = resumo.get("por_pagamento", [])
        if pgtos:
            for pg in pgtos:
                r = ctk.CTkFrame(sec, fg_color="transparent")
                r.pack(fill="x", pady=3)
                ctk.CTkLabel(r, text=pg.get("forma_pagamento", "N/A"), font=FONTE_NORMAL, text_color=COR_AMARELO, width=150, anchor="w").pack(side="left")
                ctk.CTkLabel(r, text=f"{pg.get('qtd', 0)} OS", font=FONTE_NORMAL, text_color=COR_TEXTO_SEC, width=80).pack(side="left")
                ctk.CTkLabel(r, text=f"R$ {pg.get('total', 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), font=("Segoe UI", 14, "bold"), text_color=COR_VERDE, anchor="e").pack(side="right")
        else:
            ctk.CTkLabel(sec, text="Nenhum pagamento registrado este mes.", font=FONTE_NORMAL, text_color=COR_TEXTO_SEC).pack(pady=10)

        # Historico
        sec2 = self._secao(f, "Ultimos 6 Meses")
        hist = database.faturamento_ultimos_meses(6)
        if hist:
            max_val = max((h.get("total", 0) for h in hist), default=1) or 1
            for h in hist:
                r = ctk.CTkFrame(sec2, fg_color="transparent")
                r.pack(fill="x", pady=3)
                ctk.CTkLabel(r, text=h.get("mes", ""), font=FONTE_NORMAL, text_color=COR_TEXTO, width=80, anchor="w").pack(side="left")
                # Barra visual
                pct = h.get("total", 0) / max_val
                bar_f = ctk.CTkFrame(r, fg_color=COR_CARD_HOVER, corner_radius=4, height=24)
                bar_f.pack(side="left", fill="x", expand=True, padx=8)
                bar_f.pack_propagate(False)
                bar = ctk.CTkFrame(bar_f, fg_color=COR_AMARELO, corner_radius=4)
                bar.place(relx=0, rely=0, relwidth=max(pct, 0.02), relheight=1)
                ctk.CTkLabel(r, text=f"R$ {h.get('total', 0):,.0f}".replace(",", "."), font=("Segoe UI", 12, "bold"), text_color=COR_VERDE, width=100, anchor="e").pack(side="right")
                ctk.CTkLabel(r, text=f"({h.get('qtd_os', 0)} OS)", font=("Segoe UI", 10), text_color=COR_TEXTO_SEC, width=60).pack(side="right")

    # ═══════════ CONFIGURACOES ═══════════
    def mostrar_configuracoes(self):
        self._limpar()
        self._atualizar_menu_ativo("Configuracoes")
        f = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=25, pady=15)
        self._titulo_pagina(f, "Configuracoes", "Dados que aparecem no PDF")
        sec = self._secao(f, "Dados da Empresa")
        cfg = carregar_config()
        self.campos_cfg = {}
        for key, label in [("nome", "Nome *"), ("endereco", "Endereco"), ("telefone", "Telefone"), ("cnpj", "CNPJ")]:
            r = ctk.CTkFrame(sec, fg_color="transparent")
            r.pack(fill="x", pady=5)
            ctk.CTkLabel(r, text=label, font=FONTE_NORMAL, text_color=COR_TEXTO, width=150, anchor="w").pack(side="left")
            e = ctk.CTkEntry(r, font=FONTE_NORMAL, height=38)
            e.pack(side="left", fill="x", expand=True)
            e.insert(0, cfg.get(key, ""))
            self.campos_cfg[key] = e
        ctk.CTkButton(sec, text="Salvar", font=FONTE_GRANDE, fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER, text_color=COR_SIDEBAR, height=46, corner_radius=10, command=self._salvar_cfg).pack(anchor="e", pady=(15, 0))

    def _salvar_cfg(self):
        nome = self.campos_cfg["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Atencao", "Nome obrigatorio!")
            return
        dados = {k: e.get().strip() for k, e in self.campos_cfg.items()}
        if salvar_config(dados):
            messagebox.showinfo("OK", "Configuracoes salvas! PDF atualizado.")
        else:
            messagebox.showerror("Erro", "Falha ao salvar.")


# ═══════════ PONTO DE ENTRADA ═══════════
if __name__ == "__main__":
    print_engine.EMPRESA.update(carregar_config())
    app = App()
    app.mainloop()
