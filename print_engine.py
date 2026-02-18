# -*- coding: utf-8 -*-
"""
print_engine.py — Gerador de PDF para OS (ReportLab)
Sistema Oficina 2026

PDF A4 com duas vias: Loja (superior) + Cliente (inferior).
Layout profissional com cores azul e amarelo.
"""

import os
import sys
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from database import obter_servico, listar_pecas

# ──────────────────────────── CONSTANTES ────────────────────────────

PAGE_W, PAGE_H = A4
HALF_H = PAGE_H / 2
M = 12 * mm          # margem
CW = PAGE_W - 2 * M  # largura útil

# Cores (tema azul + amarelo)
AZUL_ESCURO = HexColor("#0d1b2a")
AZUL        = HexColor("#1b3a5c")
AZUL_CLARO  = HexColor("#2d5a8e")
AMARELO     = HexColor("#f5a623")
CINZA       = HexColor("#888888")
CINZA_CLARO = HexColor("#e8eef5")
BRANCO      = white

# Dados da empresa (sobrescritos pelo config.json via main.py)
EMPRESA = {
    "nome": "ELETRONICA EXEMPLO",
    "endereco": "Rua Exemplo, 123 - Centro - Cidade/UF",
    "telefone": "(00) 0000-0000",
    "cnpj": "00.000.000/0001-00",
}

TERMO_GARANTIA = (
    "TERMO DE GARANTIA: Garantia de 90 dias a partir da data de entrega, conforme CDC (Lei 8.078/90). "
    "Nao cobre defeitos por mau uso, quedas, oscilacao de energia ou violacao por terceiros. "
    "Aparelhos nao retirados em 90 dias apos conclusao serao considerados abandonados (Art. 1.275 CC)."
)

PDF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PDFs")


def _garantir_diretorio():
    if not os.path.exists(PDF_DIR):
        os.makedirs(PDF_DIR)


def _safe(text):
    """Remove caracteres problematicos para Helvetica."""
    if not text:
        return ""
    replacements = {
        '\u2014': '-', '\u2013': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u2022': '*',
        '\u00e7': 'c', '\u00c7': 'C',
        '\u00e3': 'a', '\u00c3': 'A',
        '\u00e1': 'a', '\u00c1': 'A',
        '\u00e9': 'e', '\u00c9': 'E',
        '\u00ed': 'i', '\u00cd': 'I',
        '\u00f3': 'o', '\u00d3': 'O',
        '\u00fa': 'u', '\u00da': 'U',
        '\u00ea': 'e', '\u00ca': 'E',
        '\u00f4': 'o', '\u00d4': 'O',
        '\u00e2': 'a', '\u00c2': 'A',
        '\u00f5': 'o', '\u00d5': 'O',
        '\u00e0': 'a', '\u00c0': 'A',
        '\u00fc': 'u', '\u00dc': 'U',
        '\u00b0': 'o',
    }
    result = str(text)
    for orig, repl in replacements.items():
        result = result.replace(orig, repl)
    # Remove qualquer char acima de 127 restante
    result = result.encode('ascii', 'replace').decode('ascii')
    return result


def gerar_pdf_ra(ra_numero):
    """Gera PDF da OS. Retorna caminho ou None."""
    try:
        servico = obter_servico(ra_numero)
        if not servico:
            print(f"[PDF] Servico RA {ra_numero} nao encontrado.")
            return None

        pecas = listar_pecas(ra_numero)
        _garantir_diretorio()
        pdf_path = os.path.join(PDF_DIR, f"OS_{ra_numero}.pdf")

        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.setTitle(f"OS {ra_numero}")

        _desenhar_via(c, servico, pecas, y_offset=HALF_H, via_label="VIA DA LOJA")
        _desenhar_via(c, servico, pecas, y_offset=0, via_label="VIA DO CLIENTE")

        # Linha de corte
        c.setStrokeColor(CINZA)
        c.setDash(4, 3)
        c.setLineWidth(0.5)
        c.line(M, HALF_H, PAGE_W - M, HALF_H)
        c.setFont("Helvetica", 6)
        c.setFillColor(CINZA)
        c.drawCentredString(PAGE_W / 2, HALF_H + 1.5 * mm, "CORTE AQUI")

        c.save()
        print(f"[PDF] OK: {pdf_path}")
        _abrir_pdf(pdf_path)
        return pdf_path

    except Exception as e:
        print(f"[PDF] Erro: {e}")
        import traceback
        traceback.print_exc()
        return None


def _desenhar_via(c, servico, pecas, y_offset, via_label):
    """Desenha uma via completa (metade da pagina)."""
    x = M
    y_top = y_offset + HALF_H - M
    y = y_top

    # ─── FAIXA HEADER ───
    header_h = 20 * mm
    # Fundo azul escuro
    c.setFillColor(AZUL_ESCURO)
    c.roundRect(x, y - header_h, CW, header_h, 3 * mm, fill=1, stroke=0)

    # Faixa amarela lateral
    c.setFillColor(AMARELO)
    c.rect(x, y - header_h, 5 * mm, header_h, fill=1, stroke=0)

    # Nome da empresa
    c.setFillColor(BRANCO)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x + 8 * mm, y - 7 * mm, _safe(EMPRESA["nome"]))

    # Dados da empresa
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#cccccc"))
    c.drawString(x + 8 * mm, y - 11.5 * mm, _safe(f'{EMPRESA["endereco"]}  |  Tel: {EMPRESA["telefone"]}'))
    c.drawString(x + 8 * mm, y - 15 * mm, _safe(f'CNPJ: {EMPRESA["cnpj"]}'))

    # Via label
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(AMARELO)
    c.drawRightString(x + CW - 5 * mm, y - 7 * mm, _safe(via_label))

    y -= header_h + 3 * mm

    # ─── RA EM DESTAQUE ───
    # Box do RA
    ra_box_w = 55 * mm
    ra_box_h = 10 * mm
    c.setFillColor(AMARELO)
    c.roundRect(x, y - ra_box_h, ra_box_w, ra_box_h, 2 * mm, fill=1, stroke=0)
    c.setFillColor(AZUL_ESCURO)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x + 3 * mm, y - 7.5 * mm, _safe(f"RA: {servico['ra']}"))

    # Data e Status
    c.setFont("Helvetica", 8)
    c.setFillColor(black)
    c.drawRightString(x + CW, y - 3 * mm, _safe(f"Data: {servico.get('data_entrada', '')}"))
    c.drawRightString(x + CW, y - 7.5 * mm, _safe(f"Status: {servico.get('status', '')}"))

    y -= ra_box_h + 4 * mm

    # ─── DADOS DO CLIENTE ───
    y = _titulo_secao(c, x, y, "DADOS DO CLIENTE")

    c.setFont("Helvetica", 7.5)
    c.setFillColor(black)
    dados_cli = [
        f"Nome: {servico.get('cliente_nome', '')}",
        f"Tel: {servico.get('cliente_telefone', '')}    Doc: {servico.get('cliente_documento', '')}",
        f"End: {servico.get('cliente_endereco', '')}",
    ]
    for info in dados_cli:
        c.drawString(x + 2 * mm, y, _safe(info))
        y -= 3.2 * mm

    y -= 1.5 * mm

    # ─── DADOS DO APARELHO ───
    y = _titulo_secao(c, x, y, "DADOS DO APARELHO")

    c.setFont("Helvetica", 7.5)
    c.setFillColor(black)
    dados_ap = [
        f"Aparelho: {servico.get('aparelho', '')}    Marca: {servico.get('marca', '')}    Modelo: {servico.get('modelo', '')}",
        f"N Serie: {servico.get('numero_serie', '')}",
        f"Defeito: {servico.get('defeito_relatado', '')}",
    ]
    for info in dados_ap:
        texto = _safe(info)
        if len(texto) > 110:
            texto = texto[:110] + "..."
        c.drawString(x + 2 * mm, y, texto)
        y -= 3.2 * mm

    y -= 1.5 * mm

    # ─── PECAS / SERVICOS ───
    if pecas:
        y = _titulo_secao(c, x, y, "PECAS / SERVICOS")

        # Header da tabela
        c.setFont("Helvetica-Bold", 7)
        c.setFillColor(AZUL)
        c.drawString(x + 2 * mm, y, "Descricao")
        c.drawRightString(x + CW - 2 * mm, y, "Valor (R$)")

        y -= 1.5 * mm
        c.setStrokeColor(AZUL)
        c.setLineWidth(0.3)
        c.setDash(1, 0)
        c.line(x, y, x + CW, y)
        y -= 3 * mm

        c.setFont("Helvetica", 7)
        c.setFillColor(black)
        for peca in pecas:
            desc = _safe(peca.get("descricao", ""))
            if len(desc) > 70:
                desc = desc[:70] + "..."
            valor = peca.get("valor_unitario", 0)
            c.drawString(x + 2 * mm, y, desc)
            c.drawRightString(x + CW - 2 * mm, y, f"{valor:.2f}")
            y -= 3 * mm

        y -= 1 * mm

    # ─── VALORES ───
    valor_total = servico.get("valor_total", 0) or 0
    desconto = servico.get("desconto", 0) or 0
    valor_final = servico.get("valor_final", 0) or 0
    forma_pgto = servico.get("forma_pagamento", "") or ""

    # Caixa de total
    box_h = 12 * mm if desconto > 0 else 8 * mm
    c.setFillColor(CINZA_CLARO)
    c.roundRect(x, y - box_h, CW, box_h, 2 * mm, fill=1, stroke=0)

    c.setFont("Helvetica", 7)
    c.setFillColor(CINZA)

    if desconto > 0:
        c.drawString(x + 3 * mm, y - 4 * mm, f"Subtotal: R$ {valor_total:.2f}")
        c.drawString(x + 55 * mm, y - 4 * mm, f"Desconto: R$ {desconto:.2f}")
        if forma_pgto:
            c.drawRightString(x + CW - 3 * mm, y - 4 * mm, _safe(f"Pagamento: {forma_pgto}"))

        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(AZUL_ESCURO)
        c.drawString(x + 3 * mm, y - 10 * mm, f"TOTAL: R$ {valor_final:.2f}")
    else:
        if forma_pgto:
            c.drawString(x + 3 * mm, y - 5.5 * mm, _safe(f"Pagamento: {forma_pgto}"))
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(AZUL_ESCURO)
        c.drawRightString(x + CW - 3 * mm, y - 5.5 * mm, f"TOTAL: R$ {valor_final:.2f}")

    y -= box_h + 3 * mm

    # ─── ASSINATURA ───
    sig_y = y_offset + M + 14 * mm
    c.setStrokeColor(black)
    c.setDash(1, 0)
    c.setLineWidth(0.3)
    c.line(x, sig_y, x + 65 * mm, sig_y)
    c.line(x + 75 * mm, sig_y, x + CW, sig_y)

    c.setFont("Helvetica", 6)
    c.setFillColor(CINZA)
    c.drawString(x, sig_y - 3 * mm, "Assinatura do Cliente")
    c.drawString(x + 75 * mm, sig_y - 3 * mm, "Assinatura da Loja")

    # ─── TERMO ───
    c.setFont("Helvetica", 4.5)
    c.setFillColor(CINZA)
    termo_y = y_offset + M + 1 * mm
    linhas = _quebrar_texto(_safe(TERMO_GARANTIA), 170)
    for lt in linhas:
        c.drawString(x, termo_y, lt)
        termo_y += 2 * mm


def _titulo_secao(c, x, y, titulo):
    """Desenha o titulo de uma secao e retorna y atualizado."""
    c.setFillColor(AZUL)
    c.roundRect(x, y - 4 * mm, CW, 4 * mm, 1 * mm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(BRANCO)
    c.drawString(x + 2 * mm, y - 3 * mm, titulo)
    return y - 7 * mm


def _quebrar_texto(texto, max_chars):
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= max_chars:
            linha_atual += (" " if linha_atual else "") + palavra
            pass
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas


def _abrir_pdf(pdf_path):
    try:
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdf_path])
        else:
            subprocess.Popen(["xdg-open", pdf_path])
    except Exception as e:
        print(f"[PDF] Nao foi possivel abrir: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        gerar_pdf_ra(sys.argv[1])
    else:
        print("Uso: python print_engine.py <RA>")
