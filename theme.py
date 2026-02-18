# -*- coding: utf-8 -*-
"""
theme.py — Tema visual e constantes do Sistema Oficina 2026
"""

# Cores do tema (Azul + Amarelo Premium)
COR_SIDEBAR = "#0d1b2a"
COR_SIDEBAR_HOVER = "#1b3a5c"
COR_SIDEBAR_ACTIVE = "#f5a623"
COR_FUNDO = "#101c2c"
COR_CARD = "#162236"
COR_CARD_HOVER = "#1e3050"
COR_AZUL = "#2d7dd2"
COR_AZUL_HOVER = "#1b5fa0"
COR_AMARELO = "#f5a623"
COR_AMARELO_HOVER = "#d4901f"
COR_VERDE = "#22c55e"
COR_VERMELHO = "#ef4444"
COR_TEXTO = "#e8ecf1"
COR_TEXTO_SEC = "#8899aa"
COR_BORDA = "#2a3f55"
COR_DESTAQUE = "#f5a623"

# Fontes
FONTE_TITULO = ("Segoe UI", 22, "bold")
FONTE_SUBTITULO = ("Segoe UI", 16, "bold")
FONTE_NORMAL = ("Segoe UI", 14)
FONTE_GRANDE = ("Segoe UI", 18)
FONTE_PEQUENA = ("Segoe UI", 12)
FONTE_MENU = ("Segoe UI", 15, "bold")
FONTE_CARD_NUM = ("Segoe UI", 38, "bold")

# Formas de pagamento
FORMAS_PAGAMENTO = [
    "PIX",
    "Dinheiro",
    "Cartao Credito",
    "Cartao Debito",
    "Transferencia",
    "Boleto",
    "Cheque",
]

# Descontos sugeridos por forma de pagamento (%)
DESCONTOS_SUGERIDOS = {
    "PIX": 5.0,
    "Dinheiro": 3.0,
    "Transferencia": 3.0,
}

MESES_PT = {
    1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
    5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Set", 10: "Out", 11: "Nov", 12: "Dez",
}
